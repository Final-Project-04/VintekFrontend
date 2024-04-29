from django.contrib import admin
from django.urls import path

from .views import (
    Home,
    Categories,
    ProductListView,
    ProductListByCategoryView,
    SearchView,
    ProductDetailView,
    ProductEditView,
    ProductCreateView,
    ProductDeleteView,
    WishlistView,
    MessageFormView,
    UserMessagesView,
    ReplyCreateView,
    DeleteConversationView,
    
    
)

urlpatterns = [
    path('', Home.as_view(), name='home'),
    
    path('categories/', Categories.as_view(), name='categories'),
    
    path('products/', ProductListView.as_view(), name='products'),
    
    path('product_create/', ProductCreateView.as_view(), name='product_create'),
    
    path('products/<int:product_id>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    path('products/category/<int:category_id>/', ProductListByCategoryView.as_view(), name='product_list_by_category'),
    
    path('products/<int:product_id>/edit/',ProductEditView.as_view(), name='product-edit'),
    
    path('product_search/', SearchView.as_view(), name='product_search'),
    
    path('products/<int:product_id>/',ProductDetailView.as_view(), name='product_detail'),
    
    path('products/category/<int:category_id>/',ProductListByCategoryView.as_view(), name='product_list_by_category'),

    #Wishlist
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    
    #message
    path('message_form/<int:product_id>/<int:user_id>/', MessageFormView.as_view(), name='message_form'),
    
    path('user_messages/', UserMessagesView.as_view(), name='user_messages'),
    
    path('reply_create/', ReplyCreateView.as_view(), name='reply_create'),
    
    path('delete_conversation/<int:product_id>/', DeleteConversationView.as_view(), name='delete_conversation'),


]
