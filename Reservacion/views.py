from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Q
from .models import SportZones, SportZonesPhotos, Reservations,Clients, ReservationStatus, Infrastructures, Sports, Facilities
from .forms import AdvancedReservationForm, ReservationForm, ClientForm
from django.conf import settings

from django.http import JsonResponse
from django.http import HttpResponse
from xhtml2pdf import pisa
from openpyxl import Workbook
from .models import Clients
from django.template.loader import render_to_string

from django.shortcuts import render
from django_filters.views import FilterView
from .models import SportZones
from .filters import SportZonesFilter, ReservationsFilter

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

##############     PRUEBAS #############################

def get_reservation_color(status_id):
    """Returns a color based on the reservation status ID."""
    color_map = {
        2: '#ffeeba',  # Light yellow (Active)
        3: '#c3e6cb',  # Light green (Finalized)
        4: '#f5d0c0',  # Light pink (Reserved)
        5: '#f7cac9',  # Light red (Cancelled)
    }
    return color_map.get(status_id, '#fff')  # Default white for unknown status



############### FIN PRUEBAS#######################

#######
def signup(request):


    if request.method == 'GET':
        print('Enviando Formulario')
        return render(request,'signup.html',
                      {'form':UserCreationForm})
    else:
        if request.POST['password1']==request.POST['password2']:
            try:
                user=User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('home')

               
            except IntegrityError:
                    return render(request, 'signup.html', {
                        'form': UserCreationForm,
                        'error': 'Usuario ya existe'
                    })

        return render(request,'signup.html',{'form':UserCreationForm,"error":'Contraseña no coincide'})
##
@login_required
def signout(request):
     logout(request)
     return redirect('home')
###

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user= authenticate(request, username=request.POST['username'],
                           password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 
                          'error': 'Usuario o contraseña está vacio'})
        else:
            login(request, user)
            return redirect('home')
        
############



#############
@login_required
def cancelar_reserva(request):
    if request.method == 'POST' and request.is_ajax():
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reservations, id_reservations=reserva_id)

        # Actualizar el estado a "Cancelado"
        estado_cancelado = ReservationStatus.objects.get(name="Cancelado")
        reserva.id_reservationstatus = estado_cancelado
        reserva.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@login_required
def activar_reserva(request):
    if request.method == 'POST' and request.is_ajax():
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reservations, id_reservations=reserva_id)

        # Actualizar el estado a "Activo"
        estado_activo = ReservationStatus.objects.get(name="Activo")
        reserva.id_reservationstatus = estado_activo
        reserva.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

######## 

def home(request):
    # Filtrar las reservaciones por id_reservationstatus igual a 2 o 4
    reservations = Reservations.objects.filter(id_reservationstatus__in=[2, 4])
    events = []
    for reservation in reservations:
        title = f" {reservation.id_sportzones.name}, {reservation.id_reservationstatus.name}"
        event = {
            'title': title,
            'start': reservation.started.isoformat(),  # convertir a formato ISO 8601
            'end': reservation.finished.isoformat() if reservation.finished else None,
        }
        events.append(event)

    return render(request, 'home.html', {'events': events})




###########
def catalogue_detail(request, catalogue_id):
    catalogue = get_object_or_404(SportZones, pk=catalogue_id)
    return render(request, 'catalogue_detail.html', {'catalogue': catalogue})

def catalogue(request):
    # Obtener todos los objetos SportZones
    sportzone = SportZones.objects.all()  
    return render(request, 'catalogue.html', {'sportzone': sportzone,})



# Combina la lógica de filtrado con la vista catalogue
def sport_zones_list(request):
    f = SportZonesFilter(request.GET, queryset=SportZones.objects.all())
    return render(request, 'catalogue.html', {'filter': f})

class SportZonesListView(FilterView):
    filterset_class = SportZonesFilter
    queryset = SportZones.objects.all()
    template_name = 'catalogue.html'



##############


