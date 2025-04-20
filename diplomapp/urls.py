from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', views.district_list, name='district_list'),
    path('district/<int:pk>/', views.district_detail, name='district_detail'),
    path('building/<int:pk>/', views.building_detail, name='building_detail'),
    path('apartment/<int:pk>/', views.apartment_detail, name='apartment_detail'),
    path('apartment/<int:pk>/purchase/', views.purchase_confirmation, name='purchase_confirmation'),
    path('purchase/success/<int:apartment_pk>/', views.purchase_success, name='purchase_success'),
    path('apartment/<int:pk>/resell/', views.resell_apartment, name='resell_apartment'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('trade-in/', views.trade_in_view, name='trade_in'),
    path('infrastructure/', views.infrastructure, name='infrastructure'),
    path('search/', views.apartment_search, name='apartment_search'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('accounts/login/', LoginView.as_view(template_name='diplomapp/login.html'), name='login'),
    path('subscribe/success/', views.subscribe_success, name='subscribe_success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)