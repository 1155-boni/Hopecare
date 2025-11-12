from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('welfare/', views.welfare_dashboard, name='welfare_dashboard'),
    path('beneficiary/<int:beneficiary_id>/', views.preview_beneficiary, name='preview_beneficiary'),
    path('beneficiary/<int:beneficiary_id>/medical-records/', views.medical_records_list, name='medical_records_list'),
    path('beneficiary/<int:beneficiary_id>/medical-records/add/', views.add_medical_record, name='add_medical_record'),
    path('beneficiary/<int:beneficiary_id>/medical-records/<int:record_id>/edit/', views.edit_medical_record, name='edit_medical_record'),
    path('beneficiary/<int:beneficiary_id>/medical-records/<int:record_id>/delete/', views.delete_medical_record, name='delete_medical_record'),
    path('storekeeper/', views.storekeeper_dashboard, name='storekeeper_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
