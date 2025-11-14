# SMS Template System Guide

## Overview

The SMS Template System allows you to create and manage customizable SMS message templates for your beauty clinic. Instead of hardcoded messages, you can now create flexible templates with variables that get automatically filled in with patient information.

## Features

### ✅ **Template Management**
- Create, edit, and delete SMS templates
- Organize templates by type (confirmation, reminder, cancellation, etc.)
- Activate/deactivate templates
- Preview templates with sample data

### ✅ **Variable System**
- Use variables like `{patient_name}`, `{appointment_date}`, `{service_name}`, etc.
- Automatic variable replacement with real data
- Support for different template types with specific variables

### ✅ **Admin Interface**
- User-friendly web interface for managing templates
- Template preview functionality
- Test send feature to verify templates
- Template history and tracking

## Available Variables

### General Variables
- `{patient_name}` - Patient's full name
- `{clinic_name}` - Your clinic name
- `{clinic_phone}` - Your clinic phone number
- `{clinic_address}` - Your clinic address

### Appointment Variables
- `{appointment_date}` - Appointment date (formatted)
- `{appointment_time}` - Appointment time (formatted)
- `{service_name}` - Service or package name
- `{cancellation_reason}` - Reason for cancellation

### Package Variables
- `{package_name}` - Package name
- `{package_price}` - Package price (formatted)
- `{package_sessions}` - Number of sessions
- `{package_duration}` - Package duration in days

## Template Types

1. **Appointment Confirmation** - Sent when appointments are confirmed
2. **Appointment Reminder** - Sent 24 hours before appointments
3. **Cancellation Notification** - Sent when appointments are cancelled
4. **Package Confirmation** - Sent when packages are booked
5. **Custom Template** - For any custom SMS needs

## How to Use

### 1. Access SMS Templates
- Log in as admin/owner
- Go to "SMS Templates" in the sidebar
- View all your templates

### 2. Create a New Template
- Click "Create Template"
- Choose template type
- Enter template name and message
- Use variables in your message (e.g., `{patient_name}`)
- Save the template

### 3. Edit Existing Templates
- Click on any template to view details
- Click "Edit" to modify
- Preview your changes
- Save updates

### 4. Test Templates
- Go to template details page
- Use "Test Send" feature
- Enter a phone number
- Customize variables if needed
- Send test SMS

### 5. Activate/Deactivate
- Toggle template status
- Only active templates are used for sending
- Inactive templates are kept for future use

## Example Templates

### Appointment Confirmation
```
Hi {patient_name}!

Your appointment has been confirmed:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}
Location: {clinic_name}

Please arrive 15 minutes early.
Thank you for choosing us!

- {clinic_name} Team
```

### Appointment Reminder
```
Hi {patient_name}!

Reminder: You have an appointment tomorrow:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}

Please arrive 15 minutes early.
See you soon!

- {clinic_name} Team
```

### Cancellation Notification
```
Hi {patient_name}!

Your appointment has been cancelled:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}

{cancellation_reason}

Please contact us to reschedule.
Thank you for your understanding.

- {clinic_name} Team
```

## Default Templates

The system comes with pre-created default templates:
- Default Confirmation
- Default Reminder  
- Default Cancellation
- Default Package Confirmation

You can edit these or create your own custom templates.

## Technical Details

### Database Models
- `SMSTemplate` - Stores template information
- `SMSHistory` - Tracks sent messages with template reference

### Services
- `SMSTemplateService` - Handles template rendering and sending
- `IPROGSMSService` - Updated to use templates instead of hardcoded messages

### Admin Interface
- Template management views
- Form validation
- AJAX operations for better UX

## Benefits

1. **Flexibility** - Easy to customize messages without code changes
2. **Consistency** - Standardized message format across all communications
3. **Efficiency** - No need to manually type messages each time
4. **Professional** - Well-formatted, branded messages
5. **Scalable** - Easy to add new template types and variables

## Getting Started

1. Run migrations: `python manage.py migrate`
2. Create default templates: `python manage.py create_default_sms_templates`
3. Access admin panel and go to "SMS Templates"
4. Start customizing your templates!

## Support

For any issues or questions about the SMS Template System, check the admin interface or contact your system administrator.
