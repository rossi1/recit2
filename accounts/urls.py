from django.urls import path

from  . import views


urlpatterns = [
    path('sign-up/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.reset_password_view, name='forgot-password'),
    path('verify-code/', views.reset_code_verification, name='verify_token'),
    path('password-reset/', views.reset_password, name='pasword-reset'),
    path('create-business-account/', views.create_business_account, name='create-business'),
    path('update-business-account/<int:pk>/', views.UpdateBusinessAccount.as_view(), name='update-account'),
    path('verify-business-name/', views.validate_business_name, name='validate_business_name')
]