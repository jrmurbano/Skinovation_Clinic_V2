# SMS Integration Setup Guide

This guide will help you set up SMS notifications using the IPROG SMS API for your beauty clinic system.

## 📱 **IPROG SMS API Setup**

### 1. **Get Your API Key**
1. Visit [https://sms.iprogtech.com/](https://sms.iprogtech.com/)
2. Register for an account
3. Purchase SMS credits (₱1 per SMS)
4. Get your API key from the dashboard

### 2. **Configure Your Django Settings**
1. Open `beauty_clinic_django/settings.py`
2. Find the SMS configuration section
3. Replace `'your_api_key_here'` with your actual API key:

```python
# SMS API Configuration
IPROG_SMS_API_KEY = 'your_actual_api_key_here'  # Replace with your API key
SMS_ENABLED = True  # Set to False to disable SMS notifications
SMS_SENDER_ID = 'BEAUTY'  # Your preferred sender ID
```

### 3. **Test SMS Functionality**
1. Log in as the owner
2. Go to "SMS Testing" in the sidebar
3. Enter a phone number and test message
4. Click "Send SMS" to test

## 🔧 **SMS Features Included**

### **Automatic SMS Notifications**
- ✅ **Appointment Confirmations**: Sent when appointments are booked
- ✅ **Appointment Reminders**: Sent 24 hours before appointments
- ✅ **Cancellation Notifications**: Sent when appointments are cancelled
- ✅ **Package Confirmations**: Sent when packages are booked

### **Manual SMS Testing**
- ✅ **SMS Test Page**: Owner can send test SMS messages
- ✅ **Patient Quick Select**: Choose from recent patients
- ✅ **Real-time Results**: See SMS sending status immediately

### **Management Commands**
- ✅ **Reminder System**: Send appointment reminders via command line
- ✅ **Bulk Notifications**: Send reminders to multiple patients

## 📋 **Usage Instructions**

### **For Patients**
1. Patients will automatically receive SMS notifications when:
   - Booking appointments (if they have a phone number in their profile)
   - Appointments are confirmed
   - Appointments are cancelled
   - Booking packages

**Note**: Make sure patients have their phone numbers saved in their profiles for SMS notifications to work.

### **For Staff/Admin**
1. SMS notifications are sent automatically when:
   - Confirming appointments
   - Cancelling appointments
   - Processing appointment status changes

### **For Owner**
1. Test SMS functionality at `/owner/sms-test/`
2. Monitor SMS delivery status
3. Send manual notifications if needed

## 🚀 **Running Reminder Commands**

To send appointment reminders for tomorrow's appointments:

```bash
python manage.py send_reminders
```

This command will:
- Find all confirmed appointments for tomorrow
- Send SMS reminders to patients with phone numbers
- Show success/failure status for each SMS

## 📞 **Phone Number Formats**

The system accepts phone numbers in these formats:
- **International**: `+639xxxxxxxxx`
- **Local with 0**: `09xxxxxxxxx`
- **Local without 0**: `9xxxxxxxxx`

The system automatically converts all formats to international format.

## 💰 **Cost Information**

- **Cost**: ₱1 per SMS
- **No hidden fees**
- **Reliable delivery**
- **Perfect for capstone projects**

## 🔍 **Troubleshooting**

### **SMS Not Sending**
1. Check your API key in settings
2. Verify you have SMS credits
3. Check phone number format
4. Review error messages in the SMS test page

### **Common Issues**
- **Invalid API Key**: Make sure your API key is correct
- **Insufficient Credits**: Add more credits to your IPROG account
- **Invalid Phone Number**: Use proper Philippine phone number format
- **Network Issues**: Check your internet connection

## 📊 **Monitoring SMS Usage**

1. Check your IPROG SMS dashboard for usage statistics
2. Monitor SMS delivery status in the test page
3. Review Django logs for any SMS-related errors

## 🎯 **Best Practices**

1. **Test First**: Always test SMS functionality before going live
2. **Monitor Credits**: Keep track of your SMS credits
3. **Phone Numbers**: Ensure patients have valid phone numbers
4. **Message Length**: Keep messages under 160 characters
5. **Timing**: Send reminders at appropriate times

## 📞 **Support**

- **IPROG SMS Support**: Contact through their website
- **API Documentation**: [https://sms.iprogtech.com/](https://sms.iprogtech.com/)
- **Student-Friendly**: Designed specifically for capstone projects

---

**Your beauty clinic system now has professional SMS notification capabilities!** 🎉

Perfect for impressing your professors and demonstrating real-world integration skills.
