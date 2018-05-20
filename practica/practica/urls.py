from django.conf.urls import include, url
from django.contrib import admin
from museos import views
from django.views.static import *
from practica import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^change.css/', views.personalizar, name='Personalizar css'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_URL}),
    url(r'^$', views.pagina_principal, name='Página principal'),
    url(r'^login' , views.loginuser, name='Login'),
    url(r'^logout', views.mylogout, name='Logout'),
    url(r'^museos/$', views.museos, name='Museos'),
    url(r'^museos/(.*)', views.museos_id, name='Museo determinado'),
    url(r'^about/', views.about, name='About'),
    url(r'^(.*)/xml/', views.usuarios_xml, name='Página XML de un usuario'),
    url(r'^(.*)/$', views.usuarios, name='Página personal de un usuario'),
]
