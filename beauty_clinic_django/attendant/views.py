from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.models import User, Attendant
from appointments.models import Appointment, Notification
import json


def is_attendant(user):
    """Check if user is attendant"""
    return user.is_authenticated and user.user_type == 'attendant'


@login_required
@user_passes_test(is_attendant)
def attendant_dashboard(request):
    """Attendant dashboard - View appointments they are in charge of"""
    today = timezone.now().date()
    
    # Get today's appointments assigned to this attendant
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).order_by('appointment_time')
    
    # Get upcoming appointments (next 7 days) assigned to this attendant
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        appointment_date__lte=today + timezone.timedelta(days=7),
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date', 'appointment_time')
    
    # Get notifications regarding appointments this attendant is in charge of
    notifications = Notification.objects.filter(
        type__in=['appointment', 'confirmation', 'cancellation']
    ).order_by('-created_at')[:3]
    
    # Statistics for this attendant
    total_appointments = Appointment.objects.count()
    today_count = today_appointments.count()
    upcoming_count = upcoming_appointments.count()
    
    # Get notification count
    notification_count = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()
    
    context = {
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'notifications': notifications,
        'total_appointments': total_appointments,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'today': today,
        'notification_count': notification_count,
    }
    
    return render(request, 'attendant/dashboard.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_appointments(request):
    """Attendant appointments management"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Start with all appointments
    appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    
    # Apply filters
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(service__service_name__icontains=search_query) |
            Q(product__product_name__icontains=search_query) |
            Q(package__package_name__icontains=search_query)
        )
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search_query': search_query,
    }
    
    return render(request, 'attendant/appointments.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_appointment_detail(request, appointment_id):
    """Attendant view for appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # For now, allow all attendants to view all appointments
    # In a real system, you would check if the attendant is assigned to this appointment
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'attendant/appointment_detail.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_confirm_appointment(request, appointment_id):
    """Attendant confirm an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # For now, allow all attendants to view all appointments
    # In a real system, you would check if the attendant is assigned to this appointment
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='confirmation',
            appointment_id=appointment.id,
            title='Appointment Confirmed',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed by your attendant.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed.')
    else:
        messages.error(request, 'Only pending appointments can be confirmed.')
    
    return redirect('attendant:appointment_detail', appointment_id=appointment_id)


@login_required
@user_passes_test(is_attendant)
def attendant_complete_appointment(request, appointment_id):
    """Attendant mark appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # For now, allow all attendants to view all appointments
    # In a real system, you would check if the attendant is assigned to this appointment
    
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'completed'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='appointment',
            appointment_id=appointment.id,
            title='Appointment Completed',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} has been completed. Thank you for choosing Skinovation Beauty Clinic!',
            patient=appointment.patient
        )
        
        messages.success(request, f'Appointment for {appointment.patient.full_name} has been marked as completed.')
    else:
        messages.error(request, 'Only pending or confirmed appointments can be completed.')
    
    return redirect('attendant:appointment_detail', appointment_id=appointment_id)


@login_required
@user_passes_test(is_attendant)
def attendant_patient_profile(request, patient_id):
    """Attendant view patient profile"""
    patient = get_object_or_404(User, id=patient_id, user_type='patient')
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(
        patient=patient
    ).order_by('-appointment_date')
    
    # Get patient's packages (if any)
    packages = []  # Simplified for now
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'packages': packages,
    }
    
    return render(request, 'attendant/patient_profile.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_notifications(request):
    """Attendant notifications"""
    notifications = Notification.objects.filter(
        type__in=['appointment', 'confirmation', 'cancellation']
    ).order_by('-created_at')
    
    # Mark notifications as read
    unread_notifications = notifications.filter(is_read=False)
    for notification in unread_notifications:
        notification.is_read = True
        notification.save()
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'attendant/notifications.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Notification marked as read.')
    return redirect('attendant:notifications')


# API Endpoints for notifications
@csrf_exempt
@login_required
@user_passes_test(is_attendant)
def get_notifications_api(request):
    """API endpoint to get notifications for attendant"""
    try:
        notifications = Notification.objects.filter(
            type__in=['appointment', 'confirmation', 'cancellation']
        ).order_by('-created_at')[:20]
        
        unread_count = notifications.filter(is_read=False).count()
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'created_at_formatted': notification.created_at.strftime('%b %d, %Y %I:%M %p'),
                'is_read': notification.is_read,
                'type': notification.type
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required
@user_passes_test(is_attendant)
def update_notifications_api(request):
    """API endpoint to update notifications"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    notification = get_object_or_404(Notification, id=notification_id)
                    notification.is_read = True
                    notification.save()
                    
            elif action == 'mark_all_read':
                Notification.objects.filter(
                    type__in=['appointment', 'confirmation', 'cancellation']
                ).update(is_read=True)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid method'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
