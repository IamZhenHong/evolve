from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import UserRegistrationForm  # Custom registration form if needed
from .models import CustomUser  # Custom user model if needed
from django.contrib.auth.decorators import login_required


app_name = 'users'

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Replace with desired redirect URL
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('pages:home')  # Replace with desired redirect URL
    else:
        form = AuthenticationForm()
    return render(request, 'users/registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # Replace with desired redirect URL

@login_required(login_url='/login/')
def user_profile(request):
    if not request.session.exists(request.session.session_key):
        return redirect('login')
    # Access user profile information
    user = request.user
    # ... logic to retrieve user profile data
    return render(request, 'users/profile.html', {'user': user})