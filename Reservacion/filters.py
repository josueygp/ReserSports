import django_filters
from .models import SportCenters, SportZones, SportZonesPhotos, Reservations,Clients, ReservationStatus, Infrastructures, Sports, Facilities


from django.db.models import Q

class SportZonesFilter(django_filters.FilterSet):
    facilities = django_filters.ModelChoiceFilter(
        queryset=Facilities.objects.filter(
            id_facilities__in=SportZones.objects.values_list('id_facilities', flat=True)
        ),
        field_name='id_facilities__name',
        to_field_name='pk',
        label='Instalación'
    )
    sports = django_filters.ModelChoiceFilter(
        queryset=Sports.objects.filter(
            id_sports__in=SportZones.objects.values_list('id_sports', flat=True)
        ),
        field_name='id_sports__name',
        to_field_name='pk',
        label='Deporte'
    )
    infrastructures = django_filters.ModelChoiceFilter(
        queryset=Infrastructures.objects.filter(
            id_infrastructures__in=SportZones.objects.values_list('id_infrastructures', flat=True)
        ),
        field_name='id_infrastructures__name',
        to_field_name='pk',
        label='Infraestructura'
    )
    sportcenters = django_filters.ModelChoiceFilter(
        queryset=SportCenters.objects.filter(
            id_sportcenters__in=SportZones.objects.values_list('id_sportcenters', flat=True)
        ),
        field_name='id_sportcenters__name',
        to_field_name='pk',
        label='Centro Deportivo'
    )

    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Nombre')

    class Meta:
        model = SportZones
        fields = []

    


class ReservationsFilter(django_filters.FilterSet):
    started = django_filters.DateFromToRangeFilter(field_name='started', label='Rango de fechas', widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'}), help_text='Formato: DD-MM-YYYY')

    class Meta:
        model = Reservations
        fields = {
            'id_reservationstatus': ['exact'],
            'id_sportzones': ['exact'],
            'id_clients': ['exact'],
            'id_reservations': ['exact'],
            'started': ['exact'],
        }

    order_by = django_filters.OrderingFilter(
        fields=(
            ('started', 'started'),
        ),
        field_labels={
            'started': 'Fecha de inicio'
        }
    )

    

