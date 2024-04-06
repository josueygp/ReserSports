from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from PIL import Image
from django.core.files import File
import os
import shutil




def copy_image(instance, filename, destination_path):
    source_path = instance.url_image.path
    destination = os.path.join(destination_path, filename)
    
    try:
        shutil.copy2(source_path, destination)
    except Exception as e:
        print(f"Error al copiar el archivo: {e}")
    
    # Cerrar el archivo después de la copia
    instance.url_image.file.close()

    return destination

# Create your models here.
class Countries(models.Model):
    id_countries = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name

class States(models.Model):
    id_states = models.AutoField(primary_key=True)
    id_countries=models.ForeignKey( Countries, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name
    
class Cities(models.Model):
    id_cities = models.AutoField(primary_key=True)
    id_states=models.ForeignKey(States, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name
################

class Infrastructures(models.Model):
    id_infrastructures = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name

class Sports(models.Model):
    id_sports = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name

class Facilities(models.Model):
    id_facilities = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name

class ReservationStatus(models.Model):
    id_reservationstatus = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)
    def __str__(self):
        return  self.name

###############################

class SportCenters(models.Model):
    id_sportcenters = models.AutoField(primary_key=True)
    id_cities=models.ForeignKey(Cities, on_delete=models.CASCADE)
    url_image = models.ImageField(upload_to='images/sport-centers/', default='images/transparent.png')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return  self.name




class SportZones(models.Model):
    id_sportzones = models.AutoField(primary_key=True)
    id_facilities=models.ForeignKey(Facilities, on_delete=models.CASCADE)
    id_sports=models.ForeignKey(Sports, on_delete=models.CASCADE)
    id_infrastructures= models.ForeignKey(Infrastructures , on_delete=models.CASCADE)
    id_sportcenters =models.ForeignKey(SportCenters, on_delete=models.CASCADE)
    url_image = models.ImageField(upload_to='images/sport-zones/', default='images/transparent.png')
    capacity = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    section = models.IntegerField(default=0,editable=False)  # Añadimos el campo 'section'

   
    
    def __str__(self):
        return self.name

    

from django.core.validators import RegexValidator

class PhoneNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 15)
        kwargs.setdefault(
            'validators', [RegexValidator(r'^\+?1?\d{9,15}$', message="El número de teléfono debe tener un formato válido.")])
        super().__init__(*args, **kwargs)


class Clients(models.Model):
    id_clients = models.AutoField(primary_key=True)
    id_auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name=  models.CharField(max_length=180)
    last_name=  models.CharField(max_length=180)
    email= models.CharField(max_length=180, default='')
    contact_number = PhoneNumberField(default='')
    birth_date = models.DateField(default=timezone.now) 
    creation_date= models.DateTimeField(auto_now=True) 
    def __str__(self):
        return  self.first_name + self.last_name





class Reservations(models.Model):
    id_reservations = models.AutoField(primary_key=True)
    id_sportzones = models.ForeignKey(SportZones, on_delete=models.CASCADE)
    id_reservationstatus = models.ForeignKey(ReservationStatus, on_delete=models.CASCADE, default=4)
    id_admistrators = models.ForeignKey(User, on_delete=models.CASCADE)
    id_clients = models.ForeignKey(Clients, on_delete=models.CASCADE)
    started = models.DateTimeField(default=timezone.now)
    finished = models.DateTimeField(default=timezone.now, null=True, blank=True)
    creation_date= models.DateTimeField(auto_now=True) 
    
   

class SportCentersPhotos(models.Model):
    id_photos = models.AutoField(primary_key=True)
    id_sportcenters = models.ForeignKey(SportCenters, on_delete=models.CASCADE)
    url_image = models.ImageField(upload_to='images/sport-centers/', default='images/transparent.png')
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.id_sportcenters} - {self.title}"



class SportZonesPhotos(models.Model):
    id_photos = models.AutoField(primary_key=True)
    id_sportzones=models.ForeignKey(SportZones, on_delete=models.CASCADE)
    url_image = models.ImageField(upload_to='images/sport-zones/', default='images/transparent.png')
    title = models.CharField(max_length=255)
    description = models.TextField()
    def __str__(self):
        return f"{self.id_sportzones} - {self.title}"

    
#########################
    