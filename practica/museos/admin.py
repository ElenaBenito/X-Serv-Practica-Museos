from django.contrib import admin
from .models import Museo,Usuario,Comentario,Seleccionados

# Register your models here.
admin.site.register(Museo)
admin.site.register(Usuario)
admin.site.register(Comentario)
admin.site.register(Seleccionados)
