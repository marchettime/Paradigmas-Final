#!/usr/bin/env python
import csv
import re #Importamos re que es una libreria que tiene validadores por Expresiones Regulares. Esto nos sirve para validar los campos
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
# from flask_moment import Moment | Comentado por Colombo
from flask_script import Manager
from forms import LoginForm, SaludarForm, RegistrarForm, BuscarForm # , BuscarOpcionForm
#Import para verificar si existe el archivo ventas que vamos a usar para procesar:
import os.path
#Generamos un archivo que tenga las clases generadas por nosotros y las cargamos para su uso con un from
from classes import LineaTabla
#Numpy nos permite sumar, agrupar, sacar listas unicas (para el criterio de filtros viene como trompada) y otros menesteres.
import numpy as np
#Permite inteligencia de datos
import pandas as pd
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
# moment = Moment(app)
app.config['SECRET_KEY'] = 'un string que funcione como llave'
#String que funciona como llave
tablaRegistros = None
tablaFiltrada = None
ultimasVentas = None
mensajesErrores = []

@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow(), errores = mensajesErrores)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    if 'username' not in session:
        formulario = LoginForm()
        if formulario.validate_on_submit():
            with open('usuarios') as archivo:
                archivo_csv = csv.reader(archivo)
                registro = next(archivo_csv)#next toma el primer registro
                while registro:
                    if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                        flash('Bienvenido') #flash es cola de mensaje
                        session['username'] = formulario.usuario.data
                        if len(mensajesErrores) == 0:
                            return render_template('ingresado.html', ultimasVentas = ultimasVentas)
                        else: 
                            return render_template('ingresado.html', errores = mensajesErrores)
                    registro = next(archivo_csv, None)
                else:
                    flash('Revisá nombre de usuario y contraseña')
                    return redirect(url_for('ingresar'))
        return render_template('login.html', formulario=formulario)
    else:
        return render_template('ingresado.html', ultimasVentas = ultimasVentas, errores = mensajesErrores)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if 'username' in session and session['username'] == 'admin':
        formulario = RegistrarForm()
        if formulario.validate_on_submit():
            if formulario.password.data == formulario.password_check.data:
                with open('usuarios', 'a+') as archivo:
                    archivo_csv = csv.writer(archivo)
                    registro = [formulario.usuario.data, formulario.password.data]
                    archivo_csv.writerow(registro)
                flash('Usuario creado correctamente')
                return redirect(url_for('ingresar'))
            else:
                flash('Las passwords no matchean')
        return render_template('registrar.html', form=formulario, errores = mensajesErrores)
    else:
        return render_template('sin_permiso.html')

    
@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return render_template('sin_permiso.html')   

 
###INICIO DE PARCIAL###
#/ProdsByClient - Productos por Cliente
@app.route('/ProdsByClient', methods=['GET','POST'])
def productosPorCliente():
    if 'username' in session:
        if len(mensajesErrores) == 0:
            formularioBuscar = BuscarForm()
            # 
            #Me baso en buscar si se completo una seleccion mediante el post
            #esto nos permitira forzar la busqueda al unico registro encontrado!
            if request.method == 'POST' and request.form.get('seleccion') != None:
                formularioBuscar.palabra.data = str(request.form.get('seleccion')) #va el nombre del select
                
            if request.method == 'POST' and len(formularioBuscar.palabra.data)>=3:
                #Concepto de Filtrado: se declara un tipo de variable, para que busque en una tabla, segun los atributos de su clase.
                tablaFiltrada = [row for row in tablaRegistros if formularioBuscar.palabra.data.upper() in row.cliente.upper()]
                #Con  numpy podemos hacer selecciones de diverso tipo en arrays, aca hacemos que nos traiga los unicos de un valor! :)
                clientes = []
                for informacion in tablaFiltrada:
                    clientes.append(informacion.cliente)
                unicos = np.unique(clientes)
                #En caso de Detectar un valor demas, hacemos que vaya e impacte la tabla
                if len(clientes) == 1: #SI hay uno mando la tabla
                    return render_template('ProdsByClient.html', formulario=formularioBuscar, filtro=formularioBuscar.palabra.data, filas=tablaFiltrada, opciones=unicos)
                else: 
                    #mostrar productos:
                    return render_template('ProdsByClient.html', formulario=formularioBuscar, filas=tablaFiltrada, filtro=formularioBuscar.palabra.data, opciones=unicos)
            else:
                flash('Recuerde que el filtro debe contener al menos 3 caracteres')
                return render_template('ProdsByClient.html', formulario=formularioBuscar)
        else:
            return render_template('sin_datos.html', errores = mensajesErrores)
    else:
        return render_template('sin_permiso.html')
    
