from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, time as time_obj
from .models import Appointment, Notification
from accounts.models import User, Attendant, AttendantProfile
from services.models import Service
from products.models import Product
from packages.models import Package
from services.utils import send_appointment_sms
import json


@login_required
def my_appointments(request):
    """User's appointments"""
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def book_service(request, service_id):
    """Book a service appointment"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        attendant_id = request.POST.get('attendant', '')
        
        if appointment_date and appointment_time:
            # Get the attendant - handle empty or invalid IDs
            if attendant_id:
                try:
                    attendant = Attendant.objects.get(id=int(attendant_id))
                except (Attendant.DoesNotExist, ValueError, TypeError):
                    # If attendant doesn't exist, get the first available attendant
                    attendant = Attendant.objects.first()
                    if not attendant:
                        messages.error(request, 'No attendants available. Please contact the clinic.')
                        context = {
                            'service': service,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_service.html', context)
            else:
                # If no attendant selected, get the first available
                attendant = Attendant.objects.first()
                if not attendant:
                    messages.error(request, 'No attendants available. Please contact the clinic.')
                    context = {
                        'service': service,
                        'attendants': Attendant.objects.all(),
                    }
                    return render(request, 'appointments/book_service.html', context)
            
            # Check attendant availability based on work schedule
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            day_name = appointment_datetime.strftime('%A')
            appointment_time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            
            # Check if attendant has a profile
            attendant_available = True
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name)
                profile = getattr(user, 'attendant_profile', None)
                
                if profile:
                    # Check if it's a work day
                    if day_name not in profile.work_days:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} is not available on {day_name}. Please choose another day or attendant.')
                        context = {
                            'service': service,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_service.html', context)
                    
                    # Check if time is within work hours
                    if appointment_time_obj < profile.start_time or appointment_time_obj >= profile.end_time:
                        messages.error(request, f'Appointment time must be between {profile.start_time.strftime("%I:%M %p")} and {profile.end_time.strftime("%I:%M %p")} for {attendant.first_name} {attendant.last_name}.')
                        context = {
                            'service': service,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_service.html', context)
                    attendant_available = True
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                # If no user found, proceed without schedule check (backward compatibility)
                attendant_available = True
            
            # Check for existing appointments at the same time slot
            existing_appointments = Appointment.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                attendant_id=attendant.id,
                status__in=['pending', 'confirmed']
            ).count()
            
            # Maximum 3 patients per time slot
            if existing_appointments >= 3:
                messages.error(request, 'This time slot is fully booked. Please choose another time.')
                context = {
                    'service': service,
                    'attendants': Attendant.objects.all(),
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # Auto-confirm if attendant is available (has profile with matching schedule)
            initial_status = 'pending'
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name)
                profile = getattr(user, 'attendant_profile', None)
                if profile and day_name in profile.work_days and profile.start_time <= appointment_time_obj < profile.end_time:
                    initial_status = 'confirmed'  # Auto-confirm when attendant is available
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass
            
            appointment = Appointment.objects.create(
                patient=request.user,
                service=service,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Appointment Booked' if initial_status == 'pending' else 'Appointment Confirmed',
                message=f'Your {service.service_name} appointment has been {"booked" if initial_status == "pending" else "confirmed"} for {appointment_date} at {appointment_time}. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            # Send SMS confirmation
            sms_result = send_appointment_sms(appointment, 'confirmation')
            if sms_result['success']:
                messages.success(request, f'Appointment {"booked" if initial_status == "pending" else "confirmed automatically"}! SMS confirmation sent. Transaction ID: {transaction_id}')
            else:
                messages.success(request, f'Appointment {"booked" if initial_status == "pending" else "confirmed automatically"}! (SMS notification failed) Transaction ID: {transaction_id}')
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get all attendants (availability will be checked on booking)
    context = {
        'service': service,
        'attendants': Attendant.objects.all(),
    }
    
    return render(request, 'appointments/book_service.html', context)


@login_required
def book_product(request, product_id):
    """Book a product pre-order"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        
        if appointment_date and appointment_time:
            # Check stock availability
            if product.stock <= 0:
                messages.error(request, f'Sorry, {product.product_name} is currently out of stock. Please check back later or contact the clinic.')
                context = {
                    'product': product,
                }
                return render(request, 'appointments/book_product.html', context)
            
            # Get the default attendant for product pre-orders
            attendant = get_object_or_404(Attendant, id=1)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # Auto-confirm pre-order if stock is available
            initial_status = 'confirmed' if product.stock > 0 else 'pending'
            
            appointment = Appointment.objects.create(
                patient=request.user,
                product=product,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Deduct stock when pre-order is confirmed
            if initial_status == 'confirmed':
                product.stock -= 1
                product.save()
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Product Pre-Ordered',
                message=f'Your {product.product_name} has been pre-ordered for pickup on {appointment_date} at {appointment_time}. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            # Send SMS confirmation
            sms_result = send_appointment_sms(appointment, 'confirmation')
            if sms_result['success']:
                messages.success(request, f'Product pre-ordered successfully! SMS confirmation sent. Transaction ID: {transaction_id}')
            else:
                messages.success(request, f'Product pre-ordered successfully! (SMS notification failed) Transaction ID: {transaction_id}')
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'product': product,
    }
    
    return render(request, 'appointments/book_product.html', context)


