from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import CustomUser

def manager_required(function):
    """
    Decorator for views that are only accessible to managers (staff users).
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "You do not have permission to view this page.")
            return redirect('login')
    return wrap


def customer_and_approved_required(function):
    """
    Decorator for views that are only accessible to customers who have been approved.
    This is the definitive, robust version.
    """
    def wrap(request, *args, **kwargs):
        # 1. Check if user is logged in at all.
        if not request.user.is_authenticated:
            return redirect('login')

        # 2. Directly fetch the user from the DB to get the LATEST status.
        try:
            current_user = CustomUser.objects.get(pk=request.user.pk)
        except CustomUser.DoesNotExist:
            return redirect('login') # Failsafe if user was deleted mid-session

        # 3. Check the user's status based on the FRESH data from the DB.
        if not current_user.is_staff and current_user.is_approved:
            # SUCCESS: This is an approved customer. Let them access the view.
            return function(request, *args, **kwargs)
        
        else:
            # FAILURE: If they are not an approved customer for any reason,
            # redirect them to the main dashboard, which will handle routing.
            messages.error(request, "This area is for approved customers only.")
            return redirect('dashboard')
            
    return wrap