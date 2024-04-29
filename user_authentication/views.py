# Import necessary modules and classes
from django import forms
from.forms import CustomUserCreationForm, LoginForm
from django.views.generic.edit import FormView
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Define a view for user registration
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = '/success/'
    
    # Render the registration form
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    # Handle form submission
    def form_valid(self, form):
        # Prepare data for API request
        data = {
        'username': form.cleaned_data.get('username'), 
        'password': form.cleaned_data.get('password'),
        'password_confirm': form.cleaned_data.get('password_confirm'),
        'email': form.cleaned_data.get('email'),
        'first_name': form.cleaned_data.get('first_name'),
        'last_name': form.cleaned_data.get('last_name')
    }
        # Send a POST request to the registration API
        response = requests.post("https://vintekapi.pythonanywhere.com/register/", json=data)
        # Handle API response
        if response.status_code == 201:
            token = response.json().get('token', '')
            self.request.session['token'] = token
            return redirect('/')  # redirect to the homepage
        return JsonResponse({'error': response.json().get('error', 'Failed to create user')}, status=400)

# Define a view for user login
class LoginView(FormView):
    template_name = 'login2.html'
    form_class = LoginForm  # use the custom form class
    success_url = '/success/'

    # Render the login form
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    # Handle form submission
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        data = {'username': username, 'password': password}

        # Send a POST request to the login API
        response = requests.post("https://vintekapi.pythonanywhere.com/login/", data=data)

        # Handle API response
        if response.status_code == 200:
            token = response.json().get('token', '')
            user_id = response.json().get('user_id', '')
            username = response.json().get('username', '')
            self.request.session['token'] = token
            self.request.session['user_id'] = user_id
            self.request.session['username'] = username

            # Authenticate the user
            user = authenticate(self.request, username=username, password=password)

            # Check if the user was authenticated successfully
            if user is not None:
                # Log the user in
                login(self.request, user)

            return redirect('/')
        else:
            form.add_error(None, 'Invalid username or password')
            return self.form_invalid(form)

# Define a view for user logout
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if 'token' in request.session:
            # Send a POST request to the logout API
            response = requests.post('https://vintekapi.pythonanywhere.com/logout/', headers={'Authorization': f'Token {request.session["token"]}'})
            
            # Handle API response
            if response.status_code == 200:
                # Delete all user-related session data
                for key in ['token', 'user_id', 'username']:
                    if key in request.session:
                        del request.session[key]
                return redirect('user_authentication:login')  # Redirect to the login page
            else:
                return JsonResponse({'error': 'An error occurred while trying to log out'}, status=400)
        else:
            return JsonResponse({'error': 'No token in session'}, status=400)

# Define a view for user profile
class UserProfileView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            # Send a GET request to the user API
            response = requests.get(f'https://vintekapi.pythonanywhere.com/api/users/{user_id}/', headers={'Authorization': f'Token {token}'})
            # Handle API response
            if response.status_code == 200:
                user_data = response.json()
                return render(request, 'user_profile.html', {'user': user_data, 'profile_picture_url': user_data.get('profile_picture')})
            else:
                return JsonResponse({'error': 'An error occurred while trying to get user data'}, status=400)
        return JsonResponse({'error': 'No user ID in session'}, status=400)  # Default response

# Define a view for updating user profile
@method_decorator(csrf_exempt, name='dispatch')
class UserProfileUpdateView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            # Send a GET request to the user API
            response = requests.get(f'https://vintekapi.pythonanywhere.com/api/users/{user_id}/', headers={'Authorization': f'Token {token}'})
            # Handle API response
            if response.status_code == 200:
                return render(request, 'edit_profile.html', {'user': response.json()})
            else:
                return JsonResponse({'error': 'An error occurred while trying to get user data'}, status=400)
        return JsonResponse({'error': 'No user ID in session'}, status=400)

    # Handle form submission
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            # Prepare data for API request
            data = MultipartEncoder(
                fields={
                    'country': request.POST.get('country'),
                    'city': request.POST.get('city'),
                    'adress': request.POST.get('adress'),
                    'phone_number': request.POST.get('phone_number'),
                    'profile_picture': (request.FILES.get('profile_picture').name, request.FILES.get('profile_picture'), request.FILES.get('profile_picture').content_type) if request.FILES.get('profile_picture') else None,
                }
            )
            # Send a PUT request to the user API
            response = requests.put(f'https://vintekapi.pythonanywhere.com/api/users/{user_id}/', data=data, headers={'Authorization': f'Token {token}', 'Content-Type': data.content_type})
            # Handle API response
            if response.status_code == 200:
                return redirect('user_authentication:profile')
            else:
                return JsonResponse({'error': 'An error occurred while trying to update user profile'}, status=400)
        return JsonResponse({'error': 'No user ID in session'}, status=400)

# Define a view for editing user data
class EditUserView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            # Send a GET request to the user API
            response = requests.get(f'https://vintekapi.pythonanywhere.com/user/{user_id}/', headers={'Authorization': f'Token {token}'})
            # Handle API response
            if response.status_code == 200:
                return render(request, 'edit_user.html', {'user': response.json()})
            else:
                return JsonResponse({'error': 'An error occurred while trying to get user data'}, status=400)
        return JsonResponse({'error': 'No user ID in session'}, status=400)
    
    # Handle form submission
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            # Prepare data for API request
            data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'password': request.POST.get('new_password'),
            }
            
            # Send a PUT request to the user API
            response = requests.put(f'https://vintekapi.pythonanywhere.com/user/{user_id}/', data=data, headers={'Authorization': f'Token {token}'})
            # Handle API response
            if response.status_code == 200:
                return redirect('user_authentication:profile')
            else:
                return JsonResponse({'error': 'An error occurred while trying to update user data'}, status=400)
            
            
class DeleteUserView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if user_id:
            token = request.session.get('token')
            response = requests.delete(f'https://vintekapi.pythonanywhere.com/user/{user_id}/', headers={'Authorization': f'Token {token}'})
            if response.status_code == 204:
                for key in ['token', 'user_id', 'username']:
                    if key in request.session:
                        del request.session[key]
                return redirect('user_authentication:login')
        return JsonResponse({'error': 'An error occurred while trying to delete user account'}, status=400)