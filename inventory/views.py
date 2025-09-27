from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item, Stock
from .forms import StockInForm, StockOutForm
from django.utils import timezone
from accounts.models import AuditLog

@login_required
def stock_in(request):
    if request.user.role != 'storekeeper':
        return redirect('home')
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=True, user=request.user)
            return redirect('storekeeper_dashboard')
    else:
        form = StockInForm()
    items = Item.objects.all()
    return render(request, 'inventory/stock_in.html', {'form': form, 'items': items})

@login_required
def stock_out(request):
    if request.user.role != 'storekeeper':
        return redirect('home')
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=True, user=request.user)
            return redirect('storekeeper_dashboard')
    else:
        form = StockOutForm()
    stocks = Stock.objects.filter(quantity__gt=0)
    return render(request, 'inventory/stock_out.html', {'form': form, 'stocks': stocks})

@login_required
def inventory_list(request):
    if request.user.role != 'storekeeper':
        return redirect('home')
    items = Item.objects.all()
    stocks = Stock.objects.all()
    context = {
        'items': items,
        'stocks': stocks,
    }
    return render(request, 'inventory/inventory_list.html', context)
