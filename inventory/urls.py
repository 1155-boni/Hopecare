from django.urls import path
from . import views

urlpatterns = [
    path('stock-in/', views.stock_in, name='stock_in'),
    path('stock-out/', views.stock_out, name='stock_out'),
    path('inventory-list/', views.inventory_list, name='inventory_list'),
]
