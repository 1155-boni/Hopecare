# TODO: Rename Librarian Role to Welfare and Update Dashboard

## Completed Tasks
- [x] Analyze codebase and create plan
- [x] Update accounts/models.py: Change 'librarian' to 'welfare' in ROLE_CHOICES, add Beneficiary model
- [x] Create and run Django migration for model changes
- [x] Update accounts/forms.py: Add BeneficiaryForm
- [x] Update accounts/views.py: Change 'librarian' to 'welfare', modify welfare_dashboard
- [x] Update accounts/templates/accounts/welfare_dashboard.html: Change title, clear content, add form
- [x] Update templates/home.html: Change role check
- [x] Update create_superusers.py: Change role
- [x] Update library/views.py: Change 'librarian' references (none found)
- [x] Update library/api.py: Change 'librarian' references (none found)
- [x] Update accounts/tests.py: Change 'librarian' references (none found)
- [x] Update library/tests.py: Change 'librarian' references (none found)
- [x] Update accounts/templates/accounts/admin_dashboard.html: Remove librarian tab and content
- [x] Update accounts/templates/accounts/preview_student.html: Change 'librarian_dashboard' to 'welfare_dashboard'
- [x] Update library/templates/library/add_book.html: Change 'librarian_dashboard' to 'welfare_dashboard'
- [x] Remove student dashboard completely: Delete template, update redirects in views and templates

## Pending Tasks
- [x] Test the changes - Django server running successfully at http://127.0.0.1:8000/
