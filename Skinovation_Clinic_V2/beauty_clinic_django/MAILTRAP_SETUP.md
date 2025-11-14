# Mailtrap Integration Setup Guide

This guide will help you set up Mailtrap for email functionality in the Skinovation Beauty Clinic Django application.

## 🎯 **What's Implemented**

✅ **Mailtrap API Integration** - Using your provided API token  
✅ **Password Reset Emails** - Beautiful HTML emails sent via Mailtrap  
✅ **Test Email Functionality** - Verify integration is working  
✅ **Error Handling** - Proper error messages and logging  
✅ **Custom Email Service** - Reusable email service class  

## 🔧 **Setup Steps**

### **Step 1: Get Your Mailtrap Credentials**

1. **Go to Mailtrap**: https://mailtrap.io/home
2. **Sign up/Login** to your account
3. **Navigate to Email Testing** → **Inboxes**
4. **Select your inbox** (or create a new one)
5. **Go to SMTP Settings** tab
6. **Copy your credentials**:
   - **Username**: `your-mailtrap-username`
   - **Password**: `your-mailtrap-password`

### **Step 2: Update Django Settings**

Open `beauty_clinic_django/settings.py` and update these lines:

```python
# Email Configuration for Password Reset - Using Mailtrap
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-actual-mailtrap-username'  # Replace with your username
EMAIL_HOST_PASSWORD = 'your-actual-mailtrap-password'  # Replace with your password
DEFAULT_FROM_EMAIL = 'Skinovation Beauty Clinic <noreply@skinovation.com>'

# Mailtrap API Configuration
MAILTRAP_API_TOKEN = '6ee5f126dda72a6010c1adcd0d5f0bb7'  # Your API token
```

### **Step 3: Test the Integration**

1. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Test Mailtrap directly**:
   - Go to: `http://127.0.0.1:8000/accounts/test-mailtrap/`
   - Enter an email address
   - Click "Send Test Email"
   - Check your Mailtrap inbox

3. **Test Password Reset**:
   - Go to: `http://127.0.0.1:8000/accounts/login/patient/`
   - Click "Forgot Password?"
   - Enter a patient's email
   - Check your Mailtrap inbox for the reset email

## 📧 **Email Features**

### **Password Reset Email**
- **Beautiful HTML template** with clinic branding
- **Secure reset links** (1-hour expiration)
- **Professional styling** with gradients and animations
- **Mobile-responsive** design
- **Security notices** and contact information

### **Test Email**
- **Simple test functionality** to verify integration
- **Customizable recipient** and name
- **Success/error feedback** messages

## 🔍 **How It Works**

1. **User requests password reset** on login page
2. **System validates** email belongs to a patient
3. **Mailtrap API sends** beautiful HTML email
4. **User clicks reset link** in email
5. **User sets new password** on secure form
6. **User redirected** to login with success message

## 📁 **Files Created/Modified**

### **New Files:**
- `accounts/email_service.py` - Mailtrap email service
- `templates/accounts/test_mailtrap.html` - Test email page
- `MAILTRAP_SETUP.md` - This setup guide

### **Modified Files:**
- `beauty_clinic_django/settings.py` - Mailtrap configuration
- `accounts/views.py` - Updated password reset to use Mailtrap
- `accounts/urls.py` - Added test email URL

## 🚀 **Testing URLs**

- **Test Email**: `http://127.0.0.1:8000/accounts/test-mailtrap/`
- **Password Reset**: `http://127.0.0.1:8000/accounts/password-reset/`
- **Patient Login**: `http://127.0.0.1:8000/accounts/login/patient/`

## 🔧 **Troubleshooting**

### **Email Not Sending**
1. **Check Mailtrap credentials** in settings.py
2. **Verify API token** is correct
3. **Check Mailtrap inbox** for sent emails
4. **Look at Django console** for error messages

### **API Token Issues**
1. **Verify token** is from correct Mailtrap account
2. **Check token permissions** in Mailtrap dashboard
3. **Generate new token** if needed

### **SMTP Issues**
1. **Double-check username/password** from Mailtrap
2. **Verify SMTP settings** (host: sandbox.smtp.mailtrap.io, port: 2525)
3. **Check TLS is enabled**

## 📊 **Mailtrap Dashboard**

- **View sent emails** in your Mailtrap inbox
- **Check delivery status** and logs
- **Monitor email performance** and analytics
- **Debug email issues** with detailed logs

## 🎨 **Email Customization**

### **Update Email Template**
Edit `templates/accounts/password_reset_email.html`:
- Change clinic branding
- Update contact information
- Modify styling and colors
- Add/remove sections

### **Update Email Service**
Edit `accounts/email_service.py`:
- Change sender information
- Modify email categories
- Add new email types
- Update error handling

## 🔒 **Security Features**

- **Secure token generation** using Django's built-in system
- **Time-limited reset links** (1 hour expiration)
- **Patient-only access** (other user types cannot reset)
- **CSRF protection** on all forms
- **Email validation** before sending

## 📈 **Production Considerations**

For production, consider:
- **Upgrade to Mailtrap Production** for real email delivery
- **Add email templates** for different languages
- **Implement email queuing** for high volume
- **Add email analytics** and tracking
- **Set up email monitoring** and alerts

## 🎯 **Next Steps**

1. **Update Mailtrap credentials** in settings.py
2. **Test the integration** using the test page
3. **Try password reset** with a real patient email
4. **Customize email templates** as needed
5. **Monitor email delivery** in Mailtrap dashboard

The system is now ready for testing and production use! 🎊
