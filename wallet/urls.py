from django.urls import path

from . import views

urlpatterns = [
    path('gain-access/', views.gain_secure_token, name='gain_access'),
    path('upload-bank-detail/', views.AddBankDetails.as_view(), name='add_bank'),
    path('update-bank-detail/<int:pk>/', views.UpdateBank.as_view(), name='update-bank'),
    
]