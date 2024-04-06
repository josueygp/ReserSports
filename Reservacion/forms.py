
from django import forms
from .models import Reservations, Clients



########################################################

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Reservations


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        fields = '__all__'
        exclude = ['id_admistrators', 'id_reservationstatus']

   

class ClientForm(forms.ModelForm):
    class Meta:
        model = Clients
        exclude = ['id_auth_user']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class QuickReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        exclude = ['id_admistrators', 'id_reservationstatus','id_sportzones'] 
        fields = ['id_clients']


from django import forms
from django.utils import timezone

class AdvancedReservationForm(forms.ModelForm):
    start_date = forms.DateField(label='Fecha de inicio', widget=forms.DateInput(attrs={'type': 'date'}))
    duration = forms.ChoiceField(choices=[(30, '30 minutos'), (60, '1 hora'), (90, '1 hora 30 minutos'), (120, '2 horas')], label='Duración de la reserva')

    HORARIO_CHOICES = []
    for hora in range(9, 19):
        for minuto in (0, 30):
            hora_formato = f"{hora}:{minuto:02d}"
            if minuto == 0:
                hora_formato += " a.m."
            else:
                hora_formato += " p.m."
            HORARIO_CHOICES.append((f"{hora}:{minuto:02d}", hora_formato))

    horario = forms.ChoiceField(choices=HORARIO_CHOICES, label='Horario')

    class Meta:
        model = Reservations
        exclude = ['id_admistrators', 'id_reservationstatus', 'started', 'finished', 'creation_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        horario = cleaned_data.get('horario')
        duration = cleaned_data.get('duration')

        if start_date and horario:
            hora_inicio, minuto_inicio = [int(x) for x in horario.split(':')]
            hora_inicio = timezone.datetime.strptime(f"{hora_inicio}:{minuto_inicio:02d}", '%H:%M').time()

            start_datetime = timezone.datetime.combine(start_date, hora_inicio)
            cleaned_data['started'] = start_datetime

            if duration:
                duration_delta = timezone.timedelta(minutes=int(duration))
                finished_datetime = start_datetime + duration_delta
                cleaned_data['finished'] = finished_datetime

        return cleaned_data