from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('storekeeper/', views.storekeeper_dashboard, name='storekeeper_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('award-badge/<int:student_id>/', views.award_badge, name='award_badge'),
    path('preview-student/<int:student_id>/', views.preview_student, name='preview_student'),
]
