from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xml.etree.ElementTree as etree
from xml.dom.minidom import Document, parse
import xml.dom.minidom as dom
import datetime
import sys
from .parser import get_data
from django.http import QueryDict
import urllib

# Create your views here.

@csrf_exempt
def login_form(request):
    formulario = '<form action="login" method="POST">'
    formulario += 'Nombre<br><input type="text" name="Usuario"><br>'
    formulario += 'Contraseña<br><input type="password" name="Password"><br>'
    formulario += '<br><input type="submit" value="Entrar"></form>'
    return formulario

@csrf_exempt
def loginuser(request):
	username = request.POST['Usuario']
	password = request.POST['Password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request,user)
		direcc = '/' + str(user)
		return redirect(direcc)
	else:
		Error = "Por favor, introduzca usuario y contraseña válidos."
		template = get_template("fail.html")
		c = Context ({'Error': Error})
		renderizado = template.render(c)
		return HttpResponse(renderizado)

def mylogout(request):
	logout(request)
	return redirect("/")

def lista_coments():
    lista_todos = Museo.objects.all()
    lista_ordenada = lista_todos.order_by("-cont_coments")[:5]
    Response = "LISTADO DE MUSEOS CON MÁS COMENTARIOS<br><br>"
    Existe = False
    for i in lista_ordenada:
        coment = i.cont_coments
        if coment != 0:
            Response += "<li><a href=" + i.content_url + ">" + i.nombre + "<br></a>"
            Response += "Dirección: " + i.clase_vial + " " + i.localizacion + ", nº " + str(i.num)
            Response += "<br><a href=http://127.0.0.1:8000/museos/" + i.entidad + ">" + "Más información<br></a><br>"
            Existe = True
    if Existe == False:
        Response += "No se han registrado comentarios para ningún museo"

    Response += "</br></br>"
    return Response

def paginas_personales():
	Lista = "PÁGINAS DE USUARIOS<br><br>"
	usuarios = User.objects.all()
	for i in usuarios:
		try:
			pagina = Usuario.objects.get(nombre=i.id).titulo_pagina
		except ObjectDoesNotExist:
			pagina = "Página de " + i.username
		Lista += "<a href=http://127.0.0.1:8000/" + i.username + ">" + pagina + "</a>	Usuario: " + i.username + "<br>"

	return Lista

def personalizar(request):
	if request.user.is_authenticated():
		user_object = User.objects.get(username=request.user)
		user = Usuario.objects.get(nombre=user_object)
		letra = user.letra
		color = user.color
	else:
		letra = "14px"
		color = "#FCFCFC"

	css = get_template("change.css")
    
	c = Context({'letra':letra, 'color':color})
	renderizado = css.render(c)
	return HttpResponse(renderizado, content_type="text/css")

def lista_museos():
	lista = ''
	museos = Museo.objects.all()
	for museo in museos:
		nombre_museo = museo.nombre
		url_museo = museo.entidad
		lista += '<li><p>' + nombre_museo + '<a href="' + url_museo + '">	--> Más información</a></p></li>'

	return lista

def museos_seleccionados(user,request):
	user_object = User.objects.get(username=user)
	try:
		usuario = Usuario.objects.get(nombre=user_object)
		lista_seleccionados = Seleccionados.objects.filter(selector=usuario)
		paginator = Paginator(lista_seleccionados,5)
		page = request.GET.get('page')
		try:
			seleccionados = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			seleccionados = paginator.page(1)
		except EmptyPage:
		     # If page is out of range (e.g. 9999), deliver last page of results.
			seleccionados = paginator.page(paginator.num_pages)

		lista = "Listado de museos seleccionados por " + user + "<br>"

		for i in seleccionados:
			lista += "<br><li>Fecha de selección: " + str(i.fecha_seleccion)
			lista += "<br><a href=" + i.museo.content_url + ">" + i.museo.nombre + "<br></a>"
			lista += "Dirección: " + i.museo.clase_vial + " " + i.museo.localizacion + ", nº " + str(i.museo.num)
			lista += "<br><a href=http://127.0.0.1:8000/museos/" + i.museo.entidad + ">" + "Más información</a><br>"
	except ObjectDoesNotExist:
		lista = "El usuario no tiene ningún museo seleccionado."
		seleccionados = ""
	return lista,seleccionados

def accesibles(value):
	accesibles = '<form action="" method="POST">'
	accesibles += '<button type="submit" name="Accesible" value="' + str(value) + '"> Accesibles</button></form>'

	return accesibles

@csrf_exempt
def pagina_principal(request):
	formulario = login_form(request)
	list_comment = lista_coments()
	users = paginas_personales()
	value = 1
	accesible = accesibles(value)
	template = get_template("index.html")

	if request.user.is_authenticated():
		username = str(request.user)
		formulario = 'Bienvenido ' + username
		formulario += '<br><br><a href="http://127.0.0.1:8000/logout" > Logout </a>'

	if request.method == 'POST':
		key = request.body.decode("utf-8").split('=')[0]

		if key == 'Accesible':
			value = request.POST['Accesible']

			if value == '1':
				lista_accesibles = Museo.objects.filter(accesibilidad=1)
				lista = '<a href="http://127.0.0.1:8000/" > Volver </a>'
				value = 0
				for i in lista_accesibles:
					nombre_museo = i.nombre
					url_museo = i.content_url
					lista += "<li><p>" + nombre_museo + "</p><a href=" + url_museo + ">" + url_museo + "</a></li>"
			else:
				lista = '<a href="http://127.0.0.1:8000/" > Volver </a>'
				museos = Museo.objects.all()
				for museo in museos:
					nombre_museo = museo.nombre
					url_museo = museo.entidad
					lista += '<li><p>' + nombre_museo + '. URL del museo: ' + '<a href="museos/' + url_museo + '">	⇾ Más información</a></br></p>'
				value = 1

			accesible = accesibles(value)
			c = Context({'login': formulario, 'list_users':lista, 'accesible': accesible})

	else:
		init = Museo.objects.all()

		if len(init) == 0:
			get_data()

		c = Context({'login': formulario, 'list':list_comment, 'list_users':users, 'accesible': accesible})

	renderizado = template.render(c)
	return HttpResponse(renderizado)

@csrf_exempt
def usuarios(request, peticion):
	formulario = '<form action="" method="POST">'
	formulario += '<br>Introduzca un título para su página personal.<br><input type="text" name="Titulo">'
	formulario += '<input type="submit" value=" Cambiar"></form>'

	css = '<form action="" method="POST">'
	css += 'Modifique el tamaño de letra<br><input type="text" name="Letra">'
	css += '<br><br>Modifique el color de letra	<input type="color" name="Color"><br>'
	css += '<br><input type="submit" value="Modificar"></form>'

	museos = Museo.objects.all()
	lista= "<br>LISTADO DE MUSEOS<br><br>"
	for museo in museos:
		nombre_museo = museo.nombre
		lista += nombre_museo
		lista += '<form action="" method="POST">'
		lista += '<button type="submit" name="Seleccionar" value="' + nombre_museo + '">Seleccionar</button><br></form>'

	user_object= User.objects.get(username=peticion)

	if request.method == 'POST':
		key = request.body.decode("utf-8").split('=')[0]
		if key == "Titulo":
			titulo = request.POST['Titulo']
			try:
				user = Usuario.objects.get(nombre=user_object)
				user.titulo_pagina = titulo
				user.save()
			except ObjectDoesNotExist:
				p = Usuario(nombre=user_object, titulo_pagina=titulo)
				p.save()

		elif key == "Seleccionar":
			nombre_museo = request.POST['Seleccionar']
			today = datetime.datetime.today()

			try:
				selector = Usuario.objects.get(nombre=user_object)
				museo = Museo.objects.get(nombre=nombre_museo)
			except:
				p = Usuario(nombre=user_object)
				p.save()
				selector = Usuario.objects.get(nombre=user_object)

			Check = False
			lista_usuario = Seleccionados.objects.filter(selector=selector)
			for i in lista_usuario:
				if	nombre_museo == i.museo.nombre:
					Check=True

			if Check == False:
				p = Seleccionados(museo=museo, selector=selector, fecha_seleccion=today)
				p.save()

		elif key == "Letra":
			letra = request.POST['Letra']
			color = request.POST['Color']

			try:
				user = Usuario.objects.get(nombre=user_object)
			except:
				p = Usuario(nombre=user_object)
				p.save()
				user = Usuario.objects.get(nombre=user_object)
			if letra == "":
				letra = "15"

			user.letra = letra
			user.color = color
			user.save()

	lista_seleccionados, seleccionados= museos_seleccionados(peticion,request)

	if request.user.is_authenticated():
		username = str(request.user)
		if peticion != username:
			template = get_template("publicuser.html")
			titulo_pagina = "Página pública de " + peticion + "<br><br>"
			form_user = 'Bienvenido ' + username
			form_user += '<br><br><a href="http://127.0.0.1:8000/logout" > Logout </a>'
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user})
		else:
			template = get_template("privateuser.html")
			try:
				titulo_pagina = Usuario.objects.get(nombre=user_object).titulo_pagina
			except ObjectDoesNotExist:
				titulo_pagina = "Página personal de " + str(request.user) + "<br><br>"
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'lista': lista, 'form': formulario, 'css':css, 'titulo': titulo_pagina})
	else:
		template = get_template("publicuser.html")
		titulo_pagina = "Página pública de " + peticion + "<br><br>"
		form_user = 'Para loguearse vaya a la página de Inicio'
		c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user})

	renderizado = template.render(c)
	return HttpResponse(renderizado)


