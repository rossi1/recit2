from django.urls  import path


from . import views

urlpatterns = [
    path('create-plan/', views.CreateSubscriptionPlan.as_view(), name='plan'),
    #path('cancel-plan/', views.cancel_plan, name='cancel_plan'),
    #path('downgrade-plan', views.downgrade_plan, name='downgrade_plan'),
    #path('upgrade-plan', views.upgrade_plan, name='upgrade_plan')
]