@login_required
def book_package(request, package_id):
    """Book a package"""
    package = get_object_or_404(Package, id=package_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        attendant_id = request.POST.get('attendant', '')
        
        if appointment_date and appointment_time:
            # Get the attendant - handle empty or invalid IDs
            if attendant_id:
                try:
                    attendant = Attendant.objects.get(id=int(attendant_id))
                except (Attendant.DoesNotExist, ValueError, TypeError):
                    # If attendant doesn't exist, get the first available attendant
                    attendant = Attendant.objects.first()
                    if not attendant:
                        messages.error(request, 'No attendants available. Please contact the clinic.')
                        context = {
                            'package': package,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_package.html', context)
            else:
                # If no attendant selected, get the first available
                attendant = Attendant.objects.first()
                if not attendant:
                    messages.error(request, 'No attendants available. Please contact the clinic.')
                    context = {
                        'package': package,
                        'attendants': Attendant.objects.all(),
                    }
                    return render(request, 'appointments/book_package.html', context)
            
            # Check attendant availability based on work schedule
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            day_name = appointment_datetime.strftime('%A')
            appointment_time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            
            # Check if attendant has a profile
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name)
                profile = getattr(user, 'attendant_profile', None)
                
                if profile:
                    # Check if it's a work day
                    if day_name not in profile.work_days:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} is not available on {day_name}. Please choose another day or attendant.')
                        context = {
                            'package': package,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_package.html', context)
                    
                    # Check if time is within work hours
                    if appointment_time_obj < profile.start_time or appointment_time_obj >= profile.end_time:
                        messages.error(request, f'Appointment time must be between {profile.start_time.strftime("%I:%M %p")} and {profile.end_time.strftime("%I:%M %p")} for {attendant.first_name} {attendant.last_name}.')
                        context = {
                            'package': package,
                            'attendants': Attendant.objects.all(),
                        }
                        return render(request, 'appointments/book_package.html', context)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                # If no user found, proceed without schedule check (backward compatibility)
                pass
            
            # Check for existing appointments at the same time slot
            existing_appointments = Appointment.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                attendant_id=attendant.id,
                status__in=['pending', 'confirmed']
            ).count()
            
            # Maximum 3 patients per time slot
            if existing_appointments >= 3:
                messages.error(request, 'This time slot is fully booked. Please choose another time.')
                context = {
                    'package': package,
                    'attendants': Attendant.objects.all(),
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # Auto-confirm if attendant is available (has profile with matching schedule)
            initial_status = 'pending'
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name)
                profile = getattr(user, 'attendant_profile', None)
                if profile and day_name in profile.work_days and profile.start_time <= appointment_time_obj < profile.end_time:
                    initial_status = 'confirmed'  # Auto-confirm when attendant is available
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass
            
            appointment = Appointment.objects.create(
                patient=request.user,
                package=package,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Package Booked' if initial_status == 'pending' else 'Package Confirmed',
                message=f'Your {package.package_name} package has been {"booked" if initial_status == "pending" else "confirmed"} for {appointment_date} at {appointment_time}. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            messages.success(request, f'Package {"booked" if initial_status == "pending" else "confirmed automatically"}! Transaction ID: {transaction_id}')
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'package': package,
        'attendants': Attendant.objects.all(),
    }
    
    return render(request, 'appointments/book_package.html', context)


@login_required
def notifications(request):
    """User's notifications"""
    notifications = Notification.objects.filter(patient=request.user).order_by('-created_at')
    
    # Mark notifications as read
    notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'appointments/notifications.html', context)