@csrf_exempt
def museos(request):
	lista = lista_museos()             #Buscar por distrito:
	filtrar = '<form action="" method="POST">'
	filtrar += '<br><br><input type="text" name="distrito">'
	filtrar += '<input type="submit" value="Filtrar por distrito">'
	template = get_template("museos.html")

	if request.user.is_authenticated():
		username = str(request.user)
		form_user = 'Bienvenido ' + username
		form_user += '<br><br><a href="http://127.0.0.1:8000/logout" > Logout </a>'
	else:
		form_user = "Para loguearse vaya a la pagina de Inicio"

	if request.method == "POST":
		filtro_distrito = request.POST['distrito']
		filtro_distrito = filtro_distrito.upper()

		if filtro_distrito == '':
			lista_filtrada = "No ha introducido ningún filtro, introduzca distrito para filtrar " + lista
		else:
			museos_filtrados = Museo.objects.all()
			Encontrado = False
			lista_filtrada = "Los museos en el " + filtro_distrito + " son: "
			for i in museos_filtrados:
				if filtro_distrito == i.distrito:
					Encontrado = True
					nombre_museo = i.nombre
					url_museo = i.content_url
					lista_filtrada += "<p>" + nombre_museo + "</p><li><a href=" + url_museo + ">" + url_museo + "</a></li>"

			if Encontrado == False:		#Distrito no válido
				lista_filtrada = "Introduzca un nuevo distrito. " + filtro_distrito + " no es válido"

		c = Context({'distrito': filtrar, 'lista': lista_filtrada, 'login':form_user})

	else:
		c = Context({'distrito': filtrar, 'lista': lista, 'login':form_user})

	renderizado = template.render(c)
	return HttpResponse(renderizado)

