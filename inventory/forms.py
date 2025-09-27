from django import forms
from django.utils import timezone
from .models import Item, Stock
from accounts.models import AuditLog

class StockInForm(forms.ModelForm):
    custom_name = forms.CharField(max_length=200, required=True, label='Item Name')
    quantity = forms.IntegerField(min_value=1, label='Quantity')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Notes')

    class Meta:
        model = Stock
        fields = ['custom_name', 'quantity', 'notes', 'stock_in_date']
        widgets = {
            'stock_in_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True, user=None):
        if not hasattr(self, 'cleaned_data'):
            self.full_clean()
        cleaned_data = self.cleaned_data
        custom_name = cleaned_data['custom_name']
        item, created = Item.objects.get_or_create(name=custom_name, defaults={
            'description': '',
            'category': 'General',
        })
        instance = super().save(commit=False)
        instance.item = item
        instance.custom_name = custom_name
        instance.stock_in_date = cleaned_data.get('stock_in_date', timezone.now().date())
        if commit:
            # Update or create stock
            stock, _ = Stock.objects.get_or_create(item=item, defaults={
                'quantity': 0,
                'stock_in_date': instance.stock_in_date,
                'notes': cleaned_data.get('notes', ''),
            })
            stock.quantity += cleaned_data['quantity']
            stock.save()
            if user:
                AuditLog.objects.create(user=user, action='Stock In', details=f'Added {cleaned_data["quantity"]} of {item.name}')
            return stock
        return instance

class StockOutForm(forms.ModelForm):
    custom_name = forms.CharField(max_length=200, required=True, label='Item Name')
    quantity = forms.IntegerField(min_value=1, label='Quantity to Remove')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Notes')

    class Meta:
        model = Stock
        fields = ['custom_name', 'quantity', 'notes']
        widgets = {}

    def clean(self):
        cleaned_data = super().clean()
        custom_name = cleaned_data.get('custom_name')
        quantity_out = cleaned_data.get('quantity')
        if custom_name:
            item = Item.objects.filter(name=custom_name).first()
            if not item:
                self.add_error('custom_name', 'No item found with that name. Stock in first.')
            else:
                stock = Stock.objects.filter(item=item, quantity__gt=0).first()
                if not stock:
                    self.add_error('custom_name', 'No available stock for this item.')
                elif quantity_out and quantity_out > stock.quantity:
                    self.add_error('quantity', 'Quantity to remove exceeds available stock.')
        return cleaned_data

    def save(self, commit=True, user=None):
        if not hasattr(self, 'cleaned_data'):
            self.full_clean()
        cleaned_data = self.cleaned_data
        custom_name = cleaned_data['custom_name']
        quantity_out = cleaned_data['quantity']
        item = Item.objects.get(name=custom_name)
        stock = Stock.objects.filter(item=item, quantity__gt=0).first()
        stock.quantity -= quantity_out
        stock.stock_out_date = timezone.now().date()
        stock.notes = cleaned_data.get('notes', '')
        stock.custom_name = custom_name
        if commit:
            stock.save()
            if user:
                AuditLog.objects.create(user=user, action='Stock Out', details=f'Removed {quantity_out} of {item.name}')
        return stock
