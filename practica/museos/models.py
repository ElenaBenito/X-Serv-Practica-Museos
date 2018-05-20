from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Museo(models.Model):
	entidad = models.CharField(max_length=10)
	nombre = models.CharField(max_length=128)
	descripcion = models.TextField()
	accesibilidad = models.CharField(max_length=1)
	content_url = models.CharField(max_length=256)
	localizacion = models.CharField(max_length=128)
	clase_vial = models.CharField(max_length=128)
	tipo_num = models.CharField(max_length=1)
	num = models.CharField(max_length=10)
	localidad = models.CharField(max_length=32)
	provincia = models.CharField(max_length=32)
	codigo_postal = models.CharField(max_length=32)
	barrio = models.CharField(max_length=32)
	distrito = models.CharField(max_length=32)
	coordenada_x = models.CharField(max_length=32)
	coordenada_y = models.CharField(max_length=32)
	cont_coments = models.IntegerField(default=0)
	cont_megusta = models.IntegerField(default=0)
	telefono = models.CharField(max_length=50)
	email = models.CharField(max_length=50)

class Comentario(models.Model):
	museo = models.ForeignKey(Museo)
	coment = models.TextField()

class Usuario(models.Model):
	nombre = models.OneToOneField(User)
	titulo_pagina = models.CharField(max_length=25)
	letra = models.FloatField(default=11)
	color = models.CharField(max_length=32)

class Seleccionados(models.Model):
	museo = models.ForeignKey(Museo)
	selector = models.ForeignKey(Usuario)
	fecha_seleccion = models.DateField()
