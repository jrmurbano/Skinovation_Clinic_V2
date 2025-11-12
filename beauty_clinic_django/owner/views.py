from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
from accounts.models import User
from appointments.models import Appointment
from services.models import Service, ServiceImage, ServiceCategory
from products.models import Product, ProductImage
from packages.models import Package
from analytics.models import PatientAnalytics, ServiceAnalytics, BusinessAnalytics, TreatmentCorrelation, PatientSegment


def is_owner(user):
    """Check if user is owner"""
    return user.is_authenticated and user.user_type == 'owner'


@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    """Owner comprehensive dashboard with advanced analytics"""
    from analytics.services import AnalyticsService
    
    analytics_service = AnalyticsService()
    
    # Get comprehensive analytics data
    business_overview = analytics_service.get_business_overview()
    revenue_analytics = analytics_service.get_revenue_analytics()
    patient_analytics = analytics_service.get_patient_analytics()
    service_analytics = analytics_service.get_service_analytics()
    treatment_correlations = analytics_service.get_treatment_correlations()
    business_insights = analytics_service.get_business_insights()
    diagnostic_metrics = analytics_service.get_diagnostic_metrics()
    
    # Get notification count
    from appointments.models import Notification
    notification_count = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()
    
    context = {
        'business_overview': business_overview,
        'revenue_analytics': revenue_analytics,
        'patient_analytics': patient_analytics,
        'service_analytics': service_analytics,
        'treatment_correlations': treatment_correlations,
        'business_insights': business_insights,
        'diagnostic_metrics': diagnostic_metrics,
        'notification_count': notification_count,
    }
    
    return render(request, 'owner/dashboard.html', context)


@login_required
@user_passes_test(is_owner)
def owner_patients(request):
    """Owner patients overview"""
    # Get all patients with analytics
    patients = User.objects.filter(user_type='patient').prefetch_related('analytics', 'segments')
    
    # Calculate analytics for each patient
    patient_analytics_list = []
    for patient in patients:
        appointments = Appointment.objects.filter(patient=patient)
        analytics_data = {
            'patient': patient,
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(status='completed').count(),
            'cancelled_appointments': appointments.filter(status='cancelled').count(),
            'total_spent': sum([app.service.price for app in appointments.filter(status='completed') if app.service]),
            'last_visit': appointments.filter(status='completed').order_by('-appointment_date').first(),
            'segment': patient.segments.first().segment if patient.segments.exists() else 'unclassified',
        }
        patient_analytics_list.append(analytics_data)
    
    # Sort by total spent
    patient_analytics_list.sort(key=lambda x: x['total_spent'], reverse=True)
    
    # Get notification count
    from appointments.models import Notification
    notification_count = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()
    
    context = {
        'patient_analytics': patient_analytics_list,
        'notification_count': notification_count,
    }
    
    return render(request, 'owner/patients.html', context)


@login_required
@user_passes_test(is_owner)
def owner_appointments(request):
    """Owner appointments overview"""
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
    
    return render(request, 'owner/appointments.html', context)


@login_required
@user_passes_test(is_owner)
def owner_services(request):
    """Owner services overview"""
    services = Service.objects.annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        cancelled_bookings=Count('appointments', filter=Q(appointments__status='cancelled')),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed')),
        avg_rating=Avg('appointments__feedback__rating', filter=Q(appointments__feedback__isnull=False))
    ).order_by('-total_revenue')
    
    context = {
        'services': services,
    }
    
    return render(request, 'owner/services.html', context)


@login_required
@user_passes_test(is_owner)
def owner_packages(request):
    """Owner packages overview"""
    packages = Package.objects.annotate(
        total_bookings=Count('package_bookings'),
        total_revenue=Sum('package_bookings__price'),
        avg_rating=Avg('package_bookings__feedback__rating', filter=Q(package_bookings__feedback__isnull=False))
    ).order_by('-total_revenue')
    
    context = {
        'packages': packages,
    }
    
    return render(request, 'owner/packages.html', context)


@login_required
@user_passes_test(is_owner)
def owner_products(request):
    """Owner products overview"""
    products = Product.objects.annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        total_revenue=Sum('appointments__product__price', filter=Q(appointments__status='completed'))
    ).order_by('-total_revenue')
    
    context = {
        'products': products,
    }
    
    return render(request, 'owner/products.html', context)


