from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import Item, Stock
from .forms import StockInForm, StockOutForm
from accounts.models import User, AuditLog

User = get_user_model()

class InventoryTests(TestCase):
    def setUp(self):
        self.storekeeper = User.objects.create_user(username='teststorekeeper', password='testpass123', role='storekeeper')

    def test_item_creation(self):
        item = Item.objects.create(name='Test Item', description='Test Description')
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.description, 'Test Description')

    def test_stock_creation(self):
        item = Item.objects.create(name='Test Item')
        stock = Stock.objects.create(item=item, quantity=10, stock_in_date=timezone.now().date())
        self.assertEqual(stock.item.name, 'Test Item')
        self.assertEqual(stock.quantity, 10)

    def test_stock_in_form_valid(self):
        form_data = {
            'custom_name': 'New Item',
            'quantity': 5,
            'stock_in_date': timezone.now().date(),
            'notes': 'Test notes'
        }
        form = StockInForm(data=form_data)
        self.assertTrue(form.is_valid())
        stock = form.save()
        self.assertEqual(stock.quantity, 5)
        self.assertEqual(stock.item.name, 'New Item')
        item = Item.objects.get(name='New Item')
        self.assertTrue(item.description == '')

    def test_stock_in_form_invalid_no_name(self):
        form_data = {
            'quantity': 5,
            'stock_in_date': timezone.now().date(),
        }
        form = StockInForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('custom_name', form.errors)

    def test_stock_in_view(self):
        self.client.login(username='teststorekeeper', password='testpass123')
        response = self.client.post(reverse('stock_in'), {
            'custom_name': 'Test Stock In',
            'quantity': 10,
            'stock_in_date': timezone.now().date(),
            'notes': 'Test'
        })
        self.assertEqual(response.status_code, 302)
        stock = Stock.objects.filter(item__name='Test Stock In').first()
        self.assertIsNotNone(stock)
        self.assertEqual(stock.quantity, 10)
        audit_log = AuditLog.objects.filter(action='Stock In').first()
        self.assertIsNotNone(audit_log)
        self.assertIn('Added 10 of Test Stock In', audit_log.details)

    def test_stock_out_form_valid(self):
        item = Item.objects.create(name='Existing Item')
        stock = Stock.objects.create(item=item, quantity=20, stock_in_date=timezone.now().date())
        form_data = {
            'custom_name': 'Existing Item',
            'quantity': 5,
            'notes': 'Test out'
        }
        form = StockOutForm(data=form_data)
        self.assertTrue(form.is_valid())
        stock_out = form.save()
        self.assertEqual(stock_out.quantity, 15)  # Reduced from 20 to 15

    def test_stock_out_form_invalid_insufficient_quantity(self):
        item = Item.objects.create(name='Low Stock Item')
        stock = Stock.objects.create(item=item, quantity=3, stock_in_date=timezone.now().date())
        form_data = {
            'custom_name': 'Low Stock Item',
            'quantity': 10,
            'notes': ''
        }
        form = StockOutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_stock_out_form_invalid_nonexistent_item(self):
        form_data = {
            'custom_name': 'Non Existent Item',
            'quantity': 5,
        }
        form = StockOutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('custom_name', form.errors)

    def test_stock_out_view(self):
        item = Item.objects.create(name='Test Out Item')
        stock = Stock.objects.create(item=item, quantity=15, stock_in_date=timezone.now().date())
        self.client.login(username='teststorekeeper', password='testpass123')
        response = self.client.post(reverse('stock_out'), {
            'custom_name': 'Test Out Item',
            'quantity': 5,
            'notes': 'Test out'
        })
        self.assertEqual(response.status_code, 302)
        updated_stock = Stock.objects.get(item=item)
        self.assertEqual(updated_stock.quantity, 10)
        self.assertEqual(updated_stock.stock_out_date, timezone.now().date())
        audit_log = AuditLog.objects.filter(action='Stock Out').first()
        self.assertIsNotNone(audit_log)
        self.assertIn('Removed 5 of Test Out Item', audit_log.details)

    def test_duplicate_stock_in(self):
        # First stock in
        form_data1 = {
            'custom_name': 'Duplicate Item',
            'quantity': 10,
            'stock_in_date': timezone.now().date(),
        }
        form1 = StockInForm(data=form_data1)
        self.assertTrue(form1.is_valid())
        form1.save()
        # Second stock in same name
        form_data2 = {
            'custom_name': 'Duplicate Item',
            'quantity': 5,
            'stock_in_date': timezone.now().date(),
        }
        form2 = StockInForm(data=form_data2)
        self.assertTrue(form2.is_valid())
        form2.save()
        stock = Stock.objects.filter(item__name='Duplicate Item').first()
        self.assertEqual(stock.quantity, 15)  # Updated to 15

    def test_stock_out_no_stock_error(self):
        item = Item.objects.create(name='No Stock Item')
        # No stock created
        form_data = {
            'custom_name': 'No Stock Item',
            'quantity': 5,
        }
        form = StockOutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('custom_name', form.errors)
        self.assertIn('No available stock', str(form.errors['custom_name']))