@csrf_exempt
def museos_id(request, recurso):
    template = get_template("museos.html")
    num_megusta = 0

    if request.method == 'POST':
        key = request.body.decode("utf-8").split('=')[0]
        print(key)

        if key == 'Me+Gusta':
            museo = Museo.objects.get(entidad=recurso)
            museo.cont_megusta = museo.cont_megusta + 1
            museo.save()
            num_megusta = museo.cont_megusta
        else:
            coment = request.POST['Comentario']
            museo = Museo.objects.get(entidad=recurso)
            museo.cont_coments = museo.cont_coments + 1
            museo.save()

            p = Comentario (museo= museo, coment=coment)
            p.save()

    try:
        museo = Museo.objects.get(entidad=recurso)
        nombre = museo.nombre
        descripcion = museo.descripcion
        accesibilidad = museo.accesibilidad
        localizacion = museo.localizacion
        via = museo.clase_vial
        num = museo.num
        localidad = museo.localidad
        provincia = museo.provincia
        codigo_postal = museo.codigo_postal
        barrio = museo.barrio
        distrito = museo.distrito
        coordenada_x = museo.coordenada_x
        coordenada_y = museo.coordenada_y
        telefono = museo.telefono
        email = museo.email

        if telefono == '':
            telefono = "No disponible"

        if email == '':
            email = "No disponible"

        if accesibilidad == 1:
            acces = "Libre"
        else:
            acces = "Ocupado"

        lista_museos = Museo.objects.all()
        list_coments = ""
        museo = Museo.objects.get(entidad=recurso)
        num_megusta = museo.cont_megusta
        for i in lista_museos:
            if i.entidad == recurso:
                comentarios = Comentario.objects.filter(museo=i)
                if len(comentarios) != 0:
                    list_coments = "<li><p>COMENTARIOS</p><ol>"
                    for j in comentarios:
                        list_coments += "<li>" + j.coment + "<br>"

                Response = "<p>INFORMACIÓN ACERCA DEL MUSEO CON ID: " + recurso + "</br></p>"
                Response += "<a href=" + i.content_url + ">" + i.nombre + "</a><br>"
                Response += "Descripción: " + descripcion + "</br>"
                Response += "Accesibilidad: " + acces + "</br>"
                Response += "Localización: " + via + " " + localizacion + ", nº " + str(num)
                Response += " " + localidad + " (" + str(codigo_postal) + ")</br>"
                Response += "Ubicación: " + barrio + " " + distrito + " Coordenadas: " + str(coordenada_x) + " , " + str(coordenada_y) + "<br><br>"
                Response += "INFORMACIÓN DE CONTACTO </br>"
                Response += "Teléfono: " + telefono + "</br>"
                Response += "Email: " + email + "</br>" + list_coments + "</ol>"
                if num_megusta != 0:
                    Response += "</br><li>Numero de me gustas es: " + str(num_megusta) + "<br>"
                else:
                    Response += "</br><li>Se el primero en indicar que te gusta la página<br>"

        if request.user.is_authenticated():
            username = str(request.user)
            form_user = 'Bienvenido ' + username
            form_user += '<br><br><a href="http://127.0.0.1:8000/logout" > Logout </a>'

            formulario = '<form action="" method="POST">'
            formulario += '<br>Puede introducir un comentario si lo desea ' + str(request.user) + '<br><input type="text" name="Comentario">'
            formulario += '<input type="submit" value="Comentar"></form>'
            Response += formulario

        else:
            form_user = "Para entrar en su cuenta vaya al botón de Inicio."

        megusta = ''
        megusta += '<br> Indica que te gusta este museo</br>'
        megusta += '<form action="" method="POST">'
        megusta += '<button type="submit" name="Me Gusta" value="Me Gusta"> +1 </button></form>'
        Response += megusta

    except ObjectDoesNotExist:
        Response = "El id introducido no se corresponde con ningún museo"

    c = Context({'lista': Response, 'login': form_user})
    renderizado = template.render(c)
    return HttpResponse(renderizado)

