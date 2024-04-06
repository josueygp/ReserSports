"""
URL configuration for ReservacionDeportiva project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import  path
from Reservacion import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),

     path('generate-pdf/<int:reservation_id>/', views.generate_reservation_pdf, name='generate_reservation_pdf'),

    path('logout/',views.signout, name='logout'),
    path('signin/',views.signin, name='signin'),
    path('signup/',views.signup, name='signup'),

    path('catalogue/', views.SportZonesListView.as_view(), name='catalogue'),
    path('catalogue/<int:catalogue_id>/', views.catalogue_detail, name='cataloguedetail'),
    path('reception/',views.reception, name='reception'),
    path('reservation/',views.ReservationsListView.as_view(), name='reservation'),


    path('reservation/edit/<int:reservation_id>/',views.reservation_edit, name='reservationedit'),
    path('reservation/create/',views.reservation_create , name='reservationcreate'),
    path('reservation/delete/<int:client_id>/', views.client_delete, name='client_delete'),

    path('reservation/cancelar/<int:reservation_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservation/activar/<int:reservation_id>/', views.activar_reserva, name='activar_reserva'),
    path('reservation/finalizar/<int:reservation_id>/', views.finalizar_reserva, name='finalizar_reserva'),

    path('get_available_times/', views.get_available_times_ajax, name='get_available_times'),

    path('client/',views.client, name='client'),
    path('client/search/',views.client, name='client_search'),
    path('client/<int:client_id>/', views.client_detail, name='client_detail'),
    path('client/create/', views.create_client, name='create_client'),
    path('client/edit/<int:client_id>/', views.client_edit, name='clientedit'),
    path('client/delete/<int:client_id>/', views.client_delete, name='client_delete'),

    path('statistics/', views.reservation_statistics, name='reservation_statistics'),

    path('calendar/', views.calendar_view, name='calendar'),

    path('reservation/quickreservation/<int:sportzone_id>/',views.quick_reservation , name='quick_reservation'),

    path('sportzonelist/',views.SportZonesListFreeView.as_view() , name='sportzone_list_free'),

    path('sportzonelist_reserved/',views.sportzone_list_reserved , name='sportzone_list_reserved'),



    
    ]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

