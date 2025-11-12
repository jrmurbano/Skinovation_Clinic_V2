from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


def home(request):
    """Home page view"""
    # Redirect admin users to admin dashboard
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return redirect('appointments:admin_dashboard')
    
    return render(request, 'home.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
