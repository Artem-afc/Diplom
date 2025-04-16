from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.district_list, name='district_list'),
    path('district/<int:pk>/', views.district_detail, name='district_detail'),
    path('building/<int:pk>/', views.building_detail, name='building_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('mortgage_calculator/', views.mortgage_calculator, name='mortgage_calculator'),
    path('search/', views.apartment_search, name='apartment_search'),
    path('apartment/<int:pk>/purchase/', views.purchase_confirmation, name='purchase_confirmation'),
    path('login/', views.user_login, name='user_login'),
    path('apartment/<int:pk>/resell/', views.resell_apartment, name='resell_apartment'),
    path('apartment/<int:pk>/', views.apartment_detail, name='apartment_detail'),
    path('trade-in/', views.trade_in_view, name='trade_in'),
    path('infrastructure/', views.infrastructure, name='infrastructure'),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)