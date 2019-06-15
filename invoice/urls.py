from django.urls import path


from . import views


urlpatterns = [

    path('create-invoice/', views.CreateInvoice.as_view(), name='create_invoice'),
    path('view-pending-invoice/', views.ViewPendingInvoice.as_view(), name='view-pending_invoice'),
    path('view-approved-invoice/', views.ViewPaidInvoice.as_view(),  name='view-approved_invoice'),
    path('view-invoice/<str:invoice_id>/', views.invoice_detail_view, name='detailed_invoice'),
    path('create-client/', views.CreateClient.as_view(), name='create_client'),
    path('retrieve-client<int:user_pk>/', views.retrieve_client_info, name='retrieve_client'),
    path('update-client/<int:pk>/', views.UpdateClientInfo.as_view(), name='update_client'),
    #path('view-data/<str:encoded_data>/', views.view_data, name='view_data'),
    path('view-clients/', views.ViewAllClient.as_view(), name='view_client'),
    path('delete-client/<int:pk>/', views.DeleteClientView.as_view(), name='delete_client'),
    path('delete-invoice/<int:pk>/', views.DeleteInvoiceView.as_view(), name='delete_invoice'),
    path('create-reminder/', views.CreateAutomatedReminder.as_view(), name='create_reminder'),
    path('cancel-reminder/<str:invoice_id>/', views.cancel_reminder, name='cancel_remider'),
    path('approve-invoice/str:invoice_id>/', views.approve_invoice, name='approve'),
    path('view-data/<str:invoice_id>/', views.view_invoice_for_payment, name='view_data'),
    path('perform_invoice_transaction/', views.PerformTransaction.as_view(), name='invoice_transaction'),
    path('charge_back/', views.ChargeBackView.as_view(), name='charge_back_view')
]