@login_required
def reception(request):
    today = datetime.now()
    all_reservations = Reservations.objects.filter(started__date=today.date())
    
    cancelled_status = ReservationStatus.objects.get(name="Cancelado")
    reserved_status = ReservationStatus.objects.get(name="Reservado")
    finished_status = ReservationStatus.objects.get(name="Finalizado")
    active_status = ReservationStatus.objects.get(name="Activo")

    cancelled_reservations = all_reservations.filter(id_reservationstatus=cancelled_status)
    reserved_reservations = all_reservations.filter(id_reservationstatus=reserved_status)
    finished_reservations = all_reservations.filter(id_reservationstatus=finished_status)
    active_reservations = all_reservations.filter(id_reservationstatus=active_status)

    print("Canceladas:", cancelled_reservations)
    print("Reservadas:", reserved_reservations)
    print("Finalizadas:", finished_reservations)
    print("Activas:", active_reservations)


    return render(request, 'reception.html', {
        'all_reservations': all_reservations,
        'cancelled_reservations': cancelled_reservations,
        'reserved_reservations': reserved_reservations,
        'finished_reservations': finished_reservations,
        'active_reservations': active_reservations,
    })


##################################################z
import qrcode
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from io import BytesIO
import base64

@login_required
def generate_reservation_pdf(request, reservation_id):
    # Obtener la reserva
    reservation = get_object_or_404(Reservations, pk=reservation_id)
    
    # Renderizar la plantilla HTML con los datos de la reserva
    html = render_to_string('reservation_pdf_template.html', {'reservation': reservation})
    
    # Crear un objeto de respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reservation.pdf"'  # Cambiar 'attachment' a 'inline'

    # Convertir el HTML a PDF
    pisa.CreatePDF(html, dest=response)

    return response

def reservation_list(request):
    f = ReservationsFilter(request.GET, queryset=Reservations.objects.all())
    return render(request, 'reservation.html', {'filter': f})

class ReservationsListView(FilterView):
    filterset_class = ReservationsFilter
    queryset = Reservations.objects.all()
    template_name = 'reservation.html'



@login_required
def reservation_edit(request, reservation_id):
    reservation = get_object_or_404(Reservations, pk=reservation_id)
    if request.method == 'POST':
        form = AdvancedReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            # Enviar correo electrónico de confirmación de reservación
            reservation_data = form.cleaned_data
            client_email = reservation_data['id_clients'].email
            subject = 'Confirmación Edición de Reservación'
            html_message = render_to_string('reservation_email.html', {'reservation_data': reservation_data})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [client_email]
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            return redirect('reservation')
    else:
       form = AdvancedReservationForm(instance=reservation, initial={
            'id_sportzones': reservation.id_sportzones,
            'id_clients': reservation.id_clients,
            'start_date': reservation.started.date(),
            'horario': reservation.started.strftime('%H:%M'),
            'duration': int((reservation.finished - reservation.started).total_seconds() / 60),
        })
    return render(request, 'reservation-edit.html', {'reservation': reservation, 'form': form})




@login_required
def reservation_create(request):
    clients = Clients.objects.all()  # Definir clients fuera del bloque if

    if request.method == 'POST':
        form = AdvancedReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.id_admistrators = request.user
            reservation.id_reservationstatus_id = 4  # 4 es el id de 'Reservado'
            reservation.started = form.cleaned_data['started']
            duration = form.cleaned_data['duration']
            if duration == '30':
                reservation.finished = reservation.started + timezone.timedelta(minutes=30)
            elif duration == '60':
                reservation.finished = reservation.started + timezone.timedelta(hours=1)
            elif duration == '90':
                reservation.finished = reservation.started + timezone.timedelta(hours=1.5)
            elif duration == '120':
                reservation.finished = reservation.started + timezone.timedelta(hours=2)
            reservation.save()

            # Enviar correo electrónico de confirmación de reservación
            reservation_data = {
                'id_sportzones': reservation.id_sportzones,
                'id_clients': reservation.id_clients,
                'started': reservation.started,
                'finished': reservation.finished,
                'duration': duration,
            }
            client_email = reservation.id_clients.email
            subject = 'Confirmación de Reservación'
            html_message = render_to_string('reservation_email.html', {'reservation_data': reservation_data})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [client_email]
            try:
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            except Exception as e:
                messages.error(request, f"No se pudo enviar el correo de confirmación: {e}", extra_tags='alert-danger')
            else:
                messages.success(request, "La reservación ha sido creada y se ha enviado el correo de confirmación.", extra_tags='alert-success')
            return redirect('reservation')
        else:
            print("Errores del formulario:")
            print(form.errors)
            messages.error(request, "No se pudo crear la reservación. Por favor, revise los datos ingresados.", extra_tags='alert-danger')
    else:
        form = AdvancedReservationForm()

        

    return render(request, 'reservation-create.html', {'form': form, 'clients': clients})





