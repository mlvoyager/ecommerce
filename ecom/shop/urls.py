from django.urls import path

from shop.views import (
    index,
    detail,
    cart_view,
    checkout,
    app_evaluation,
    categories_view,
    admin_dashboard,
    
)


urlpatterns = [
    path('', index, name='home'),
    path('<int:myid>/', detail, name="detail"),
    path('panier/', cart_view, name="cart"),
    path('commande/', checkout, name="checkout"),
    path('evaluation/', app_evaluation, name="app_evaluation"),
    
    path('categories/', categories_view, name="categories"),
    path('admin-dashboard/', admin_dashboard, name="admin_dashboard"),
    
]