@login_required
@user_passes_test(is_owner)
def owner_analytics(request):
    """Owner comprehensive analytics dashboard"""
    from analytics.services import AnalyticsService
    
    analytics_service = AnalyticsService()
    
    # Get comprehensive analytics data
    business_overview = analytics_service.get_business_overview()
    revenue_analytics = analytics_service.get_revenue_analytics()
    patient_analytics = analytics_service.get_patient_analytics()
    service_analytics = analytics_service.get_service_analytics()
    treatment_correlations = analytics_service.get_treatment_correlations()
    business_insights = analytics_service.get_business_insights()
    diagnostic_metrics = analytics_service.get_diagnostic_metrics()
    
    # Get filter parameters
    date_range = request.GET.get('date_range', '30')
    view_type = request.GET.get('view_type', 'overview')
    
    # Adjust date ranges based on filter
    if date_range == '7':
        days = 7
    elif date_range == '90':
        days = 90
    elif date_range == '365':
        days = 365
    else:
        days = 30
    
    context = {
        'business_overview': business_overview,
        'revenue_analytics': revenue_analytics,
        'patient_analytics': patient_analytics,
        'service_analytics': service_analytics,
        'treatment_correlations': treatment_correlations,
        'business_insights': business_insights,
        'diagnostic_metrics': diagnostic_metrics,
        'date_range': date_range,
        'view_type': view_type,
        'days': days,
    }
    
    return render(request, 'owner/analytics.html', context)


# Owner Management Functions