def usuarios_xml(request, peticion):
	user_object = User.objects.get(username=peticion)
	doc = Document()
	cont = doc.createElement("Contenidos")
	doc.appendChild(cont)
	info = doc.createElement("infoDataset")
	cont.appendChild(info)
	nombre = doc.createElement("Nombre")
	info.appendChild(nombre)
	ptext = doc.createTextNode("XML de museos seleccionados por el usuario " + peticion)
	nombre.appendChild(ptext)
	url = doc.createElement("url")
	info.appendChild(url)
	ptext = doc.createTextNode("http://127.0.0.1:8000/" + peticion + "/xml/")
	url.appendChild(ptext)
	mus = doc.createElement("Museos")
	cont.appendChild(mus)

	try:
		usuario = Usuario.objects.get(nombre=user_object)
		lista_seleccionados = Seleccionados.objects.filter(selector=usuario)

		for i in lista_seleccionados:
			item = doc.createElement("Contenido")
			mus.appendChild(item)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "ID-ENTIDAD")
			ptext = doc.createTextNode(i.museo.entidad)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "NOMBRE")
			ptext = doc.createTextNode(i.museo.nombre)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "DESCRIPCION")
			ptext = doc.createTextNode(i.museo.descripcion)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "ACCESIBILIDAD")
			if i.museo.accesibilidad == True:
				acces = 1
			else:
				acces = 0
			ptext = doc.createTextNode(str(acces))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CONTENT_URL")
			ptext = doc.createTextNode(i.museo.content_url)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "LOCALIZACION")
			ptext = doc.createTextNode(i.museo.localizacion)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CLASE VIAL")
			ptext = doc.createTextNode(i.museo.clase_vial)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "TIPO NUM")
			ptext = doc.createTextNode(i.museo.tipo_num)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "NUM")
			ptext = doc.createTextNode(str(i.museo.num))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "LOCALIDAD")
			ptext = doc.createTextNode(i.museo.localidad)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "PROVINCIA")
			ptext = doc.createTextNode(i.museo.provincia)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CODIGO POSTAL")
			ptext = doc.createTextNode(str(i.museo.codigo_postal))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "BARRIO")
			ptext = doc.createTextNode(i.museo.barrio)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "DISTRITO")
			ptext = doc.createTextNode(i.museo.distrito)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "COORDENADA X")
			ptext = doc.createTextNode(str(i.museo.coordenada_x))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "COORDENADA Y")
			ptext = doc.createTextNode(str(i.museo.coordenada_y))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			datos = doc.createElement("DATOSDECONTACTO")
			item.appendChild(datos)
			atributo = doc.createElement("atributo")
			datos.appendChild(atributo)
			atributo.setAttribute("nombre", "TELEFONO")
			ptext = doc.createTextNode(i.museo.telefono)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			datos.appendChild(atributo)
			atributo.setAttribute("nombre", "EMAIL")
			ptext = doc.createTextNode(i.museo.email)
			atributo.appendChild(ptext)
	except:
		print("")

	xml = doc.toprettyxml(indent=" ")
	return HttpResponse(xml, content_type = "text/xml")

