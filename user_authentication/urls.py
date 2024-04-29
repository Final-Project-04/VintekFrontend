
from django.urls import path
from .views import LoginView 


from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    UserProfileView,
    UserProfileUpdateView,
    EditUserView,
    DeleteUserView,
    
    
    )


app_name = 'user_authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('edit_profile/', UserProfileUpdateView.as_view(), name='edit_profile'),
    path('edit_user/', EditUserView.as_view(), name='edit_user'),
    path('delete_account/', DeleteUserView.as_view(), name='delete_account'),


    

    
    ]