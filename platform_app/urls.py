from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gigs/', views.gig_list, name='gig_list'),
    path('gigs/category/<slug:category_slug>/', views.gig_list, name='gig_list_by_category'),
    path('gigs/<int:pk>/', views.gig_detail, name='gig_detail'),
    path('gigs/create/', views.create_gig, name='create_gig'),
    path('gigs/<int:gig_id>/order/', views.create_order, name='create_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/message/', views.send_message, name='send_message'),
    path('orders/<int:pk>/update/<str:status>/', views.update_order_status, name='update_order_status'),
    path('my-gigs/', views.my_gigs, name='my_gigs'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:gig_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('gigs/<int:pk>/edit/', views.edit_gig, name='edit_gig'),
    # API Endpoints
    path('api/gigs/', views.api_gig_list, name='api_gig_list'),
    path('api/categories/', views.api_category_list, name='api_category_list'),
]
