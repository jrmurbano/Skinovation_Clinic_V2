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
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        attendant_obj = None
        messages.warning(request, 'No attendant profile found. Please contact staff to set up your attendant profile.')
    
    # Get today's appointments assigned to this attendant
    if attendant_obj:
        today_appointments = Appointment.objects.filter(
            appointment_date=today,
            attendant=attendant_obj
        ).order_by('appointment_time')
        
        # Get upcoming appointments (next 7 days) assigned to this attendant
        upcoming_appointments = Appointment.objects.filter(
            appointment_date__gte=today,
            appointment_date__lte=today + timezone.timedelta(days=7),
            status__in=['pending', 'confirmed'],
            attendant=attendant_obj
        ).order_by('appointment_date', 'appointment_time')
    else:
        today_appointments = Appointment.objects.none()
        upcoming_appointments = Appointment.objects.none()
    
    # Get notifications regarding appointments this attendant is in charge of
    notifications = Notification.objects.filter(
        type__in=['appointment', 'confirmation', 'cancellation']
    ).order_by('-created_at')[:3]
    
    # Statistics for this attendant
    if attendant_obj:
        total_appointments = Appointment.objects.filter(attendant=attendant_obj).count()
    else:
        total_appointments = 0
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
    """Attendant appointments management - Only shows appointments assigned to this attendant"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        attendant_obj = None
        messages.warning(request, 'No attendant profile found. Please contact staff to set up your attendant profile.')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Start with appointments assigned to this attendant only
    if attendant_obj:
        appointments = Appointment.objects.filter(attendant=attendant_obj).order_by('-appointment_date', '-appointment_time')
    else:
        appointments = Appointment.objects.none()
    
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
    """Attendant view appointment details - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only view appointments assigned to you.')
        return redirect('attendant:appointments')
    
    # Get feedback for this appointment
    from appointments.models import Feedback
    feedback = None
    attendant_feedback = None
    try:
        feedback = Feedback.objects.get(appointment=appointment)
        # Separate service/package/product feedback from attendant feedback
        attendant_feedback = {
            'rating': feedback.attendant_rating,
            'comment': feedback.comment if feedback.attendant_rating else None
        }
    except Feedback.DoesNotExist:
        pass
    
    context = {
        'appointment': appointment,
        'feedback': feedback,
        'attendant_feedback': attendant_feedback,
    }
    
    return render(request, 'attendant/appointment_detail.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_confirm_appointment(request, appointment_id):
    """Attendant confirm an appointment - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only confirm appointments assigned to you.')
        return redirect('attendant:appointments')
    
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
    """Attendant mark appointment as completed - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only complete appointments assigned to you.')
        return redirect('attendant:appointments')
    
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'completed'
        appointment.save()
        
        # Create notification for patient with feedback prompt
        Notification.objects.create(
            type='appointment',
            appointment_id=appointment.id,
            title='Appointment Completed - Please Leave Feedback',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} has been completed. Please leave your feedback to help us improve our services!',
            patient=appointment.patient
        )
        
        messages.success(request, f'Appointment for {appointment.patient.full_name} has been marked as completed. Feedback form will be available to the patient.')
    else:
        messages.error(request, 'Only pending or confirmed appointments can be completed.')
    
    return redirect('attendant:appointment_detail', appointment_id=appointment_id)


@login_required
@user_passes_test(is_attendant)
def attendant_patient_profile(request, patient_id):
    """Attendant view patient profile - Only for patients with assigned appointments"""
    patient = get_object_or_404(User, id=patient_id, user_type='patient')
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify patient has assigned appointment with this attendant (Data Privacy compliance)
    if not Appointment.objects.filter(patient=patient, attendant=attendant_obj).exists():
        messages.error(request, 'You can only view patient profiles for appointments assigned to you.')
        return redirect('attendant:dashboard')
    
    # Get patient's appointments assigned to this attendant only
    appointments = Appointment.objects.filter(
        patient=patient,
        attendant=attendant_obj
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
def attendant_history(request):
    """Attendant view own history of completed appointments only"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get only completed appointments assigned to this attendant
    completed_appointments = Appointment.objects.filter(
        attendant=attendant_obj,
        status='completed'
    ).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'completed_appointments': completed_appointments,
    }
    
    return render(request, 'attendant/history.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_feedback(request):
    """Attendant view own feedback from patients"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get feedback for appointments assigned to this attendant
    from appointments.models import Feedback
    feedbacks = Feedback.objects.filter(
        appointment__attendant=attendant_obj,
        attendant_rating__isnull=False
    ).order_by('-created_at')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(feedbacks, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedbacks': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'attendant/feedback.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_schedule(request):
    """Attendant view their availability schedule"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get attendant profile with work schedule
    try:
        profile = request.user.attendant_profile
    except:
        from accounts.models import AttendantProfile
        profile = None
    
    context = {
        'attendant': attendant_obj,
        'profile': profile,
    }
    
    return render(request, 'attendant/schedule.html', context)


@login_required
@user_passes_test(is_attendant)
def attendant_manage_profile(request):
    """Attendant manage their own profile (edit name, username, email)"""
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        
        if not all([first_name, last_name, username]):
            messages.error(request, 'First name, last name, and username are required.')
            return redirect('attendant:manage_profile')
        
        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('attendant:manage_profile')
        
        # Check if email is already taken by another user (if provided)
        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'That email is already taken. Please choose another one.')
            return redirect('attendant:manage_profile')
        
        # Store old names before updating
        old_first_name = user.first_name
        old_last_name = user.last_name
        
        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        if email:
            user.email = email
        if middle_name:
            user.middle_name = middle_name
        user.save()
        
        # Update Attendant object if it exists (match by old name)
        try:
            attendant_obj = Attendant.objects.get(
                first_name=old_first_name,
                last_name=old_last_name
            )
            # Update the Attendant object with new names
            attendant_obj.first_name = first_name
            attendant_obj.last_name = last_name
            attendant_obj.save()
        except Attendant.DoesNotExist:
            # Attendant object doesn't exist - that's okay, it might be created by staff later
            pass
        except Attendant.MultipleObjectsReturned:
            # Multiple attendants with same name - update all
            Attendant.objects.filter(
                first_name=old_first_name,
                last_name=old_last_name
            ).update(first_name=first_name, last_name=last_name)
        
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('attendant:manage_profile')
    
    context = {
        'user': user,
    }
    
    return render(request, 'attendant/manage_profile.html', context)


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
        # Filter notifications for the current attendant user
        notifications = Notification.objects.filter(
            patient=request.user,
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
