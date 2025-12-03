from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone

from pbaabp.admin import organizer_admin, OrganizerAccess
from .models import Item, ItemType, Loan

class ItemTypeAdmin(OrganizerAccess, admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    list_filter = ["created_at"]

# class LoanInline(admin.TabularInline):
#     model = Loan
#     extra = 1
#     fields = ["user", "quantity", "active", "expected_return", "borrowed_at", "returned_at", "checkout_note", "return_note"]
#     readonly_fields = ["borrowed_at", "created_at", "updated_at"]

class ItemAdmin(OrganizerAccess, admin.ModelAdmin):
    list_display = [
        "name",
        "note",
        "total_quantity",
        "available_quantity",
        "loan_quantity_input",
        "create_loan_button",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name"]
    list_filter = ["created_at"]

    # inlines = [LoanInline]

    def has_change_permission(self, request, obj=None):
        return True
        
    def loan_quantity_input(self, obj):
        return format_html(
            '<input type="number" min="1" max="{}" value="1" '
            'id="loan_quantity_{}" style="width: 60px;" />',
            obj.available_quantity,
            obj.id
        )
    loan_quantity_input.short_description = "Loan Qty"
    
    def create_loan_button(self, obj):
        return format_html(
            '<button type="button" onclick="createLoan({})" '
            'style="padding: 5px 10px; cursor: pointer;">Create Loan</button>',
            obj.id
        )
    create_loan_button.short_description = "Action"

    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and 'create_loan' in request.POST:
            item_id = request.POST.get('item_id')
            quantity = request.POST.get('quantity', 1)
            
            try:
                from django.contrib.auth.models import User
                item = Item.objects.get(id=item_id)
                quantity = int(quantity)
                
                if quantity > item.available_quantity:
                    messages.error(request, f"Cannot loan {quantity} items. Only {item.available_quantity} available.")
                else:
                    # Create loan for the current admin user (or modify as needed)
                    loan = Loan.objects.create(
                        item=item,
                        user=request.user,  # or select user in a modal
                        quantity=quantity,
                        active=True,
                        borrowed_at=timezone.now()
                    )
                    item.available_quantity -= quantity
                    item.save()

                    messages.success(request, f"Loan created successfully for {quantity} x {item.name}")
                    
            except (Item.DoesNotExist, ValueError) as e:
                messages.error(request, f"Error creating loan: {str(e)}")
        
        return super().changelist_view(request, extra_context)
    # actions = ["checkout"]


class LoanAdmin(OrganizerAccess, admin.ModelAdmin):
    list_display = [
        "user",
        "item",
        "quantity",
        "active",
        "expected_return",
        "borrowed_at",
        "returned_at",
        "return_note",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["user__username", "item__name"]
    date_hierarchy = "borrowed_at"

    actions = ["return_items"]

    def return_items(self, request, queryset):
        from django.utils import timezone
        queryset.update(active=False, returned_at=timezone.now())
        self.message_user(request, f"{queryset.count()} loans marked as returned.")
    return_items.short_description = "Mark selected loans as returned"

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return False
        return obj.user == request.user
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False
        return obj.user == request.user

admin.site.register(Loan, LoanAdmin)
admin.site.register(ItemType, ItemTypeAdmin)
admin.site.register(Item, ItemAdmin)
organizer_admin.register(Loan, LoanAdmin)
organizer_admin.register(ItemType, ItemTypeAdmin)
organizer_admin.register(Item, ItemAdmin)