from django.urls  import path


from . import views

urlpatterns = [
    path('create-plan/', views.CreateSubscriptionPlan.as_view(), name='plan'),
    path('cancel-plan/', views.cancel_subscription_plan, name='cancel_plan')
]