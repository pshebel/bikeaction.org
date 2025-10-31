from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_loans, name='my_loans'),
    path('items/', views.item_list, name='item_list'),
    path('checkout/', views.checkout_items, name='checkout'),
    path('return/', views.return_items, name='return_items'),
]