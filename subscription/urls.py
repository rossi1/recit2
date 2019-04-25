from django.urls  import path


from . import views

urlpatterns = [
    path('create-plan/', views.CreateSubscriptionPlan.as_view(), name='plan')
]