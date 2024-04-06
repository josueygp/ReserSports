from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (Countries, States, Cities, Infrastructures, Sports, Facilities, ReservationStatus,
                     SportCenters, SportZones, Clients, Reservations, SportCentersPhotos, SportZonesPhotos)

# Register your models here.
class ReservationsAdmin(ImportExportModelAdmin):
    list_display = ('id_reservations', 'id_sportzones', 'id_reservationstatus', 'id_admistrators', 'id_clients', 'started', 'finished','creation_date')
    search_fields = ('id_reservations', 'id_clients__first_name', 'id_clients__last_name')
    list_filter=('id_sportzones','id_reservationstatus','started', 'creation_date')
    date_hierarchy="started"
######
class ClientsAdmin(ImportExportModelAdmin):
    list_display=("first_name","last_name",'birth_date','email','contact_number','creation_date')
    search_fields=("first_name","last_name")
    date_hierarchy="creation_date"
#######
class SportZonesAdmin(ImportExportModelAdmin):
    list_display = ('id_sportzones', 'name', 'id_sportcenters', 'id_facilities', 'id_sports', 'id_infrastructures', 'capacity','section')
    search_fields=('name',)
    list_filter=('id_sports', 'id_facilities','id_infrastructures')
#######
class SportCentersAdmin(ImportExportModelAdmin):
    list_display = ('id_sportcenters', 'name', 'id_cities')
    search_fields=('name',)
    list_filter=('id_cities',)
#######
class CountriesAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######

class StatesAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######

class CitiesAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######
    
class InfrastructuresAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######
    
class SportsAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######
    
class facilitiesAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######
    
class reservationsAdmin(ImportExportModelAdmin):
    list_display=('name',)
    search_fields=('name',)
######
    


admin.site.register(Countries,CountriesAdmin)
admin.site.register(States,StatesAdmin)
admin.site.register(Cities,CitiesAdmin)
admin.site.register(Infrastructures,InfrastructuresAdmin)
admin.site.register(Sports,SportsAdmin)
admin.site.register(Facilities,facilitiesAdmin)
admin.site.register(ReservationStatus,reservationsAdmin)
admin.site.register(SportCenters,SportCentersAdmin)
admin.site.register(SportZones,SportZonesAdmin)
admin.site.register(Clients,ClientsAdmin)
admin.site.register(Reservations, ReservationsAdmin)
admin.site.register(SportCentersPhotos)
admin.site.register(SportZonesPhotos)
