

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('wallet/',  include('wallet.urls')),
    path('invoice/', include('invoice.urls')),
    path('transaction/', include('transaction.urls')),
    path('subscription/', include('subscription.urls')),
    path('inventory/', include('inventory_system.urls'))
] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