@login_required
@user_passes_test(is_owner)
def owner_manage_services(request):
    """Owner manage services"""
    services = Service.objects.all().order_by('service_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            service_name = request.POST.get('service_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            duration = request.POST.get('duration')
            category_id = request.POST.get('category')
            
            if service_name and price and duration:
                try:
                    Service.objects.create(
                        service_name=service_name,
                        description=description,
                        price=price,
                        duration=duration,
                        category_id=category_id
                    )
                    messages.success(request, 'Service added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding service: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            service.service_name = request.POST.get('service_name', service.service_name)
            service.description = request.POST.get('description', service.description)
            price = request.POST.get('price')
            if price:
                service.price = price
            duration = request.POST.get('duration')
            if duration:
                service.duration = duration
            category_id = request.POST.get('category')
            if category_id:
                service.category_id = category_id
            service.save()
            messages.success(request, 'Service updated successfully!')
        
        elif action == 'delete':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            service.delete()
            messages.success(request, 'Service deleted successfully!')
        
        return redirect('owner:manage_services')
    
    categories = ServiceCategory.objects.all()
    context = {
        'services': services,
        'categories': categories,
    }
    return render(request, 'owner/manage_services.html', context)


@login_required
@user_passes_test(is_owner)
def owner_manage_packages(request):
    """Owner manage packages"""
    packages = Package.objects.all().order_by('package_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            package_name = request.POST.get('package_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            sessions = request.POST.get('sessions')
            duration_days = request.POST.get('duration_days')
            grace_period_days = request.POST.get('grace_period_days')
            
            if package_name and price and sessions:
                try:
                    Package.objects.create(
                        package_name=package_name,
                        description=description,
                        price=price,
                        sessions=sessions,
                        duration_days=duration_days or 0,
                        grace_period_days=grace_period_days or 0
                    )
                    messages.success(request, 'Package added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding package: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            package_id = request.POST.get('package_id')
            package = get_object_or_404(Package, id=package_id)
            package.package_name = request.POST.get('package_name', package.package_name)
            package.description = request.POST.get('description', package.description)
            price = request.POST.get('price')
            if price:
                package.price = price
            sessions = request.POST.get('sessions')
            if sessions:
                package.sessions = sessions
            duration_days = request.POST.get('duration_days')
            if duration_days:
                package.duration_days = duration_days
            grace_period_days = request.POST.get('grace_period_days')
            if grace_period_days:
                package.grace_period_days = grace_period_days
            package.save()
            messages.success(request, 'Package updated successfully!')
        
        elif action == 'delete':
            package_id = request.POST.get('package_id')
            package = get_object_or_404(Package, id=package_id)
            package.delete()
            messages.success(request, 'Package deleted successfully!')
        
        return redirect('owner:manage_packages')
    
    context = {
        'packages': packages,
    }
    return render(request, 'owner/manage_packages.html', context)


@login_required
@user_passes_test(is_owner)
def owner_manage_products(request):
    """Owner manage products"""
    products = Product.objects.all().order_by('product_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock') or request.POST.get('stock_quantity')
            
            if product_name and price:
                try:
                    Product.objects.create(
                        product_name=product_name,
                        description=description,
                        price=price,
                        stock=stock or 0
                    )
                    messages.success(request, 'Product added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding product: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.product_name = request.POST.get('product_name', product.product_name)
            product.description = request.POST.get('description', product.description)
            price = request.POST.get('price')
            if price:
                product.price = price
            stock = request.POST.get('stock') or request.POST.get('stock_quantity')
            if stock is not None:
                product.stock = stock
            product.save()
            messages.success(request, 'Product updated successfully!')
        
        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        
        return redirect('owner:manage_products')
    
    context = {
        'products': products,
    }
    return render(request, 'owner/manage_products.html', context)


@login_required
@user_passes_test(is_owner)
def owner_manage_patient_profiles(request):
    """Owner manage patient profiles"""
    patients = User.objects.filter(user_type='patient').order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit':
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id, user_type='patient')
            patient.first_name = request.POST.get('first_name', patient.first_name)
            patient.last_name = request.POST.get('last_name', patient.last_name)
            patient.email = request.POST.get('email', patient.email)
            patient.phone = request.POST.get('phone', patient.phone)
            patient.address = request.POST.get('address', patient.address)
            patient.gender = request.POST.get('gender', patient.gender)
            patient.civil_status = request.POST.get('civil_status', patient.civil_status)
            patient.birthday = request.POST.get('birthday', patient.birthday)
            patient.occupation = request.POST.get('occupation', patient.occupation)
            patient.save()
            messages.success(request, 'Patient profile updated successfully!')
        
        elif action == 'delete':
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id, user_type='patient')
            patient.delete()
            messages.success(request, 'Patient deleted successfully!')
        
        return redirect('owner:manage_patient_profiles')
    
    context = {
        'patients': patients,
    }
    return render(request, 'owner/manage_patient_profiles.html', context)


@login_required
@user_passes_test(is_owner)
def owner_view_history_log(request):
    """Owner view history log"""
    from services.models import HistoryLog
    
    history_logs = HistoryLog.objects.all().order_by('-datetime')
    
    context = {
        'history_logs': history_logs,
    }
    return render(request, 'owner/history_log.html', context)


@login_required
@user_passes_test(is_owner)
def owner_manage_service_images(request):
    """Owner view to manage service images"""
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
    return render(request, 'owner/manage_service_images.html', context)


@login_required
@user_passes_test(is_owner)
def owner_manage_product_images(request):
    """Owner view to manage product images"""
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
    return render(request, 'owner/manage_product_images.html', context)


@login_required
@user_passes_test(is_owner)
def owner_delete_service_image(request, image_id):
    """Delete a service image"""
    image = get_object_or_404(ServiceImage, id=image_id)
    service_name = image.service.service_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {service_name}')
    return redirect('owner:manage_service_images')


@login_required
@user_passes_test(is_owner)
def owner_delete_product_image(request, image_id):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_name = image.product.product_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {product_name}')
    return redirect('owner:manage_product_images')


@login_required
@user_passes_test(is_owner)
def owner_set_primary_service_image(request, image_id):
    """Set a service image as primary"""
    image = get_object_or_404(ServiceImage, id=image_id)
    # Unset other primary images for this service
    ServiceImage.objects.filter(service=image.service, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.service.service_name}')
    return redirect('owner:manage_service_images')


@login_required
@user_passes_test(is_owner)
def owner_set_primary_product_image(request, image_id):
    """Set a product image as primary"""
    image = get_object_or_404(ProductImage, id=image_id)
    # Unset other primary images for this product
    ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.product.product_name}')
    return redirect('owner:manage_product_images')