def about(request):
    template = get_template("about.html")

    Cuerpo = "Práctica realizada por Elena Benito del Pino.<br><br>"
    Cuerpo += "-------FUNCIONAMIENTO DE LA APLICACIÓN-------<br><br>"
    Cuerpo += "<li> Esta web muestra los 5 museos de Madrid que tengan más comentarios en la página principal, "
    Cuerpo += "una lista de usuarios y un botón 'Accesibiles' que nos muestra sólo los museos que son accesibles.</li><br><br>"
    Cuerpo += "<li> A través de la opción 'Todos' del menú puede acceder a la lista de todos los museos disponibles en la base de datos, "
    Cuerpo += "con el nombre del museo y un enlace 'Más información' para acceder a la página del museo en la aplicación. "
    Cuerpo += "En la página del museo aparece el nombre, un párrafo con información, los comentarios que tuviera y un botón para indicar si le gusta.</li>"
    Cuerpo += "<li> Siempre se puede volver a la página principal pulsando la opción 'Inicio' del menú. </li>"
    Cuerpo += "<li> La opción 'About' del menú nos muestra esta explicación de la práctica.</li></br></br>"
    Cuerpo += "<li> Cada usuario tiene una interfaz pública que se puede visitar a través de los enlaces en "
    Cuerpo += "el listado de 'Páginas de usuarios' donde se muestran los museos seleccionados por ese usuario de 5 en 5.</li><br><br>"
    Cuerpo += "<li> Los usuarios que se registren también tendrán una interfaz privada a la que acceden con su usuario y contraseña "
    Cuerpo += " desde la página principal, en la que podrán cambiar el estilo del sitio del usuario y elegir el título de su página."
    Cuerpo += " También podrán añadir a su lista los museos que seleccionen y escribir comentarios en las páginas de los museos.</li><br><br>"
    Cuerpo += "<li> En el recurso /usuario/xml cualquiera puede consultar el documento XML con todos los museos seleccionados por el usuario.</li><br><br>"
    Cuerpo += "<li> Pulsando en el pie de página puede acceder al portal de datos abiertos del Ayuntamiento de Madrid, "
    Cuerpo += "donde hemos obtenido nuestra base de datos, y también al fichero xml con los datos.</li>"

    c = Context({'lista': Cuerpo})
    renderizado = template.render(c)

    return HttpResponse(renderizado)
