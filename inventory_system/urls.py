from django.urls import path, include


from . import views

invoice_urls = [
    path('create-invoice/', views.InvoiceProductCreateView.as_view(), name='create'),
    path('view-invoice/', views.InvoiceProductListView.as_view(), name='invoice_inv')
]


urlpatterns =  [
    path('create-product/', views.ProductCreationView.as_view(), name='product_create_view'),
    path('edit-product/<int:pk>/', views.ProductEditView.as_view(), name='product_edit_view'),
    path('delete-product/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete_view'),
    path('view-products/', views.ProductListingView.as_view(), name='product_list_view'),
    path('update-quantity/<int:product_id>/', views.update_product_quantity_view_to_not_available, name='update_product'),
    path('', include(invoice_urls)),
    path('view-product-data/<str:product_id>/', views.view_product_for_payment, name='view_product_data'),
    path('search-product/', views.SearchProductView.as_view(), name='search_product')
]