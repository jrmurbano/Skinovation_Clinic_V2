from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum
from django.http import JsonResponse
from .models import Appointment, Notification
from accounts.models import User
from services.models import Service, ServiceImage
from products.models import Product, ProductImage
from services.utils import send_appointment_sms

def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Staff dashboard - shows appointments, pre-orders, and patient list"""
    # Get today's date
    today = timezone.now().date()
    
    # Get all appointments (services and packages)
    all_appointments = Appointment.objects.filter(
        Q(service__isnull=False) | Q(package__isnull=False)
    ).order_by('-appointment_date', '-appointment_time')[:10]
    
    # Get pre-orders (product appointments)
    pre_orders = Appointment.objects.filter(
        product__isnull=False
    ).order_by('-appointment_date', '-appointment_time')[:10]
    
    # Get patient list
    patients = User.objects.filter(user_type='patient').order_by('-date_joined')[:10]
    
    # Get statistics
    total_appointments = Appointment.objects.filter(
        Q(service__isnull=False) | Q(package__isnull=False)
    ).count()
    pending_count = Appointment.objects.filter(
        status='pending',
        product__isnull=True
    ).count()
    confirmed_count = Appointment.objects.filter(
        status='confirmed',
        product__isnull=True
    ).count()
    pre_order_count = Appointment.objects.filter(product__isnull=False).count()
    total_patients = User.objects.filter(user_type='patient').count()
    
    context = {
        'all_appointments': all_appointments,
        'pre_orders': pre_orders,
        'patients': patients,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'pre_order_count': pre_order_count,
        'total_patients': total_patients,
        'today': today,
    }
    
    return render(request, 'appointments/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_appointments(request):
    """Admin view for all appointments"""
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
    
    return render(request, 'appointments/admin_appointments.html', context)

@login_required
@user_passes_test(is_admin)
def admin_appointment_detail(request, appointment_id):
    """Admin view for appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/admin_appointment_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_confirm_appointment(request, appointment_id):
    """Admin confirm an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='confirmation',
            appointment_id=appointment.id,
            title='Appointment Confirmed',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.',
            patient=appointment.patient
        )
        
        # Send SMS confirmation
        sms_result = send_appointment_sms(appointment, 'confirmation')
        if sms_result['success']:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed. SMS sent.')
        else:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed. (SMS failed)')
    else:
        messages.error(request, 'Only pending appointments can be confirmed.')
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_complete_appointment(request, appointment_id):
    """Admin mark appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
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
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_cancel_appointment(request, appointment_id):
    """Admin cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Appointment Cancelled',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled. Please contact us to reschedule.',
            patient=appointment.patient
        )
        
        # Send SMS cancellation notification
        sms_result = send_appointment_sms(appointment, 'cancellation')
        if sms_result['success']:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been cancelled. SMS sent.')
        else:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been cancelled. (SMS failed)')
    else:
        messages.error(request, 'Only pending or confirmed appointments can be cancelled.')
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_maintenance(request):
    """Admin maintenance page"""
    from services.models import Service
    from packages.models import Package
    from products.models import Product
    
    services_count = Service.objects.count()
    packages_count = Package.objects.count()
    products_count = Product.objects.count()
    
    # Get recent activity (example - you can expand this)
    recent_services = Service.objects.all().order_by('-id')[:5]
    
    context = {
        'services_count': services_count,
        'packages_count': packages_count,
        'products_count': products_count,
        'recent_services': recent_services,
    }
    
    return render(request, 'appointments/admin_maintenance.html', context)

@login_required
@user_passes_test(is_admin)
def admin_patients(request):
    """Admin patients management page"""
    from accounts.models import User
    
    # Get all patients (non-admin users)
    patients = User.objects.filter(user_type='patient').order_by('-id')
    
    # Get statistics for each patient
    patient_stats = []
    for patient in patients:
        appointments = Appointment.objects.filter(patient=patient)
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        
        # Count packages (you might need to adjust this based on your model)
        packages_count = appointments.filter(package__isnull=False).count()
        
        # Get last visit
        last_visit = appointments.filter(status='completed').order_by('-appointment_date').first()
        last_visit_date = last_visit.appointment_date if last_visit else None
        
        patient_stats.append({
            'patient': patient,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'packages_count': packages_count,
            'last_visit': last_visit_date,
        })
    
    context = {
        'patient_stats': patient_stats,
    }
    
    return render(request, 'appointments/admin_patients.html', context)

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    """Admin notifications management page"""
    notifications = Notification.objects.all().order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'appointments/admin_notifications.html', context)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings page"""
    from accounts.models import Attendant
    from .models import ClosedDay
    
    attendants = Attendant.objects.all()
    closed_days = ClosedDay.objects.all()
    
    # Create a list of hours for the schedule
    hours = ['10', '11', '12', '13', '14', '15', '16', '17', '18']
    
    context = {
        'attendants': attendants,
        'closed_days': closed_days,
        'hours': hours,
    }
    
    return render(request, 'appointments/admin_settings.html', context)

