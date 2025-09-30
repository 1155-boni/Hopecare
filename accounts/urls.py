from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('storekeeper/', views.storekeeper_dashboard, name='storekeeper_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('award-badge/<int:student_id>/', views.award_badge, name='award_badge'),
    path('preview-student/<int:student_id>/', views.preview_student, name='preview_student'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
