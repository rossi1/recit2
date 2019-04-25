from django.urls import path

from . import views


urlpatterns = [
    path('c/history', views.ViewClientHistory.as_view(), name='client_history'),
    path('u/history', views.ViewUserHistory.as_view(), name='user_history')
 
]