def get_available_times(start_date, sportzone_id):
    import datetime
    start_date = datetime.date.fromisoformat(start_date)
    reservations = Reservations.objects.filter(
        id_sportzones_id=sportzone_id,
        started__date=start_date,
        id_reservationstatus__in=[2, 4]
    )
    available_times = []
    for hour in range(9, 19):
        for minute in (0, 30):
            start_time = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time(hour, minute)))
            end_time = start_time + timezone.timedelta(minutes=30)
            if not reservations.filter(started__lte=end_time, finished__gte=start_time).exists():
                available_times.append((f"{hour}:{minute:02d}", f"{hour}:{minute:02d}"))
    return available_times

def get_available_times_ajax(request):
    start_date = request.GET.get('start_date')
    sportzone_id = request.GET.get('sportzone_id')
    if start_date and sportzone_id:
        available_times = get_available_times(start_date, int(sportzone_id))
        return JsonResponse({'available_times': available_times})
    else:
        return JsonResponse({'error': 'Falta información'})





@login_required
def cancelar_reserva(request, reservation_id):
    reservation = Reservations.objects.get(pk=reservation_id)
    if reservation.id_reservationstatus_id == 4:  # Verificar si la reserva está en estado 'Reservado'
        reservation.id_reservationstatus = ReservationStatus.objects.get(pk=5)  # Cambiar a 'Cancelado'
        reservation.save()

        # Enviar correo electrónico de confirmación de cancelación de reservación
        client_email = reservation.id_clients.email
        subject = 'Confirmación de Cancelación de Reservación'
        html_message = render_to_string('cancel_reservation_email.html', {'reservation': reservation})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [client_email]

        try:
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        except Exception as e:
            messages.error(request, f"No se pudo enviar el correo de confirmación de cancelación: {e}")
        else:
            messages.success(request, "La reservación ha sido cancelada y se ha enviado el correo de confirmación.")

    return redirect('reservation')



@login_required
def activar_reserva(request, reservation_id):
    reservation = Reservations.objects.get(pk=reservation_id)
    if reservation.id_reservationstatus_id == 4:
        reservation.id_reservationstatus = ReservationStatus.objects.get(pk=2)  # Cambiar a 'Activo'
        reservation.save()

        # Enviar correo electrónico de confirmación de inicio de reservación
        client_email = reservation.id_clients.email
        subject = 'Confirmación de Inicio de Reservación'
        html_message = render_to_string('actived_reservation_email.html', {'reservation': reservation})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [client_email]

        try:
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        except Exception as e:
            messages.error(request, f"No se pudo enviar el correo de confirmación de inicio de reservación: {e}")
        else:
            messages.success(request, "La reservación ha sido activada y se ha enviado el correo de confirmación.")

    return redirect('reservation')

@login_required
def finalizar_reserva(request, reservation_id):
    reservation = Reservations.objects.get(pk=reservation_id)
    if reservation.id_reservationstatus_id == 2:
        reservation.id_reservationstatus = ReservationStatus.objects.get(pk=3)  # Cambiar a 'Finalizado'
        reservation.save()

        # Enviar correo electrónico de confirmación de finalización de reservación
        client_email = reservation.id_clients.email
        subject = 'Confirmación de Finalización de Reservación'
        html_message = render_to_string('finished_reservation_email.html', {'reservation': reservation})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [client_email]

        try:
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        except Exception as e:
            messages.error(request, f"No se pudo enviar el correo de confirmación de finalización de reservación: {e}")
        else:
            messages.success(request, "La reservación ha sido finalizada y se ha enviado el correo de confirmación.")

    return redirect('reservation')



