from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Item, Loan
from .forms import CheckoutForm, ReturnForm, LoanFormSet


@login_required
def locker(request):
    if not (
       # organizer 
       request.user.is_staff
    ):
        messages.error(request, "You do not have permission to view the locker.")
        return redirect("#")
    
    return render(request, 'locker.html')

@login_required
def item_list(request):
    if not (
       # organizer 
       request.user.is_staff
    ):
        messages.error(request, "You do not have permission to view the locker.")
        return redirect("#")
    
    items = Item.objects.filter(
        available_quantity__gt=0
    )
    loaned_items = Loan.objects.filter(
        active=True
    )

    return render(request, 'item_list.html', {'items': items, 'loaned_items': loaned_items})


@login_required
def checkout_items(request):
    if not (
       # organizer 
       request.user.is_staff
    ):
        messages.error(request, "You do not have permission to view the locker.")
        return redirect("#")

    items = Item.objects.filter(
        available_quantity__gt=0
    )
    if request.method == "POST":
        checkout_form = CheckoutForm(request.POST) 
        formset = LoanFormSet(request.POST)
        if formset.is_valid() and checkout_form.is_valid():
            expected_return = checkout_form.cleaned_data['expected_return']
            checkout_note = checkout_form.cleaned_data['note']
            for form in formset.cleaned_data:
                item = Item.objects.get(id=form["item_id"])
                if form["quantity"] and form["quantity"] > 0 and form["quantity"] <= item.available_quantity:
                    Loan.objects.create(
                        item=item,
                        user=request.user,
                        quantity=form["quantity"],
                        expected_return=expected_return,
                        checkout_note=checkout_note
                    )

                    item.available_quantity -= form["quantity"]
                    item.save()
            messages.success(request, f'Successfully borrowed {len(formset)} item(s)!')
            return redirect('item_list')
        else:
            messages.error(request, f'Invalid form {formset.is_valid()}, {formset}')
            return redirect('item_list')
    else:
        initial_data = [
            {"item_id": item.id, "name": item.name, "type": item.type.name, "available_quantity": item.available_quantity}
            for item in items
        ]
        formset = LoanFormSet(initial=initial_data)
        initial_due_date = timezone.now() + timedelta(days=7)
        checkout_form = CheckoutForm(initial={'expected_return': initial_due_date})
    
    return render(request, 'checkout.html', {"formset": formset, "checkout_form": checkout_form})

@login_required
def return_items(request):
    if not (
       # organizer 
       request.user.is_staff
    ):
        messages.error(request, "You do not have permission to view the locker.")
        return redirect("#")
    
    active_loans = Loan.objects.filter(
        user=request.user,
        active=True,
    )
    
    if request.method == 'POST':
        form = ReturnForm(request.POST, user_loans=active_loans)
        if form.is_valid():
            selected_loans = form.cleaned_data['loans']
            return_note = form.cleaned_data['return_note']

            
            if not selected_loans:
                messages.error(request, 'Please select at least one item to return.')
                return redirect('return_items')

            for loan in selected_loans:
                loan.active = False
                loan.returned_at = timezone.now()
                loan.return_note = return_note
                loan.save()

                item = loan.item
                item.available_quantity += loan.quantity
                item.save()
            
            messages.success(request, f'Successfully returned {len(selected_loans)} item(s)!')
            return redirect('item_list')
    else:
        form = ReturnForm(user_loans=active_loans)
    
    return render(request, 'return.html', {
        'form': form,
        'active_loans': active_loans,
    })


@login_required
def my_loans(request):
    if not (
       # organizer 
       request.user.is_staff
    ):
        messages.error(request, "You do not have permission to view the locker.")
        return redirect("#")

    loans = Loan.objects.filter(
        user=request.user,
        active=True,
    )
    return render(request, 'my_loans.html', {'loans': loans})
