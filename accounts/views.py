from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomUserCreationForm

# Create your views here.
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account for {username} created! Please wait for a manager to approve it.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    """
    A simple view that logs the user out using a GET request.
    """
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('landing_page')