#########################################



@login_required
def client(request):
    search_query = request.GET.get('search', '')
    if search_query:
        try:
            client_id = int(search_query)
            # Busca por el ID del cliente y los nombres de los clientes
            clients = Clients.objects.filter(id_clients=client_id)
        except ValueError:
            # Si el valor no es un número válido, busca solo por los nombres de los clientes
            clients = Clients.objects.filter(Q(first_name__icontains=search_query) | 
                                              Q(last_name__icontains=search_query))
    else:
        clients = Clients.objects.all()
    
    context = {'clients': clients}
    
    # Verificar si la solicitud es para un PDF
    if request.GET.get('format') == 'pdf':
        # Obtener el cliente específico si está presente en la consulta
        client_id = request.GET.get('client_id')
        if client_id:
            client = Clients.objects.get(id_clients=client_id)
            reservations = client.reservations_set.all()  # Cambiar aquí
            context = {'client': client, 'reservations': reservations}
        template_path = 'clients_pdf_template.html'
        return render_pdf(template_path, context)
    
    # Verificar si la solicitud es para un archivo Excel
    elif request.GET.get('format') == 'excel':
        return generate_excel(clients)

    return render(request, 'clients.html', context)




def generate_excel(clients):
    # Crear un libro de trabajo de Excel
    wb = Workbook()
    # Activar la hoja de trabajo predeterminada
    ws = wb.active

    # Agregar encabezados a la primera fila
    ws.append(['ID', 'Nombre', 'Apellido', 'Fecha de Nacimiento'])

    # Agregar datos de clientes a las filas
    for client in clients:
        ws.append([
            client.id_clients,
            client.first_name,
            client.last_name,
            client.birth_date
        ])

    # Crear una respuesta HTTP con el contenido del archivo Excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
    # Guardar el libro de trabajo en la respuesta
    wb.save(response)

    return response

def render_pdf(template_path, context_dict):
    template_str = render_to_string(template_path, context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="clientes.pdf"'  # Cambiar 'attachment' a 'inline'

    pisa_status = pisa.CreatePDF(
        template_str, dest=response, encoding='utf-8')
    
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, pisa_status.log), content_type='text/html')
    return response



@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Clients, pk=client_id)
    reservations = Reservations.objects.filter(id_clients=client)
    return render(request, 'clients_detail.html', {'client': client, 'reservations': reservations})