@login_required
def request_cancellation(request, appointment_id):
    """Request cancellation for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if appointment can be cancelled (must be at least 2 days before)
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointment_date, appointment.appointment_time)
    )
    days_until_appointment = (appointment_datetime - timezone.now()).days
    
    if days_until_appointment < 2:
        messages.error(request, 'Cancellation is not allowed within 2 days of the appointment. Please contact the clinic directly.')
        return redirect('appointments:my_appointments')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Check if appointment can be cancelled
        if appointment.status not in ['pending', 'confirmed']:
            messages.error(request, 'This appointment cannot be cancelled.')
            return redirect('appointments:my_appointments')
        
        # Create cancellation request
        from .models import CancellationRequest
        
        # Determine appointment type
        appointment_type = 'regular'
        if appointment.package:
            appointment_type = 'package'
        
        cancellation_request = CancellationRequest.objects.create(
            appointment_id=appointment.id,
            appointment_type=appointment_type,
            patient=request.user,
            reason=reason,
            status='pending'
        )
        
        # Create notification for staff
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Request',
            message=f'Patient {request.user.full_name} has requested to cancel their appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time}. Reason: {reason}',
            patient=None  # Staff notification
        )
        
        messages.success(request, 'Your cancellation request has been submitted. The staff will review it shortly.')
        return redirect('appointments:my_appointments')
    
    # GET request - show cancellation form
    context = {
        'appointment': appointment,
        'days_until_appointment': days_until_appointment,
    }
    
    return render(request, 'appointments/request_cancellation.html', context)


@login_required
def request_reschedule(request, appointment_id):
    """Request reschedule for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_appointment_date')
        new_time = request.POST.get('new_appointment_time')
        reason = request.POST.get('reason', '')
        
        if not new_date or not new_time:
            messages.error(request, 'Please provide both new date and time.')
            return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        
        # Check if appointment can be rescheduled
        if appointment.status not in ['pending', 'confirmed']:
            messages.error(request, 'This appointment cannot be rescheduled.')
            return redirect('appointments:my_appointments')
        
        # Create reschedule request
        from .models import RescheduleRequest
        
        reschedule_request = RescheduleRequest.objects.create(
            appointment_id=appointment.id,
            new_appointment_date=new_date,
            new_appointment_time=new_time,
            patient=request.user,
            reason=reason,
            status='pending'
        )
        
        # Create notification for staff
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Reschedule Request',
            message=f'Patient {request.user.full_name} has requested to reschedule their appointment for {appointment.get_service_name()} from {appointment.appointment_date} at {appointment.appointment_time} to {new_date} at {new_time}. Reason: {reason}',
            patient=None  # Staff notification
        )
        
        messages.success(request, 'Your reschedule request has been submitted. The staff will review it shortly.')
        return redirect('appointments:my_appointments')
    
    # GET request - show reschedule form
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/request_reschedule.html', context)


@login_required
def submit_feedback(request, appointment_id):
    """Submit feedback for a completed appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status != 'completed':
        messages.error(request, 'Feedback can only be submitted for completed appointments.')
        return redirect('appointments:my_appointments')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, 'Please provide a rating.')
            return redirect('appointments:my_appointments')
        
        rating = int(rating)
        if rating < 1 or rating > 5:
            messages.error(request, 'Rating must be between 1 and 5.')
            return redirect('appointments:my_appointments')
        
        # Check if feedback already exists
        from .models import Feedback
        if Feedback.objects.filter(appointment=appointment, patient=request.user).exists():
            messages.error(request, 'You have already submitted feedback for this appointment.')
            return redirect('appointments:my_appointments')
        
        # Create feedback
        Feedback.objects.create(
            appointment=appointment,
            patient=request.user,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('appointments:my_appointments')
    
    return redirect('appointments:my_appointments')


@csrf_exempt
@require_http_methods(["GET"])
def get_notifications_api(request):
    """API endpoint to get notifications (replaces get_notifications.php)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        if request.user.user_type == 'admin':
            # For admin, show all notifications
            notifications = Notification.objects.filter(patient__isnull=True).order_by('-created_at')[:10]
        else:
            # For patients, show their notifications
            notifications = Notification.objects.filter(patient=request.user).order_by('-created_at')[:10]
        
        # Count unread notifications
        unread_count = notifications.filter(is_read=False).count()
        
        # Format notifications
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at_formatted': notification.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_notifications_api(request):
    """API endpoint to update notifications (replaces update_notifications.php)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            action = data.get('action')
            notification_id = data.get('notification_id')
        else:
            action = request.POST.get('action')
            notification_id = request.POST.get('notification_id')
        
        if action == 'mark_read':
            if notification_id:
                notification = get_object_or_404(Notification, id=notification_id)
                if request.user.user_type == 'admin' or notification.patient == request.user:
                    notification.is_read = True
                    notification.save()
                    return JsonResponse({'success': True})
        
        elif action == 'mark_all_read':
            if request.user.user_type == 'admin':
                Notification.objects.filter(patient__isnull=True).update(is_read=True)
            else:
                Notification.objects.filter(patient=request.user).update(is_read=True)
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Invalid action'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})