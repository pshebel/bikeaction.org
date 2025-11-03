from django.contrib import admin

from .models import Item, ItemType, Loan


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    list_filter = ["created_at"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "note",
        "total_quantity",
        "available_quantity",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name"]
    list_filter = ["created_at"]


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
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
