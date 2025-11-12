from .models import Notification


def notification_count(request):
    """Add notification count to all templates"""
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            # For admin, show all notifications
            count = Notification.objects.filter(patient__isnull=True).count()
        else:
            # For patients, show their notifications
            count = Notification.objects.filter(patient=request.user, is_read=False).count()
    else:
        count = 0
    
    return {
        'notification_count': count
    }


