from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import User
from .forms import CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .email_service import MailtrapEmailService


def login_selection(request):
    """Main login selection page - Only accessible to staff, attendant, and owner"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    # Restrict access - patients should not be able to access this page
    # This page is only for staff (admin), attendant, and owner
    # Patients should use the direct patient login URL
    return render(request, 'accounts/login_selection.html')


def patient_login(request):
    """Patient login view"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.user_type == 'patient':
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid credentials for patient login.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'accounts/patient_login.html')


def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.user_type == 'admin':
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('/admin/')
            else:
                messages.error(request, 'Invalid credentials for admin login.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'accounts/admin_login.html')


def owner_login(request):
    """Owner login view"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.user_type == 'owner':
                login(request, user)
                messages.success(request, 'Welcome Back Ma\'am Kranchy')
                return redirect('owner:dashboard')
            else:
                messages.error(request, 'Invalid credentials for owner login.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'accounts/owner_login.html')


def attendant_login(request):
    """Attendant login view"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.user_type == 'attendant':
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('attendant:dashboard')
            else:
                messages.error(request, 'Invalid credentials for attendant login.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'accounts/attendant_login.html')


def redirect_to_dashboard(user):
    """Helper function to redirect users to their appropriate dashboard"""
    if user.user_type == 'admin':
        return redirect('/admin/')
    elif user.user_type == 'owner':
        return redirect('owner:dashboard')
    elif user.user_type == 'attendant':
        return redirect('attendant:dashboard')
    else:
        return redirect('accounts:profile')


def login_view(request):
    """Legacy login view - redirects to selection page"""
    return redirect('accounts:login_selection')


def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login the user after registration
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            # Redirect patients to their profile page
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    """Edit user profile - available for patient and attendant"""
    if request.user.user_type not in ['patient', 'attendant']:
        messages.error(request, 'You do not have permission to edit your profile.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        from .forms import ProfileEditForm
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import ProfileEditForm
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


def test_mailtrap(request):
    """Test view to verify Mailtrap integration"""
    if request.method == 'POST':
        email = request.POST.get('email', 'ksreyes.chmsu@gmail.com')
        name = request.POST.get('name', 'Test User')
        
        email_service = MailtrapEmailService()
        result = email_service.send_test_email(email, name)
        
        if result['success']:
            messages.success(request, f"Test email sent successfully to {email}!")
        else:
            messages.error(request, f"Failed to send test email: {result['message']}")
    
    return render(request, 'accounts/test_mailtrap.html')


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view for patients"""
    template_name = 'accounts/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'patient'
        return context
    
    def form_valid(self, form):
        """Override to only send reset emails to patients using Django's email system"""
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email, user_type='patient')
            if user.is_active:
                # Generate token and create reset URL
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset URL
                reset_url = self.request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={
                        'uidb64': uid,
                        'token': token
                    })
                )
                
                # Send email using Django's email system
                subject = 'Password Reset - Skinovation Beauty Clinic'
                message = render_to_string('accounts/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': 'Skinovation Beauty Clinic',
                })
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                        html_message=message,  # Send as HTML email
                    )
                    messages.success(self.request, 'Password reset email sent! Please check your inbox.')
                except Exception as e:
                    messages.error(self.request, f"Failed to send email: {str(e)}")
            else:
                messages.error(self.request, 'This account is inactive.')
        except User.DoesNotExist:
            messages.error(self.request, 'No patient account found with this email address.')
        
        return redirect(self.success_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'patient'
        return context


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Custom password reset done view"""
    template_name = 'accounts/password_reset_done.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'patient'
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Custom password reset complete view"""
    template_name = 'accounts/password_reset_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'patient'
        return context