#/ClientsByProd - Clientes con sus productos    
@app.route('/ClientsByProd', methods=['GET','POST'])
def clientesPorProducto():
    if 'username' in session:
        if len(mensajesErrores) == 0:
            formularioBuscar = BuscarForm()
            # 
            #Me baso en buscar si se completo una seleccion mediante el post
            #esto nos permitira forzar la busqueda al unico registro encontrado!
            if request.method == 'POST' and request.form.get('seleccion') != None:
                formularioBuscar.palabra.data = str(request.form.get('seleccion')) #va el nombre del select
                
            if request.method == 'POST' and len(formularioBuscar.palabra.data)>=3:
                #Concepto de Filtrado: se declara un tipo de variable, para que busque en una tabla, segun los atributos de su clase.
                tablaFiltrada = [row for row in tablaRegistros if formularioBuscar.palabra.data.upper() in row.producto.upper()]
                #Genero un array para filtrar si hay mas de un producto... lo voy a poner asi para despues mandarlo a filtrar por usuario
                productos = []
                for informacion in tablaFiltrada:
                    productos.append(informacion.producto)
                #Con  numpy podemos hacer selecciones de diverso tipo en arrays, aca hacemos que nos traiga los unicos de un valor! :)
                unicos = np.unique(productos)
                #En caso de Detectar un valor demas, hacemos que vaya e impacte la tabla
                if len(productos) == 1: #SI hay uno mando la tabla
                    return render_template('ClientsByProd.html', formulario=formularioBuscar, filas=tablaFiltrada, filtro=formularioBuscar.palabra.data, opciones=unicos)
                else: 
                    return render_template('ClientsByProd.html', formulario=formularioBuscar, filas=tablaFiltrada, filtro=formularioBuscar.palabra.data, opciones=unicos)
            else:
                flash('Recuerde que el filtro debe contener al menos 3 caracteres')
                return render_template('ClientsByProd.html', formulario=formularioBuscar)
        else:
            return render_template('sin_datos.html', errores = mensajesErrores)
    else:
        return render_template('sin_permiso.html')


#/MostSoldProds - N Productos mas vendidos
@app.route('/MostSoldProds', methods=['GET'])
def productosMasVendidos():
    if 'username' in session:
        if len(mensajesErrores) == 0:
            #Buscar segun suma!
            #Paso a un array las cantidades y los codigos de productos para mapearlos con el numpy. Es buena practica? Y... por ahora no se me ocurre otra.
            listaProds = []
            cantidades = []
            for registro in tablaRegistros:
                listaProds.append(registro.codigo + '-' + registro.producto)
                cantidades.append(int(registro.cantidad))
            listado = pd.DataFrame({'producto': listaProds, 'cantidad': cantidades})
            listaSumarizada = listado.groupby('producto').sum().sort_values(by=['cantidad'], ascending=False).head(5)
            
            listaProds = listaSumarizada.reset_index()[['producto', 'cantidad']].values.tolist()
    
            return render_template('MostSoldProds.html', filas=listaProds)
        else:
            return render_template('sin_datos.html', errores = mensajesErrores)
    else:
        return render_template('sin_permiso.html')
  

#/BestClients - Mejores Clientes (Pedidos mas grandes)
@app.route('/BestClients', methods=['GET'])
def mejoresClientes():
    if 'username' in session:
        if len(mensajesErrores) == 0:
            #Buscar segun suma!
            #Paso a un array las cantidades y los codigos de productos para mapearlos con el numpy. Es buena practica? Y... por ahora no se me ocurre otra.
            listaClientes = []
            montos = []
            for registro in tablaRegistros:
                listaClientes.append(registro.cliente)
                montos.append(int(registro.cantidad)*float(registro.precioUnitario))
            listado = pd.DataFrame({'Cliente': listaClientes, 'Montos': montos})
            listaSumarizada = listado.groupby('Cliente').sum().sort_values(by=['Montos'], ascending=False).head(5)
            
            listaClientes = listaSumarizada.reset_index()[['Cliente', 'Montos']].values.tolist()
            
            return render_template('BestClients.html', filas=listaClientes)
        else:
            return render_template('sin_datos.html', errores = mensajesErrores)
    else:
        return render_template('sin_permiso.html')
   
    
