// Get base path for API calls
const basePath = window.location.pathname.includes('/admin/') ? '../' :
    window.location.pathname.includes('/patient/') ? '../' :
    window.location.pathname.includes('/attendant/') ? '' : '';

// Notification sound - handle missing file gracefully
let notificationSound = null;
try {
    notificationSound = new Audio('/static/assets/sounds/notification.wav');
    notificationSound.onerror = function() {
        console.log('Notification sound file not found, sound disabled');
        notificationSound = null;
    };
} catch (error) {
    console.log('Could not load notification sound:', error);
    notificationSound = null;
}

// Function to update notification count
function updateNotificationCount(count) {
    const countElement = document.querySelector('.notification-count, .admin-notification-count');
    if (countElement) {
        const oldCount = parseInt(countElement.textContent);
        countElement.textContent = count;
        countElement.style.display = count > 0 ? 'block' : 'none';

        // Play sound if there are new notifications
        if (count > oldCount && notificationSound) {
            notificationSound.play().catch(error => {
                console.log('Error playing notification sound:', error);
            });
        }
    }
}

// Function to format notification item
function formatNotification(notification) {
    const isRead = notification.is_read ? 'bg-light' : 'bg-info bg-opacity-10';
    return `
        <div class="notification-item p-2 border-bottom ${isRead}" data-id="${notification.notification_id}">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <strong>${notification.title}</strong>
                <small class="text-muted">${notification.created_at_formatted}</small>
            </div>
            <p class="mb-0 text-muted">${notification.message}</p>
            ${!notification.is_read ? `
                <button class="btn btn-sm btn-link mark-read-btn p-0 mt-1" data-id="${notification.notification_id}">
                    Mark as Read
                </button>
            ` : ''}
        </div>
    `;
}

// Function to fetch and update notifications
function fetchNotifications() {
    // Determine the correct API endpoint based on current page
    let apiUrl = '/notifications/get_notifications.php';  // Global endpoint
    
    if (window.location.pathname.includes('/attendant/')) {
        apiUrl = basePath + 'api/notifications/';
    } else if (window.location.pathname.includes('/appointments/')) {
        apiUrl = basePath + 'appointments/notifications/get_notifications.php';
    }
    
    // Skip notification fetching if we're on login pages or password reset pages
    if (window.location.pathname.includes('/login/') || 
        window.location.pathname.includes('/password-reset/') ||
        window.location.pathname.includes('/register/')) {
        return;
    }
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateNotificationCount(data.unread_count);
                
                const notificationsList = document.querySelector('.notifications-list, .admin-notifications-list');
                if (notificationsList) {
                    if (data.notifications.length === 0) {
                        notificationsList.innerHTML = '<div class="p-3 text-center text-muted">No notifications</div>';
                    } else {
                        notificationsList.innerHTML = data.notifications.map(formatNotification).join('');
                        
                        // Add click handlers for mark as read buttons
                        notificationsList.querySelectorAll('.mark-read-btn').forEach(btn => {
                            btn.addEventListener('click', function(e) {
                                e.preventDefault();
                                markAsRead(this.dataset.id);
                            });
                        });
                    }
                }
            }
        })
        .catch(error => {
            // Only log errors if we're not on login/password reset pages
            if (!window.location.pathname.includes('/login/') && 
                !window.location.pathname.includes('/password-reset/') &&
                !window.location.pathname.includes('/register/')) {
                console.error('Error fetching notifications:', error);
            }
        });
}

// Function to mark a notification as read
function markAsRead(notificationId) {
    let apiUrl = '/notifications/update_notifications.php';  // Global endpoint
    
    if (window.location.pathname.includes('/attendant/')) {
        apiUrl = basePath + 'api/notifications/update/';
    } else if (window.location.pathname.includes('/appointments/')) {
        apiUrl = basePath + 'appointments/notifications/update_notifications.php';
    }
    
    const requestData = {
        action: 'mark_read',
        notification_id: notificationId
    };
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications();
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

// Function to mark all notifications as read
function markAllAsRead() {
    let apiUrl = '/notifications/update_notifications.php';  // Global endpoint
    
    if (window.location.pathname.includes('/attendant/')) {
        apiUrl = basePath + 'api/notifications/update/';
    } else if (window.location.pathname.includes('/appointments/')) {
        apiUrl = basePath + 'appointments/notifications/update_notifications.php';
    }
    
    const requestData = {
        action: 'mark_all_read'
    };
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications();
        }
    })
    .catch(error => console.error('Error marking all notifications as read:', error));
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize notifications
document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch
    fetchNotifications();
    
    // Set up periodic updates
    setInterval(fetchNotifications, 30000); // Check every 30 seconds
    
    // Add click handler for mark all as read button
    const markAllReadBtn = document.querySelector('.mark-all-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllAsRead);
    }
});