@login_required
def client_edit(request, client_id):
    client = Clients.objects.get(id_clients=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()

            # Enviar correo electrónico al cliente
            client_data = form.cleaned_data
            subject = 'Se han modificado tus datos como cliente'
            html_message = render_to_string('client_email.html', {'client_data': client_data})  
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [client_data['email']]  # Usar el email del cliente obtenido del formulario

            try:
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            except Exception as e:
                messages.error(request, f"No se pudo enviar el correo de modificación de datos: {e}")
            else:
                messages.success(request, "Los datos del cliente han sido modificados y se ha enviado el correo de confirmación.")
            return redirect('client_detail', client_id=client_id)
    else:
        # Convertir la fecha de nacimiento a un objeto datetime.date antes de pasarla al formulario
        birth_date = client.birth_date.strftime('%Y-%m-%d')
        form = ClientForm(instance=client, initial={'birth_date': birth_date})
    return render(request, 'clients-edit.html', {'form': form, 'client': client})



from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            # Asignar automáticamente el usuario autenticado al campo id_auth_user
            form.instance.id_auth_user = request.user
            form.save()
            
            # Enviar correo electrónico al cliente
            client_data = form.cleaned_data
            subject = 'Usted ha sido dado de alta como cliente'
            html_message = render_to_string('client_email.html', {'client_data': client_data}) 
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [client_data['email']]  # Usar el email del cliente obtenido del formulario

            try:
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            except Exception as e:
                messages.error(request, f"No se pudo enviar el correo de alta como cliente: {e}")
            else:
                messages.success(request, "Cliente creado exitosamente y se ha enviado el correo de confirmación.")
            return redirect('client')  # Reemplaza 'home' con el nombre de tu vista principal
    else:
        form = ClientForm()

    return render(request, 'clients-create.html', {'form': form})



@login_required
def client_delete(request, client_id):
    client = get_object_or_404(Clients, pk=client_id)
    
    if request.method == 'POST':
        # Obtener los datos del cliente antes de eliminarlo
        client_data = {
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'contact_number': client.contact_number,
            'birth_date': client.birth_date,
        }
        
        # Eliminar al cliente
        client.delete()
        
        # Enviar correo electrónico de confirmación de eliminación
        subject = 'Cliente eliminado'
        html_message = client.first_name + client.last_name + 'Usted ha sido eliminado de nuestra base de datos como cliente.'
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [client_data['email']]

        try:
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        except Exception as e:
            messages.error(request, f"No se pudo enviar el correo de confirmación de eliminación: {e}")
        else:
            messages.success(request, "Cliente eliminado exitosamente y se ha enviado el correo de confirmación.")
            
        return redirect('client')  # Redirige directamente a la lista de clientes después de eliminar el registro
    
    return render(request, 'clients-delete.html', {'client': client})

#########################

from django.shortcuts import render
from .models import Reservations, SportZones, ReservationStatus
from django.db.models import Count, Avg, F, DateTimeField, ExpressionWrapper, DurationField, Max
from django.db.models.functions import TruncMonth, TruncYear,TruncWeek,TruncDay
@login_required
def reservation_statistics(request):
    # Contar el número total de reservaciones
    total_reservations = Reservations.objects.count()

    # Contar el número de reservaciones por zona deportiva
    reservations_per_sportzone = Reservations.objects.values('id_sportzones__name').annotate(count=Count('id_sportzones'))

    # Obtener la cantidad de reservaciones por estado de reservación
    reservations_per_status = Reservations.objects.values('id_reservationstatus__name').annotate(count=Count('id_reservationstatus'))

    # Calcular la duración promedio de las reservaciones
    duration_avg = Reservations.objects.annotate(
        duration=ExpressionWrapper(
            F('finished') - F('started'),
            output_field=DurationField()
        )
    ).aggregate(Avg('duration'))

    # Obtener las reservaciones más recientes por cliente
    recent_reservations_per_client = Reservations.objects.values('id_clients__first_name', 'id_clients__last_name').annotate(latest=Max('started')).order_by('-latest')

    # Contar las reservaciones por administrador
    reservations_per_admin = Reservations.objects.values('id_admistrators__username').annotate(count=Count('id_admistrators'))

    # Obtener las reservaciones por mes
    reservations_per_month = Reservations.objects.annotate(
        month=TruncMonth('started')
    ).values('month').annotate(count=Count('id_reservations')).order_by('month')

    # Obtener las reservaciones por año
    reservations_per_year = Reservations.objects.annotate(
        year=TruncYear('started')
    ).values('year').annotate(count=Count('id_reservations')).order_by('year')

    # Obtener las zonas deportivas más utilizadas
    top_sportzones = Reservations.objects.values('id_sportzones__name').annotate(
        count=Count('id_sportzones')
    ).order_by('-count')[:5]

    reservations_per_client = Reservations.objects.values('id_clients__first_name', 'id_clients__last_name').annotate(count=Count('id_clients'))

        # Obtener las reservaciones por rango de fechas (por día)
    reservations_per_date_range = Reservations.objects.annotate(
        date_range=TruncDay('started')
    ).values('date_range').annotate(count=Count('id_reservations')).order_by('date_range')

    # Obtener las reservaciones por rango de fechas (por semana)
    reservations_per_date_range = Reservations.objects.annotate(
        date_range=TruncWeek('started')
    ).values('date_range').annotate(count=Count('id_reservations')).order_by('date_range')

    # Obtener las reservaciones por rango de fechas (por mes)
    reservations_per_date_range = Reservations.objects.annotate(
        date_range=TruncMonth('started')
    ).values('date_range').annotate(count=Count('id_reservations')).order_by('date_range')

    # Obtener las reservaciones por rango de fechas (por año)
    reservations_per_date_range = Reservations.objects.annotate(
        date_range=TruncYear('started')
    ).values('date_range').annotate(count=Count('id_reservations')).order_by('date_range')

    # Obtener las reservaciones por día de la semana
    reservations_per_weekday = Reservations.objects.annotate(weekday=TruncWeek('started')).values('weekday').annotate(count=Count('id_reservations'))


    context = {
        'total_reservations': total_reservations,
        'reservations_per_sportzone': reservations_per_sportzone,
        'reservations_per_status': reservations_per_status,
        'duration_avg': duration_avg,
        'recent_reservations_per_client': recent_reservations_per_client,
        'reservations_per_admin': reservations_per_admin,
        'reservations_per_month': reservations_per_month,
        'reservations_per_year': reservations_per_year,
        'top_sportzones': top_sportzones,
        'reservations_per_client': reservations_per_client,
        'reservations_per_date_range': reservations_per_date_range,
        'reservations_per_weekday': reservations_per_weekday,
    }

    return render(request, 'statistics.html', context)


#########

#####################from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import QuickReservationForm
from .models import Reservations
@login_required
def quick_reservation(request, sportzone_id):
    # Obtener la zona deportiva actual
    sportzone = SportZones.objects.get(pk=sportzone_id)
    
    # Obtener la hora actual
    current_time = timezone.now().time()

    # Obtener todas las reservaciones existentes para esta zona deportiva
    existing_reservations = Reservations.objects.filter(
        id_sportzones=sportzone,
        id_reservationstatus_id__in=[2, 4],  # Reservado o En espera
        started__date=timezone.now().date(),  # Solo las reservaciones para hoy
    )

    # Calcular las horas en las que no se solapan reservaciones existentes
    available_durations = []
    for button_duration in [30, 60, 90, 120]:
        end_time = (timezone.datetime.combine(timezone.now().date(), current_time) + timezone.timedelta(minutes=button_duration)).time()
        overlaps = False
        for reservation in existing_reservations:
            if (reservation.started.time() < end_time and reservation.finished.time() > current_time):
                overlaps = True
                break
        if not overlaps:
            available_durations.append(button_duration)

    if request.method == 'POST':
        form = QuickReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.id_reservationstatus_id = 2  # Asigna el estado "Reservado"
            reservation.id_sportzones_id = sportzone_id  # Asigna el ID de la zona deportiva
            reservation.id_admistrators_id = request.user.id  # Asigna el ID del usuario autenticado al campo id_admistrators_id
            
            reservation.started = timezone.now()
            duration = request.POST.get('duration')
            if duration == '30':
                reservation.finished = reservation.started + timezone.timedelta(minutes=30)
            elif duration == '60':
                reservation.finished = reservation.started + timezone.timedelta(hours=1)
            elif duration == '90':
                reservation.finished = reservation.started + timezone.timedelta(hours=1.5)
            elif duration == '120':
                reservation.finished = reservation.started + timezone.timedelta(hours=2)
            reservation.save()
            
            # Envía correo electrónico de confirmación
            client_email = reservation.id_clients.email
            subject = 'Confirmación de Reservación'
            reservation_data = {
                'client_first_name': reservation.id_clients.first_name,
                'client_last_name': reservation.id_clients.last_name,
                'sportzone_name': reservation.id_sportzones.name,
                'started': reservation.started,
                'finished': reservation.finished,
            }
            html_message = render_to_string('reservationQuick_email.html', {'reservation_data': reservation_data})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [client_email]
            
            try:
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
                messages.success(request, "Reservación exitosa. Se ha enviado un correo de confirmación.")
            except Exception as e:
                messages.error(request, f"No se pudo enviar el correo de confirmación: {e}")
            
            return redirect('reservation')  # Redirige a la página de éxito
    else:
        form = QuickReservationForm()

    return render(request, 'quick_reservation.html', {'form': form, 'available_durations': available_durations})


###################
from django.shortcuts import render
from .models import SportZones, Reservations
@login_required 
def calendar_view(request):
    # Obtener todas las zonas deportivas
    sport_zones = SportZones.objects.all()

    # Obtener las reservaciones activas (con estado 2 y 4)
    active_reservations = Reservations.objects.filter(id_reservationstatus__in=[2, 4])

    # Crear un diccionario para almacenar las reservaciones por zona deportiva y hora
    reservations_by_zone_and_hour = {}

    # Iterar sobre las reservaciones activas
    for reservation in active_reservations:
        sport_zone = reservation.id_sportzones
        start_hour = reservation.started.hour
        end_hour = None
        if reservation.finished:
            end_hour = reservation.finished.hour
        else:
            # Manejar el caso cuando finished es None
            # Por ejemplo, asignar un valor predeterminado a end_hour
            end_hour = 23  # Asumiendo que el establecimiento cierra a las 11 pm

        if sport_zone not in reservations_by_zone_and_hour:
            reservations_by_zone_and_hour[sport_zone] = {}

        for hour in range(start_hour, end_hour + 1):
            if hour not in reservations_by_zone_and_hour[sport_zone]:
                reservations_by_zone_and_hour[sport_zone][hour] = []
            reservations_by_zone_and_hour[sport_zone][hour].append(reservation)
    # Crear una lista de horas para la tabla
    hours = range(9, 18)  # Asumiendo que el establecimiento abre a las 8 am y cierra a las 10 pm

    context = {
        'sport_zones': sport_zones,
        'hours': hours,
        'reservations_by_zone_and_hour': reservations_by_zone_and_hour,
    }

    return render(request, 'calendar.html', context)
########################
def sportzone_list_free(request):
    """
    Vista que muestra un listado de SportZones disponibles para reservar.

    Esta vista toma en cuenta los siguientes factores:
    1. Las zonas deportivas que ya están reservadas en el momento actual.
    2. Deja un margen de 30 minutos antes de una próxima reservación para evitar solapes.
    3. Verifica si la reservación tiene un estado específico ('Activo', 'Reservado') antes de considerarla como activa.
    """
    current_time = timezone.now()

    # Obtener las reservaciones activas en el momento actual con estado específico
    active_reservations = Reservations.objects.filter(
        started__lte=current_time,
        finished__gte=current_time,
        id_reservationstatus__name__in=['Activo', 'Reservado']
    )

    # Obtener las zonas deportivas reservadas en el momento actual
    reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in active_reservations]

    # Obtener las próximas reservaciones que comienzan dentro de 30 minutos
    upcoming_reservations = Reservations.objects.filter(
        started__gt=current_time,
        started__lte=current_time + timedelta(minutes=30),
        id_reservationstatus__name__in=['Activo', 'Reservado']
    )

    # Obtener las zonas deportivas que estarán reservadas dentro de 30 minutos
    upcoming_reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in upcoming_reservations]

    # Excluir las zonas deportivas que están reservadas actualmente y las que estarán reservadas dentro de 30 minutos
    free_sportzones = SportZones.objects.exclude(
        id_sportzones__in=reserved_sportzone_ids + upcoming_reserved_sportzone_ids
    )

    return render(request, 'sportzone_free.html', {'free_sportzones': free_sportzones})

