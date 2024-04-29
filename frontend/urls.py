from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_ui.urls')),
    path('user_authentication/', include('user_authentication.urls')),
    path('shoppingcart/', include('shoppingcart.urls')),
    path('order_and_payment/', include('order_and_payment.urls')),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
