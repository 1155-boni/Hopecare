# TODO: Add Stock Out Quantity Column to Inventory List

## Current Work
Implementing a new 'out_quantity' field to track cumulative removed quantity for each stock item, updating forms, template, and tests as per approved plan.

## Key Technical Concepts
- Django models: Adding IntegerField to Stock model.
- Forms: Custom save() in StockOutForm to increment out_quantity.
- Templates: Adding table column in inventory_list.html.
- Testing: Unit tests for new field behavior.
- Migrations: Database schema update for new field.
- No changes to serializers (uses '__all__') or views (context already includes stocks).

## Relevant Files and Code
- inventory/models.py: Add `out_quantity = models.IntegerField(default=0, blank=True)` to Stock class.
- inventory/forms.py: In StockOutForm.save(), after `stock.quantity -= quantity_out`, add `stock.out_quantity += quantity_out`.
- inventory/templates/inventory/inventory_list.html: In Stocks table <thead>, add <th>Stock Out Quantity</th> after <th>Stock Out Date</th>; in <tbody> rows, add <td>{{ stock.out_quantity|default:"0" }}</td> after stock_out_date <td>.
- inventory/tests.py: Update test_stock_out_form_valid: assert stock_out.out_quantity == 5; update test_stock_out_view: assert updated_stock.out_quantity == 5; add new test_multiple_stock_outs: Create stock, out 5 (assert 5), out 3 (assert 8 total).

## Problem Solving
- Ensures cumulative tracking without separate history table (simple accumulation per stock instance).
- Handles multiple outs for same item by incrementing on each stock_out.
- Defaults to 0 for existing records via migration.

## Pending Tasks and Next Steps
- [x] Edit inventory/models.py to add out_quantity field.
- [x] Execute `python manage.py makemigrations inventory` and `python manage.py migrate` to apply DB changes.
- [x] Edit inventory/forms.py to update StockOutForm.save() for out_quantity increment.
- [x] Edit inventory/templates/inventory/inventory_list.html to add the new column.
- [x] Edit inventory/tests.py to update existing tests and add new test for multiple stock outs.
- [x] Run `python manage.py test inventory` to verify all tests pass (expect 12 tests now).
- [ ] Verify UI: Use browser to login as storekeeper, stock in item, stock out multiple times, check inventory list shows accumulating out_quantity.
- [ ] Test API: Curl POST/PATCH to /api/stocks/ to confirm out_quantity updates.
- [x] Update this TODO.md with [x] as steps complete.