@login_required
def sport_zones_list_Free(request):
    """
    Vista alternativa que utiliza un filtro para listar los SportZones disponibles.

    Esta vista toma en cuenta los siguientes factores:
    1. Las zonas deportivas que ya están reservadas en el momento actual.
    2. Deja un margen de 30 minutos antes de una próxima reservación para evitar solapes.
    3. Verifica si la reservación tiene un estado específico ('Activo', 'Reservado') antes de considerarla como activa.
    """
    current_time = timezone.now()

    # Obtener las reservaciones activas en el momento actual con estado específico
    active_reservations = Reservations.objects.filter(
        started__lte=current_time,
        finished__gte=current_time,
        id_reservationstatus__name__in=['Activo', 'Reservado']
    )

    # Obtener las zonas deportivas reservadas en el momento actual
    reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in active_reservations]

    # Obtener las próximas reservaciones que comienzan dentro de 30 minutos
    upcoming_reservations = Reservations.objects.filter(
        started__gt=current_time,
        started__lte=current_time + timedelta(minutes=30),
        id_reservationstatus__name__in=['Activo', 'Reservado']
    )

    # Obtener las zonas deportivas que estarán reservadas dentro de 30 minutos
    upcoming_reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in upcoming_reservations]

    # Excluir las zonas deportivas que están reservadas actualmente y las que estarán reservadas dentro de 30 minutos
    free_sportzones = SportZones.objects.exclude(
        id_sportzones__in=reserved_sportzone_ids + upcoming_reserved_sportzone_ids
    )

    f = SportZonesFilter(request.GET, queryset=free_sportzones)
    return render(request, 'sportzone_free.html', {'filter': f})

