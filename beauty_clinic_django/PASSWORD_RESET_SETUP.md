# Password Reset Setup Guide

This guide will help you set up Gmail-based password reset functionality for the Skinovation Beauty Clinic Django application.

## Features Implemented

✅ **Forgot Password Link** - Added to patient login page  
✅ **Email-based Reset** - Gmail SMTP integration  
✅ **Secure Token System** - Time-limited reset links (1 hour)  
✅ **Beautiful UI** - Consistent with clinic's design theme  
✅ **Patient-only Reset** - Only patients can reset passwords  
✅ **Comprehensive Templates** - All password reset pages styled  

## Gmail Configuration

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Factor Authentication if not already enabled

### Step 2: Generate App Password
1. In Google Account settings, go to Security
2. Under "2-Step Verification", click "App passwords"
3. Select "Mail" as the app
4. Select "Other" as the device and enter "Django Beauty Clinic"
5. Copy the generated 16-character password

### Step 3: Update Django Settings
Open `beauty_clinic_django/settings.py` and update these lines:

```python
# Email Configuration for Password Reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-actual-email@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # Replace with app password
DEFAULT_FROM_EMAIL = 'Skinovation Beauty Clinic <your-actual-email@gmail.com>'
```

## URL Structure

The password reset system uses these URLs:

- `/accounts/password-reset/` - Request password reset
- `/accounts/password-reset/done/` - Email sent confirmation
- `/accounts/password-reset/confirm/<uidb64>/<token>/` - Set new password
- `/accounts/password-reset/complete/` - Password reset complete

## How It Works

1. **Patient clicks "Forgot Password?"** on login page
2. **Enters email address** on reset request page
3. **System validates** email belongs to a patient account
4. **Email sent** with secure reset link (expires in 1 hour)
5. **Patient clicks link** in email
6. **Sets new password** on secure form
7. **Redirected to login** with success message

## Security Features

- **Time-limited tokens** (1 hour expiration)
- **Patient-only access** (other user types cannot reset)
- **Secure token generation** using Django's built-in system
- **HTTPS-ready** reset links
- **CSRF protection** on all forms

## Testing the System

1. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to patient login:**
   ```
   http://127.0.0.1:8000/accounts/login/patient/
   ```

3. **Click "Forgot Password?"**

4. **Enter a patient's email address**

5. **Check email inbox** for reset link

6. **Click the link** and set new password

## Troubleshooting

### Email Not Sending
- Verify Gmail credentials in settings.py
- Check if 2FA is enabled on Gmail account
- Ensure app password is correct (16 characters)
- Check Django console for error messages

### Reset Link Not Working
- Check if link has expired (1 hour limit)
- Verify URL structure matches Django patterns
- Check if user account is active

### Styling Issues
- Ensure static files are collected: `python manage.py collectstatic`
- Check if CSS files are loading properly
- Verify template inheritance is working

## Customization

### Email Template
Edit `templates/accounts/password_reset_email.html` to customize:
- Clinic branding
- Contact information
- Email styling
- Security messages

### UI Styling
All password reset pages use the same design system:
- `templates/accounts/password_reset.html`
- `templates/accounts/password_reset_done.html`
- `templates/accounts/password_reset_confirm.html`
- `templates/accounts/password_reset_complete.html`

### Timeout Settings
Modify `PASSWORD_RESET_TIMEOUT` in settings.py to change token expiration time.

## Files Modified/Created

### New Files:
- `templates/accounts/password_reset.html`
- `templates/accounts/password_reset_done.html`
- `templates/accounts/password_reset_confirm.html`
- `templates/accounts/password_reset_complete.html`
- `templates/accounts/password_reset_email.html`
- `templates/accounts/password_reset_subject.txt`
- `PASSWORD_RESET_SETUP.md`

### Modified Files:
- `accounts/forms.py` - Added password reset forms
- `accounts/views.py` - Added password reset views
- `accounts/urls.py` - Added password reset URLs
- `templates/accounts/patient_login.html` - Added forgot password link
- `beauty_clinic_django/settings.py` - Added email configuration

## Support

If you encounter any issues with the password reset system, check:
1. Django console for error messages
2. Gmail account security settings
3. Network connectivity
4. Django email backend configuration

The system is now ready for production use with proper Gmail credentials!
