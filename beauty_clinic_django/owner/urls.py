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
]
