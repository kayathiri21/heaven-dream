
from django.urls import path
from app import views
app_name='app'
urlpatterns = [
    path('',views.index,name="index"),
    path('categories/', views.category, name='category'),
    path('product/', views.featureproduct, name='allproduct'),
    path('categories/<int:category_id>/', views.product_list, name='product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
   
    path('cart/', views.cart, name='cart'),
    path('cart/<int:cart_item_id>/remove_cart/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),

    
    path('success/', views.success, name='success'),
    
    path('cancel/', views.cancel, name='cancel'),
]