@login_required
@user_passes_test(is_admin)
def admin_add_attendant(request):
    """Add new attendant"""
    if request.method == 'POST':
        from accounts.models import Attendant
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        shift_date = request.POST.get('shift_date')
        shift_time = request.POST.get('shift_time')
        
        if first_name and last_name:
            try:
                # Create attendant
                Attendant.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    shift_date=shift_date if shift_date else None,
                    shift_time=shift_time if shift_time else None
                )
                
                messages.success(request, f'Attendant {first_name} {last_name} added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding attendant: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_delete_attendant(request, attendant_id):
    """Delete attendant"""
    from accounts.models import Attendant
    
    attendant = get_object_or_404(Attendant, id=attendant_id)
    attendant_name = f"{attendant.first_name} {attendant.last_name}"
    attendant.delete()
    
    messages.success(request, f'Attendant {attendant_name} deleted successfully.')
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_delete_notification(request, notification_id):
    """Delete notification"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    
    messages.success(request, 'Notification deleted successfully.')
    return redirect('appointments:admin_notifications')

@login_required
@user_passes_test(is_admin)
def admin_view_patient(request, patient_id):
    """View patient details"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    
    return render(request, 'appointments/admin_patient_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_edit_patient(request, patient_id):
    """Edit patient"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id)
    
    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name', patient.first_name)
        patient.last_name = request.POST.get('last_name', patient.last_name)
        patient.email = request.POST.get('email', patient.email)
        patient.phone = request.POST.get('phone', patient.phone)
        patient.full_name = f"{patient.first_name} {patient.last_name}"
        patient.save()
        
        messages.success(request, f'Patient {patient.full_name} updated successfully.')
        return redirect('appointments:admin_patients')
    
    context = {
        'patient': patient,
    }
    
    return render(request, 'appointments/admin_edit_patient.html', context)

@login_required
@user_passes_test(is_admin)
def admin_delete_patient(request, patient_id):
    """Delete patient"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id)
    patient_name = patient.full_name
    patient.delete()
    
    messages.success(request, f'Patient {patient_name} deleted successfully.')
    return redirect('appointments:admin_patients')

@login_required
@user_passes_test(is_admin)
def admin_add_closed_day(request):
    """Add closed day"""
    if request.method == 'POST':
        from .models import ClosedDay
        
        date = request.POST.get('start_date')
        reason = request.POST.get('reason')
        
        if date and reason:
            try:
                ClosedDay.objects.create(date=date, reason=reason)
                messages.success(request, f'Closed day {date} added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding closed day: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_delete_closed_day(request, closed_day_id):
    """Delete closed day"""
    from .models import ClosedDay
    
    closed_day = get_object_or_404(ClosedDay, id=closed_day_id)
    closed_day.delete()
    
    messages.success(request, 'Closed day deleted successfully.')
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_cancellation_requests(request):
    """Admin view for cancellation requests"""
    from .models import CancellationRequest
    
    cancellation_requests = CancellationRequest.objects.all().order_by('-created_at')
    
    context = {
        'cancellation_requests': cancellation_requests,
    }
    
    return render(request, 'appointments/admin_cancellation_requests.html', context)

@login_required
@user_passes_test(is_admin)
def admin_approve_cancellation(request, request_id):
    """Admin approve cancellation request"""
    from .models import CancellationRequest
    
    cancellation_request = get_object_or_404(CancellationRequest, id=request_id)
    appointment = get_object_or_404(Appointment, id=cancellation_request.appointment_id)
    
    if cancellation_request.status == 'pending':
        # Update cancellation request status
        cancellation_request.status = 'approved'
        cancellation_request.save()
        
        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Approved',
            message=f'Your cancellation request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been approved.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Cancellation request approved for {appointment.patient.full_name}.')
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')

@login_required
@user_passes_test(is_admin)
def admin_reject_cancellation(request, request_id):
    """Admin reject cancellation request"""
    from .models import CancellationRequest
    
    cancellation_request = get_object_or_404(CancellationRequest, id=request_id)
    appointment = get_object_or_404(Appointment, id=cancellation_request.appointment_id)
    
    if cancellation_request.status == 'pending':
        # Update cancellation request status
        cancellation_request.status = 'rejected'
        cancellation_request.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Request Rejected',
            message=f'Your cancellation request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been rejected. Please contact us for more information.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Cancellation request rejected for {appointment.patient.full_name}.')
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')


@login_required
@user_passes_test(is_admin)
def admin_manage_service_images(request):
    """Admin view to manage service images"""
    services = Service.objects.all().order_by('service_name')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            # Handle image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                alt_text = request.POST.get('alt_text', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # If this is set as primary, unset other primary images for this service
                if is_primary:
                    ServiceImage.objects.filter(service=service, is_primary=True).update(is_primary=False)
                
                ServiceImage.objects.create(
                    service=service,
                    image=image,
                    alt_text=alt_text,
                    is_primary=is_primary
                )
                messages.success(request, f'Image uploaded successfully for {service.service_name}')
            else:
                messages.error(request, 'Please select an image to upload')
    
    context = {
        'services': services,
    }
    return render(request, 'appointments/admin_manage_service_images.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_product_images(request):
    """Admin view to manage product images"""
    products = Product.objects.all().order_by('product_name')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            # Handle image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                alt_text = request.POST.get('alt_text', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # If this is set as primary, unset other primary images for this product
                if is_primary:
                    ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
                
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    alt_text=alt_text,
                    is_primary=is_primary
                )
                messages.success(request, f'Image uploaded successfully for {product.product_name}')
            else:
                messages.error(request, 'Please select an image to upload')
    
    context = {
        'products': products,
    }
    return render(request, 'appointments/admin_manage_product_images.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_service_image(request, image_id):
    """Delete a service image"""
    image = get_object_or_404(ServiceImage, id=image_id)
    service_name = image.service.service_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {service_name}')
    return redirect('appointments:admin_manage_service_images')


@login_required
@user_passes_test(is_admin)
def admin_delete_product_image(request, image_id):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_name = image.product.product_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {product_name}')
    return redirect('appointments:admin_manage_product_images')


@login_required
@user_passes_test(is_admin)
def admin_set_primary_service_image(request, image_id):
    """Set a service image as primary"""
    image = get_object_or_404(ServiceImage, id=image_id)
    # Unset other primary images for this service
    ServiceImage.objects.filter(service=image.service, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.service.service_name}')
    return redirect('appointments:admin_manage_service_images')


@login_required
@user_passes_test(is_admin)
def admin_set_primary_product_image(request, image_id):
    """Set a product image as primary"""
    image = get_object_or_404(ProductImage, id=image_id)
    # Unset other primary images for this product
    ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.product.product_name}')
    return redirect('appointments:admin_manage_product_images')


@login_required
@user_passes_test(is_admin)
def admin_inventory(request):
    """Staff inventory management for products"""
    products = Product.objects.all().order_by('product_name')
    
    # Get low stock products (stock < 10)
    low_stock_products = products.filter(stock__lt=10)
    
    # Get out of stock products
    out_of_stock_products = products.filter(stock=0)
    
    # Statistics
    total_products = products.count()
    total_stock_value = sum(p.price * p.stock for p in products)
    low_stock_count = low_stock_products.count()
    out_of_stock_count = out_of_stock_products.count()
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    
    return render(request, 'appointments/admin_inventory.html', context)


@login_required
@user_passes_test(is_admin)
def admin_update_stock(request, product_id):
    """Update product stock"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'add' or 'set'
        quantity = int(request.POST.get('quantity', 0))
        
        if action == 'add':
            product.stock += quantity
            messages.success(request, f'Added {quantity} units to {product.product_name}. New stock: {product.stock}')
        elif action == 'set':
            product.stock = quantity
            messages.success(request, f'Stock for {product.product_name} set to {quantity}')
        
        product.save()
        
        # Check if product is now available for pre-ordering
        if product.stock > 0 and product.stock < 10:
            messages.warning(request, f'{product.product_name} is running low on stock ({product.stock} units remaining).')
        
        return redirect('appointments:admin_inventory')
    
    return redirect('appointments:admin_inventory')
