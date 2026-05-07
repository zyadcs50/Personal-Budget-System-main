from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_view.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', auth_view.LogoutView.as_view(http_method_names=['get', 'post']), name='logout'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('setup-budget/', views.setup_budget, name='setup_budget'),
    path('expenses/', views.expenses, name='expenses'),
    path('delete-budget/', views.delete_budget, name='delete_budget'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('home/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),

]
