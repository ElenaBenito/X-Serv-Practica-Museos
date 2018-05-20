from django.shortcuts import render
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from .models import *
import urllib.request
import sys


def normalize_whitespace(text):
	string = ""
	result = string.join(text)
	return result

class myContentHandler(ContentHandler):
	def __init__ (self):
		self.inItem = False
		self.inContent = False
		self.theContent = ""
		self.entidad = ""
		self.nombre = ""
		self.descripcion = ""
		self.accesibilidad = ""
		self.contenturl = ""
		self.first = True
		self.nombrevia = ""
		self.clasevial = ""
		self.tiponum = ""
		self.num = ""
		self.localidad = ""
		self.provincia = ""
		self.codigopostal = ""
		self.barrio = ""
		self.distrito= ""
		self.coordenadax = ""
		self.coordenaday= ""
		self.latitud = ""
		self.longitud = ""
		self.telefono = ""
		self.email = ""
		self.attr = ""
		self.url = False

	def startElement (self, name, attrs):
		if name == 'contenido':
			self.inItem = True
		if self.inItem:
			if name == 'atributo':
				self.attr = normalize_whitespace(attrs.get('nombre'))

				if self.attr == "ID-ENTIDAD":
					self.inContent = True
				elif self.attr ==  "NOMBRE":
					self.inContent = True
				elif self.attr ==  "DESCRIPCION":
					self.inContent = True
				elif self.attr == "ACCESIBILIDAD":
					self.inContent = True
				elif self.attr == "CONTENT-URL":
					self.url = True
					self.inContent = True
				elif self.attr == "NOMBRE-VIA":
					self.inContent = True
				elif self.attr == "CLASE-VIAL":
					self.inContent = True
				elif self.attr == "TIPO-NUM":
					self.inContent = True
				elif self.attr == "NUM":
					self.inContent = True
				elif self.attr == "LOCALIDAD":
					self.inContent = True
				elif self.attr == "PROVINCIA":
					self.inContent = True
				elif self.attr == "CODIGO-POSTAL":
					self.inContent = True
				elif self.attr == "BARRIO":
					self.inContent = True
				elif self.attr == "DISTRITO":
					self.inContent = True
				elif self.attr == "COORDENADA-X":
					self.inContent = True
				elif self.attr == "COORDENADA-Y":
					self.inContent = True
				elif self.attr == "DATOSCONTACTOS":
					self.inContent = True
				elif self.attr == "TELEFONO":
					self.inContent = True
				elif self.attr == "EMAIL":
					self.inContent = True


	def endElement (self, name):
		if self.inContent:
			self.theContent = normalize_whitespace(self.theContent)

		if self.attr == "ID-ENTIDAD":
			self.entidad = self.theContent
			self.theContent = ""
		elif self.attr == "NOMBRE":
			self.nombre = self.theContent
			self.theContent = ""
		elif self.attr == "DESCRIPCION":
			self.descripcion = self.theContent
			self.theContent = ""
		elif self.attr == "ACCESIBILIDAD":
			self.accesibilidad = self.theContent
			self.theContent = ""
		elif self.attr == "CONTENT-URL":
			self.contenturl = normalize_whitespace(self.theContent)
			self.url = False
			self.first = False
			self.theContent = ""
		elif self.attr == "NOMBRE-VIA":
			self.nombrevia = self.theContent
			self.theContent = ""
		elif self.attr == "CLASE-VIAL":
			self.clasevial = self.theContent
			self.theContent = ""
		elif self.attr == "TIPO-NUM":
			self.tiponum = self.theContent
			self.theContent = ""
		elif self.attr == "NUM":
			self.num = self.theContent
			self.theContent = ""
		elif self.attr == "LOCALIDAD":
			self.localidad = self.theContent
			self.theContent = ""
		elif self.attr == "PROVINCIA":
			self.provincia = self.theContent
			self.theContent = ""
		elif self.attr == "CODIGO-POSTAL":
			self.codigopostal = self.theContent
			self.theContent = ""
		elif self.attr == "BARRIO":
			self.barrio = self.theContent
			self.theContent = ""
		elif self.attr == "DISTRITO":
			self.distrito = self.theContent
			self.theContent = ""
		elif self.attr == "COORDENADA-X":
			self.coordenadax = self.theContent
			self.theContent = ""
		elif self.attr == "COORDENADA-Y":
			self.coordenaday = self.theContent
			self.theContent = ""
		elif self.attr == "DATOSCONTACTOS":

			p = Museo(entidad=self.entidad, nombre=self.nombre, descripcion=self.descripcion, accesibilidad=self.accesibilidad, content_url=self.contenturl, localizacion=self.nombrevia, clase_vial=self.clasevial, tipo_num=self.tiponum, num=self.num, localidad=self.localidad, provincia=self.provincia, codigo_postal=self.codigopostal, barrio=self.barrio, distrito=self.distrito, coordenada_x=self.coordenadax, coordenada_y=self.coordenaday, telefono=self.telefono, email=self.email)
			p.save()

		if self.attr == "TELEFONO":
			self.attr = "DATOSCONTACTOS"
			self.telefono = self.theContent
			self.theContent = ""
		elif self.attr == "EMAIL":
			self.attr = "DATOSCONTACTOS"
			self.email = self.theContent
			self.theContent = ""

	def characters (self, chars):
		if self.inContent:
			if self.url:
				if self.first == True:
					self.theContent = self.theContent + chars
				else:
					self.first = True
					self.theContent = chars
			else:
				self.theContent = chars


def get_data():
	theParser = make_parser()
	theHandler = myContentHandler()
	theParser.setContentHandler(theHandler)

	url = 'https://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?'
	url += 'vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=201132-0-'
	url += 'museos&mgmtid=118f2fdbecc63410VgnVCM1000000b205a0aRCRD&preview=full'
	xmlFile = urllib.request.urlopen(url)
	theParser.parse(xmlFile)

	return("Parser completed")