def cargaArchivo(): #Guardamos el archivo en una Matriz
    #generar matriz de datos | Cabeceras: CODIGO,PRODUCTO,CLIENTE,CANTIDAD,PRECIO
    cabeceras = ['','','','','']
    nroLinea = -1
    muestra = LineaTabla('','','','','')
    listaDelArchivo = []
   
    with open('ventas') as archivo: #carga de archivo de ventas
        archivo_csv = csv.reader(archivo)
        registro = next(archivo_csv)#next toma el primer registro
        while registro != None:
            nroLinea = nroLinea + 1#si hay un problema con el archivo, no vamos a poder cargar nada, y deberia de haber una excepcion. Esto nos ayuda a controlar los registros. (desp veremos el por qué)
            if validacionCantidadColumnas(registro, nroLinea+1):#validarRegistro(registro) Ponemos +1 porque es para el msj de error
                if nroLinea == 0:
                    cabeceras[0] = registro[0]
                    cabeceras[1] = registro[1]
                    cabeceras[2] = registro[2]
                    cabeceras[3] = registro[3]
                    cabeceras[4] = registro[4] 
                else: #bifurcador de validaciones    
                    i = 0
                    while i < 5:
                        if cabeceras[i] == 'CODIGO':
                            if validacionCampoCodigo(registro[i], nroLinea+1):#Ponemos +1 porque es para el msj de error
                                muestra.codigo=registro[i]
                        elif cabeceras[i] == 'PRODUCTO':
                            muestra.producto=registro[i]
                        elif cabeceras[i] == 'CLIENTE':
                            muestra.cliente=registro[i]
                        elif cabeceras[i] == 'CANTIDAD':
                            if validacionCampoCantidad(registro[i], nroLinea+1):#Ponemos +1 porque es para el msj de error
                                muestra.cantidad=registro[i]
                        elif cabeceras[i] == 'PRECIO':
                            if validacionCampoPrecio(registro[i], nroLinea+1):#Ponemos +1 porque es para el msj de error
                                muestra.precioUnitario=registro[i]
                        else:
                            msjError = 'La columna informada no corresponde a un valor esperado'
                            mensajesErrores.append(msjError)
                            print(mensaje)
                        i = i + 1
                    if muestra.codigo != '' and muestra.producto != '' and  muestra.cliente != '' and  muestra.cantidad != '' and  muestra.precioUnitario != '':
                        listaDelArchivo.append(LineaTabla(muestra.codigo,muestra.producto, muestra.cliente, muestra.cantidad, muestra.precioUnitario))
                    muestra = LineaTabla('','','','','')
            registro = next(archivo_csv, None)

    #Finalizada la carga, validamos el largo de lo que cargamos, no sea inferior al archivo leido
    print("Registros en Archivo:", nroLinea, "| Registros Procesados OK:", len(listaDelArchivo))
    if len(listaDelArchivo)< nroLinea:
        mensaje = "Registros en Archivo: {0} | Registros Procesados OK: {1}".format(nroLinea, len(listaDelArchivo))
        #mensaje = ("Registros en Archivo:", nroLinea, "| Registros Procesados OK:", len(listaDelArchivo))
        mensajesErrores.append(mensaje)
        return None
    else:
        return listaDelArchivo

    
def validacionCantidadColumnas(registro, nroLinea): #Que sean 5. Y, que ninguna sea repetida.
    if len(registro) != 5:
        msjError = "Error en cantidad de columnas en la linea {0}!".format(nroLinea)
        mensajesErrores.append(msjError)
        print(msjError)
        return False
    return True
    
def validacionCampoCodigo(campo, nroLinea): #Valida el formato no admite nulo y 3 Letras + 3 numeros (validar que los primeros tres sea tipo string y los ultimos 3 sean numeros. no se debe extender de mas de 6 caracteres.
    #Aca usamos 're' que fue importado al principio para utilizar expresion regular al momento de validar el campo
    if len(campo) == 6 and re.fullmatch(r'[A-Z]+',campo[0:3]) and re.fullmatch(r'[0-9]+',campo[3:6]):
        return True
    else:
        msjError = ("El campo \"CÓDIGO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErrores.append(msjError)
        return False

def validacionCampoCantidad(campo, nroLinea): #Sólo pueden haber enteros
    if re.fullmatch(r'[0-9]+',campo):
        return True
    else:
        #print("El campo \"CANTIDAD\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        msjError = ("El campo \"CANTIDAD\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErrores.append(msjError)
        return False

def validacionCampoPrecio(campo, nroLinea): #Flotante con 2 decimales
    if re.fullmatch(r'[0-9]+(\.[0-9][0-9]?)?',campo):
        return True
    else:
        #print("El campo \"PRECIO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        msjError = ("El campo \"PRECIO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErrores.append(msjError)
        return False
  
if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    
    if os.path.isfile('ventas'): #Con esta libreria nos permite verificar la existencia del archivo
        tablaRegistros = cargaArchivo()
        if tablaRegistros != None: #Si la lista del archivo no devuelve vacio, mostramos la data:
            ultimasVentas = reversed(tablaRegistros[len(tablaRegistros)-10:])
        else:
            print("No se pudo procesar el archivo!!!")
            #mensajesErrores.append("No se pudo procesar el archivo!!!")
    else:
        #print("El archivo no existe")
        mensajesErrores.append("El archivo no existe")
    
    #Impresion de errores por consola que se hayan acumulado. Ojo, esto nos va a servir para controlar los errores generales
    for error in mensajesErrores:
        print(error)
    
    manager.run() #Cargado todo, inicializamos el servidor.
    
    
