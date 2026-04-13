
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('book/<int:product_id>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/<str:action>/', views.booking_action, name='booking_action'),
    path('booking/<int:booking_id>/complete/', views.complete_booking, name='complete_booking'),
]