class SportZonesListFreeView(FilterView):
    """
    Vista basada en clase que utiliza el filtro SportZonesFilter para listar SportZones disponibles.

    Esta vista toma en cuenta los siguientes factores:
    1. Las zonas deportivas que ya están reservadas en el momento actual.
    2. Deja un margen de 30 minutos antes de una próxima reservación para evitar solapes.
    3. Verifica si la reservación tiene un estado específico ('Activo', 'Reservado') antes de considerarla como activa.
    """
    filterset_class = SportZonesFilter
    template_name = 'sportzone_free.html'

    def get_queryset(self):
        current_time = timezone.now()

        # Obtener las reservaciones activas en el momento actual con estado específico
        active_reservations = Reservations.objects.filter(
            started__lte=current_time,
            finished__gte=current_time,
            id_reservationstatus__name__in=['Activo', 'Reservado']
        )

        # Obtener las zonas deportivas reservadas en el momento actual
        reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in active_reservations]

        # Obtener las próximas reservaciones que comienzan dentro de 30 minutos
        upcoming_reservations = Reservations.objects.filter(
            started__gt=current_time,
            started__lte=current_time + timedelta(minutes=30),
            id_reservationstatus__name__in=['Activo', 'Reservado']
        )

        # Obtener las zonas deportivas que estarán reservadas dentro de 30 minutos
        upcoming_reserved_sportzone_ids = [reservation.id_sportzones_id for reservation in upcoming_reservations]

        # Excluir las zonas deportivas que están reservadas actualmente y las que estarán reservadas dentro de 30 minutos
        free_sportzones = SportZones.objects.exclude(
            id_sportzones__in=reserved_sportzone_ids + upcoming_reserved_sportzone_ids
        )

        return free_sportzones

