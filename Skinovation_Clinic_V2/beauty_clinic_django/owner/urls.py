from django.urls import path
from . import views
from . import sms_views

app_name = 'owner'

urlpatterns = [
    path('', views.owner_dashboard, name='dashboard'),
    path('patients/', views.owner_patients, name='patients'),
    path('appointments/', views.owner_appointments, name='appointments'),
    path('services/', views.owner_services, name='services'),
    path('packages/', views.owner_packages, name='packages'),
    path('products/', views.owner_products, name='products'),
    path('analytics/', views.owner_analytics, name='analytics'),
    # Management functions
    path('manage/services/', views.owner_manage_services, name='manage_services'),
    path('manage/packages/', views.owner_manage_packages, name='manage_packages'),
    path('manage/products/', views.owner_manage_products, name='manage_products'),
    path('manage/patient-profiles/', views.owner_manage_patient_profiles, name='manage_patient_profiles'),
    path('history-log/', views.owner_view_history_log, name='history_log'),
    path('inventory/', views.owner_view_inventory, name='view_inventory'),
    
    # Image Management URLs
    path('manage/service-images/', views.owner_manage_service_images, name='manage_service_images'),
    path('manage/product-images/', views.owner_manage_product_images, name='manage_product_images'),
    path('delete-service-image/<int:image_id>/', views.owner_delete_service_image, name='delete_service_image'),
    path('delete-product-image/<int:image_id>/', views.owner_delete_product_image, name='delete_product_image'),
    path('set-primary-service-image/<int:image_id>/', views.owner_set_primary_service_image, name='set_primary_service_image'),
    path('set-primary-product-image/<int:image_id>/', views.owner_set_primary_product_image, name='set_primary_product_image'),
    
    # SMS functionality
    path('sms-test/', sms_views.sms_test, name='sms_test'),
    path('send-test-sms/', sms_views.send_test_sms, name='send_test_sms'),
    
    # Attendant Management
    path('manage/attendants/', views.owner_manage_attendants, name='manage_attendants'),
    path('manage/attendants/create-user/', views.owner_create_attendant_user, name='create_attendant_user'),
    path('manage/attendants/edit-user/<int:user_id>/', views.owner_edit_attendant_user, name='edit_attendant_user'),
    path('manage/attendants/toggle-user/<int:user_id>/', views.owner_toggle_attendant_user, name='toggle_attendant_user'),
    path('manage/attendants/reset-password/<int:user_id>/', views.owner_reset_attendant_password, name='reset_attendant_password'),
    path('manage/attendants/profile/<int:user_id>/', views.owner_manage_attendant_profile, name='manage_attendant_profile'),
    path('manage/attendants/add/', views.owner_add_attendant, name='add_attendant'),
    path('manage/attendants/delete/<int:attendant_id>/', views.owner_delete_attendant, name='delete_attendant'),
]
