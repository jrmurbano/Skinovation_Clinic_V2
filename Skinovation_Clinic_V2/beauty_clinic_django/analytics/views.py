from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
from .models import PatientAnalytics, ServiceAnalytics, BusinessAnalytics, TreatmentCorrelation, PatientSegment
from accounts.models import User
from appointments.models import Appointment
from services.models import Service
from products.models import Product
from packages.models import Package


def is_owner_or_admin(user):
    """Check if user is owner or admin"""
    return user.is_authenticated and user.user_type in ['owner', 'admin']


@login_required
@user_passes_test(is_owner_or_admin)
def analytics_dashboard(request):
    """Comprehensive analytics dashboard"""
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # Basic statistics
    total_patients = User.objects.filter(user_type='patient').count()
    total_appointments = Appointment.objects.count()
    total_revenue = Appointment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('service__price'))['total'] or 0
    
    # Recent activity
    recent_appointments = Appointment.objects.filter(
        appointment_date__gte=last_30_days
    ).order_by('-appointment_date')[:10]
    
    # Patient analytics
    patient_stats = {
        'new_patients_30_days': User.objects.filter(
            user_type='patient',
            created_at__gte=last_30_days
        ).count(),
        'active_patients': User.objects.filter(
            user_type='patient',
            appointments__appointment_date__gte=last_30_days
        ).distinct().count(),
        'at_risk_patients': PatientSegment.objects.filter(segment='at_risk').count(),
    }
    
    # Service popularity
    popular_services = Service.objects.annotate(
        booking_count=Count('appointments')
    ).order_by('-booking_count')[:5]
    
    # Monthly trends
    monthly_appointments = Appointment.objects.filter(
        appointment_date__gte=last_90_days
    ).extra(
        select={'month': "strftime('%%Y-%%m', appointment_date)"}
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('service__price')
    ).order_by('month')
    
    # Treatment correlations
    correlations = TreatmentCorrelation.objects.filter(
        correlation_strength__gte=0.5
    ).order_by('-correlation_strength')[:10]
    
    # Patient segments
    segments = PatientSegment.objects.values('segment').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'patient_stats': patient_stats,
        'popular_services': popular_services,
        'monthly_appointments': monthly_appointments,
        'correlations': correlations,
        'segments': segments,
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def patient_analytics(request):
    """Detailed patient analytics"""
    # Get filter parameters
    segment_filter = request.GET.get('segment', '')
    search_query = request.GET.get('search', '')
    
    # Get patients with analytics
    patients = User.objects.filter(user_type='patient').prefetch_related('analytics')
    
    # Apply filters
    if segment_filter:
        patients = patients.filter(segments__segment=segment_filter)
    
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
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
    
    context = {
        'patient_analytics': patient_analytics_list,
        'segment_filter': segment_filter,
        'search_query': search_query,
    }
    
    return render(request, 'analytics/patient_analytics.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def service_analytics(request):
    """Service performance analytics"""
    # Service performance metrics
    services = Service.objects.annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        cancelled_bookings=Count('appointments', filter=Q(appointments__status='cancelled')),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed')),
        avg_rating=Avg('appointments__feedback__rating', filter=Q(appointments__feedback__isnull=False))
    ).order_by('-total_bookings')
    
    # Service categories performance
    category_stats = Service.objects.values('category__name').annotate(
        service_count=Count('id'),
        total_bookings=Count('appointments'),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed'))
    ).order_by('-total_revenue')
    
    # Seasonal trends
    seasonal_data = Appointment.objects.filter(
        appointment_date__gte=timezone.now().date() - timedelta(days=365)
    ).extra(
        select={'month': "strftime('%%m', appointment_date)"}
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('service__price')
    ).order_by('month')
    
    context = {
        'services': services,
        'category_stats': category_stats,
        'seasonal_data': seasonal_data,
    }
    
    return render(request, 'analytics/service_analytics.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def treatment_correlations(request):
    """Treatment correlation analysis"""
    correlations = TreatmentCorrelation.objects.select_related(
        'primary_service', 'secondary_service'
    ).order_by('-correlation_strength')
    
    # Filter by strength
    min_strength = request.GET.get('min_strength', 0.3)
    correlations = correlations.filter(correlation_strength__gte=min_strength)
    
    context = {
        'correlations': correlations,
        'min_strength': min_strength,
    }
    
    return render(request, 'analytics/treatment_correlations.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def business_insights(request):
    """Business insights and recommendations"""
    # Calculate key metrics
    total_patients = User.objects.filter(user_type='patient').count()
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancellation_rate = (Appointment.objects.filter(status='cancelled').count() / total_appointments * 100) if total_appointments > 0 else 0
    
    # Revenue trends
    revenue_trend = Appointment.objects.filter(
        status='completed',
        appointment_date__gte=timezone.now().date() - timedelta(days=90)
    ).extra(
        select={'week': "strftime('%%Y-%%W', appointment_date)"}
    ).values('week').annotate(
        revenue=Sum('service__price')
    ).order_by('week')
    
    # Patient retention
    retention_data = []
    for i in range(1, 13):  # Last 12 months
        month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        new_patients = User.objects.filter(
            user_type='patient',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        returning_patients = User.objects.filter(
            user_type='patient',
            appointments__appointment_date__gte=month_start,
            appointments__appointment_date__lt=month_end
        ).distinct().count()
        
        retention_data.append({
            'month': month_start.strftime('%Y-%m'),
            'new_patients': new_patients,
            'returning_patients': returning_patients,
            'retention_rate': (returning_patients / new_patients * 100) if new_patients > 0 else 0
        })
    
    # Generate insights
    insights = []
    
    if cancellation_rate > 20:
        insights.append({
            'type': 'warning',
            'title': 'High Cancellation Rate',
            'message': f'Your cancellation rate is {cancellation_rate:.1f}%. Consider improving appointment reminders and customer service.',
        })
    
    if completed_appointments < total_appointments * 0.7:
        insights.append({
            'type': 'info',
            'title': 'Appointment Completion Rate',
            'message': f'Your completion rate is {(completed_appointments/total_appointments*100):.1f}%. Focus on reducing cancellations.',
        })
    
    # Top performing services
    top_services = Service.objects.annotate(
        booking_count=Count('appointments', filter=Q(appointments__status='completed'))
    ).order_by('-booking_count')[:3]
    
    if top_services:
        insights.append({
            'type': 'success',
            'title': 'Top Performing Services',
            'message': f'Your most popular services are: {", ".join([s.service_name for s in top_services])}. Consider promoting these further.',
        })
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancellation_rate': cancellation_rate,
        'revenue_trend': revenue_trend,
        'retention_data': retention_data,
        'insights': insights,
    }
    
    return render(request, 'analytics/business_insights.html', context)