####################

@login_required
def sportzone_list_reserved(request):
    current_time = timezone.now()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Filtra las reservaciones activas/en curso
    active_reservations = Reservations.objects.filter(
        started__lte=current_time,
        finished__gte=current_time,
        id_reservationstatus_id=2
    ).select_related('id_sportzones')

    # Filtra las reservaciones vencidas pero aún en curso
    overdue_reservations = Reservations.objects.filter(
        finished__lt=current_time,
        id_reservationstatus_id=2
    ).select_related('id_sportzones')

    # Filtra las reservaciones ya hechas para hoy
    completed_reservations = Reservations.objects.filter(
    started__date=timezone.now().date(),
    finished__date=timezone.now().date(),  # Asegúrate de que la reserva haya terminado en el día actual
    id_reservationstatus_id=4
).select_related('id_sportzones')

    # Filtra las reservaciones sin confirmar que ya pasaron
    unconfirmed_reservations = Reservations.objects.filter(
        started__lt=current_time,
        id_reservationstatus_id=4
    ).select_related('id_sportzones')

    for reservation in active_reservations:
        # Calcula los minutos restantes para la reserva
        time_remaining = (reservation.finished - current_time).total_seconds() / 60
        reservation.minutes_remaining = max(int(time_remaining), 0)  # Asegúrate de que los minutos restantes sean al menos 0

    return render(request, 'sportzone_reserved.html', {
        'active_reservations': active_reservations,
        'overdue_reservations': overdue_reservations,
        'completed_reservations': completed_reservations,
        'unconfirmed_reservations': unconfirmed_reservations,
        'current_time': current_time
    })
