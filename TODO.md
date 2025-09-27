# Hopecare Project TODO

## Current Progress
- [x] Initial setup: Virtual env, Django project, apps (accounts, library, inventory), dependencies.
- [x] Models: User (roles, badge, profile_picture), AuditLog, Book, StudentBookRecord, SchoolRecord, Item, Stock.
- [x] Authentication: Signup with role choice, login/logout with audit.
- [x] Dashboards: Basic role-based (student, librarian, storekeeper, admin) with data display.
- [x] Inventory: Stock in/out views/templates, alerts in dashboard.
- [x] Test data and basic testing via browser.
- [x] Git initialized.

## Remaining Steps (from approved plan)
1. [ ] Configure PostgreSQL DB and Cloudinary in settings.py (load .env, DATABASES, DEFAULT_FILE_STORAGE=CloudinaryStorage).
2. [ ] Update User model for profile_picture (CloudinaryField), create migration.
3. [ ] Add profile management: views/forms/templates for upload/view per role.
4. [ ] Library features: views/forms for add/view book/school records, badge awarding logic (based on books read count).
5. [ ] Enhance dashboards: search/filter students/books/items, low stock/expiry alerts with notifications.
6. [ ] Reports: Add views for PDF/Excel export (reportlab/openpyxl), charts (Chart.js in templates).
7. [ ] Notifications: Simple email for badge/expiry (using Django's send_mail).
8. [ ] Audit trail: Ensure all actions logged in views.
9. [ ] DRF: Install djangorestframework, add serializers/views for API endpoints (users, records, stock).
10. [ ] UI: Bootstrap progress bars for student progress, badge icons (Font Awesome).
11. [ ] Testing: Unit tests for models/views (coverage >80%).
12. [ ] Deployment: Dockerfile, docker-compose for Postgres, GitHub Actions CI, Heroku config (Procfile, runtime.txt).

## Next Steps
- Proceed with step 1: DB/Cloudinary config, then migrate and test.
- Commit after each small change.
- Update this file after completing steps.
