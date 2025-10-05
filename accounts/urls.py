from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('welfare/', views.welfare_dashboard, name='welfare_dashboard'),
    path('storekeeper/', views.storekeeper_dashboard, name='storekeeper_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('award-badge/<int:student_id>/', views.award_badge, name='award_badge'),
    path('preview-student/<int:student_id>/', views.preview_student, name='preview_student'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
