from django.urls import path
from .views import ShoppingCartView, AddProductView, RemoveProductView, DeleteProductView, UpdateQuantityView

app_name = 'shoppingcart'


urlpatterns = [
    path('cart/', ShoppingCartView.as_view(), name='cart'),
    path('add-product/<int:product_id>/', AddProductView.as_view(), name='add_product'),
    path('remove-product/<int:cart_item_id>/', RemoveProductView.as_view(), name='remove_product'),
    path('delete-product/<int:cart_item_id>/', DeleteProductView.as_view(), name='delete_product'),
    path('update-quantity/<int:pk>/', UpdateQuantityView.as_view(), name='update_quantity'),
]