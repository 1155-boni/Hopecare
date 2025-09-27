# Hopecare Project TODO

## Current Task: Add Delete Account Functionality to User Profiles and Update Navbar

### Steps to Complete:
1. [x] Add delete_profile view to accounts/views.py: Handle POST request to delete user account, log action in AuditLog, logout user, redirect to home with success message.
2. [x] Add URL pattern for delete_profile in accounts/urls.py: path('profile/delete/', views.delete_profile, name='delete_profile').
3. [x] Update accounts/templates/accounts/profile.html: Add a separate form below the update form for account deletion, using POST to 'delete_profile', include CSRF token, style as red danger button, add JavaScript confirmation dialog before submission.
4. [x] Update templates/base.html: Replace logout link with profile link in navbar for authenticated users.
5. [x] Update accounts/templates/accounts/profile.html: Add logout button to the profile page.
6. [x] Test the implementation: Login as a test user, verify navbar shows profile link, navigate to profile, edit profile to confirm existing functionality, test logout button, then delete account and verify logout, success message, and no errors.
7. [x] Commit changes: "Add delete account functionality to user profiles and update navbar with profile link, move logout to profile page".

### Follow-up After Completion:
- Verify no cascade deletion issues for related records (e.g., book records, stocks).
- Ensure profile editing remains fully functional.
- Manual testing via browser; no new unit tests for this feature.
