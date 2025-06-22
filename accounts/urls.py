from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Our custom registration URL
    path('register/', views.register, name='register'),

    # Our custom login view that uses our form
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),

    # Use the rest of Django's built-in auth views (logout, password reset, etc.)
    # This automatically gives us the POST-only logout view.
    path('logout/', views.logout_view, name='logout'),
]