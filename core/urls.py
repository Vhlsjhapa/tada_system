from django.contrib import admin
from django.urls import path
from travel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication (प्रमाणीकरण)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('set-active-fy/', views.set_active_fiscal_year, name='set_active_fiscal_year'),
    
    # Dashboard (ड्यासबोर्ड)
    path('', views.dashboard, name='dashboard'),
    
    # Employee Management (कर्मचारी व्यवस्थापन - Admin Only)
    path('employees/', views.manage_employees, name='manage_employees'),
    
    # User Management (प्रयोगकर्ता व्यवस्थापन - Admin Only)
    path('users/', views.manage_users, name='manage_users'),
    
    # Office & System Data Management (Admin Only)
    path('offices/', views.manage_offices, name='manage_offices'),
    path('offices/set-default/<int:pk>/', views.set_default_office, name='set_default_office'),
    path('reset-all-records/', views.reset_all_records_view, name='reset_all_records'),
    path('reset-now/', views.reset_now_direct, name='reset_now_direct'),
    
    # PDF / Print & Delete Views (म.ले.प. फारामहरू)
    path('order/<int:pk>/', views.travel_order_pdf, name='travel_order_pdf'),
    path('order/<int:pk>/delete/', views.delete_order_view, name='delete_order'),
    path('bill/<int:pk>/', views.travel_bill_pdf, name='travel_bill_pdf'),
    path('bill/<int:pk>/delete/', views.delete_bill_view, name='delete_bill'),
    path('report/<int:pk>/', views.travel_report_pdf, name='travel_report_pdf'),
    path('report/<int:pk>/delete/', views.delete_report_view, name='delete_report'),
    
    # Travel Record Register (भ्रमण अभिलेख खाता - Landscape Mode)
    path('register/', views.travel_register_view, name='travel_register'),
    path('travel-register/', views.travel_register_view, name='travel_register_alias'),
    path('ledger/', views.travel_register_view, name='travel_ledger_alias'),
    
    # Automated Application Letters (आधिकारिक निवेदनहरू)
    path('order/<int:pk>/nivedan/', views.order_nivedan, name='order_nivedan'),
    path('bill/<int:pk>/nivedan/', views.bill_nivedan, name='bill_nivedan'),
    
    # Web Forms (फारामहरू)
    path('order/new/', views.order_form_view, name='create_order'),
    path('order/<int:pk>/edit/', views.edit_order_view, name='edit_order'),
    path('order/<int:pk>/action/<str:action>/', views.order_workflow_action, name='order_workflow_action'),
    path('bill/new/', views.bill_form_view, name='create_bill'),
    path('report/new/', views.report_form_view, name='create_report'),
    
    # JSON APIs for Auto-fill
    path('api/employee/<int:pk>/', views.api_employee_detail, name='api_employee_detail'),
    path('api/order/<int:pk>/', views.api_order_detail, name='api_order_detail'),
    path('api/next-order-number/', views.api_next_order_number, name='api_next_order_number'),
]

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
]