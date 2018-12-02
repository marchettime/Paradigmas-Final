import csv
import re #Importamos re que es una libreria que tiene validadores por Expresiones Regulares. Esto nos sirve para validar los campos
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
from flask_script import Manager
from forms import LoginForm, SaludarForm, RegistrarForm, BuscarForm, AltaVentaForm
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
app.config['SECRET_KEY'] = 'un string que funcione como llave'
#String que funciona como llave
tablaRegistros = None
tablaFiltrada = None
ultimasVentas = None
mensajesErroresArchivo = []
cabeceras = ['','','','',''] #Lo defino global adrede porque lo tengo que tener en cuenta al momento de grabar!

@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow(), errores = mensajesErroresArchivo)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html', errores=mensajesErroresArchivo), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html', errores=mensajesErroresArchivo), 500



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
                        return redirect(url_for('ultimasVentas'))
                    registro = next(archivo_csv, None)
                else:
                    flash('Revisá nombre de usuario y contraseña')
                    return redirect(url_for('ingresar'))
        return render_template('login.html', formulario=formulario)
    else:
        return redirect(url_for('ultimasVentas'))


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if 'username' in session and session['username'] == 'admin':
        formulario = RegistrarForm()
        if formulario.validate_on_submit():
            if formulario.password.data == formulario.password_check.data:
                with open('usuarios', 'a+') as archivo:
                    archivo_csv = csv.writer(archivo, lineterminator="\n")
                    registro = [formulario.usuario.data, formulario.password.data]
                    archivo_csv.writerow(registro)
                flash('Usuario creado correctamente')
                return redirect(url_for('ingresar'))
            else:
                flash('Las passwords no matchean')
        return render_template('registrar.html', form=formulario, errores = mensajesErroresArchivo)
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

###INICIO DE FINAL###
@app.route('/LatestSales', methods=['GET','POST'])
def ultimasVentas():
    if 'username' in session:
        tablaRegistros = cargaArchivo() #Vuelvo a procesar el archivo y lo traigo a memoria. No solo yo puedo estar trabajando agregando registros.
        if len(mensajesErroresArchivo) == 0: #como no asumo que sea valido porque puede ser que aparecio otro, valido, si esta OK, corto los ultimos 5.
            if tablaRegistros != None: #Si la lista del archivo no devuelve vacio, mostramos la data:
                ultimasVentas = reversed(tablaRegistros[len(tablaRegistros)-5:])
            return render_template('LatestSales.html', ultimasVentas = ultimasVentas)
        else:
            return render_template('sin_datos.html', errores = mensajesErroresArchivo)
    else:
        return render_template('sin_permiso.html') 

@app.route('/AddSale', methods=['GET', 'POST'])
def agregarVenta():
    if 'username' in session:
        formulario = AltaVentaForm()
        if request.method == 'GET':
            return render_template('AddSale.html', formulario=formulario)
        else: 
            if request.method == 'POST' and formulario.validate():
                venta = LineaTabla('','','','','') #Genero una clase para pasar los datos del formulario(no hay necesiadad pero, es mas prolijo a mi gusto)
                ventaOrdenado = ['','','','',''] #Generamos un vector posicional para importar a la base, nos sirve para poner segun la cabecera
                venta.codigo = formulario.codigo.data.upper()       #Traslado de dato de formulario a objeto venta
                venta.producto = formulario.producto.data    #Traslado de dato de formulario a objeto venta
                venta.cantidad = formulario.cantidad.data    #Traslado de dato de formulario a objeto venta
                venta.precioUnitario = formulario.precio.data#Traslado de dato de formulario a objeto venta
                venta.cliente = formulario.nombreCliente.data#Traslado de dato de formulario a objeto venta
                i = 0
                while i < 5: #comparo valores y los importo segun corresponda al orden de aparicion de la CABECERA
                    if cabeceras[i] == 'CODIGO':
                        ventaOrdenado[i] = venta.codigo
                    elif cabeceras[i] == 'PRODUCTO':
                        ventaOrdenado[i] = venta.producto
                    elif cabeceras[i] == 'CLIENTE':
                        ventaOrdenado[i] = venta.cliente
                    elif cabeceras[i] == 'CANTIDAD':
                        ventaOrdenado[i] = venta.cantidad
                    elif cabeceras[i] == 'PRECIO':
                        ventaOrdenado[i] = venta.precioUnitario
                    i = i + 1
                
                #Preparado de escritura del archivo. ponemos delimitador de linea para que no rompa por el SO trabajado 
                with open('ventas', 'a+') as archivo:
                    archivo_csv = csv.writer(archivo, lineterminator="\n")#Para que escriba bien el archivo, le demarco el terminador de linea
                    archivo_csv.writerow(ventaOrdenado)
                flash('¡Venta registrada con éxito!') #Mensaje para informar que se hizo todo OK! :)
                return redirect(url_for('ultimasVentas')) #redirecciono a las Ultimas ventas para uqe le muestre todito con el reprocesamiento
            else:
                return render_template('AddSale.html', formulario=formulario) #Si mandamos nuevamente el formulario va a ver los errores!
    else:
        return render_template('sin_permiso.html') 


###INICIO DE PARCIAL###
#/ProdsByClient - Productos por Cliente
@app.route('/ProdsByClient', methods=['GET','POST'])
def productosPorCliente():
    if 'username' in session:
        tablaRegistros = cargaArchivo()
        if len(mensajesErroresArchivo) == 0:
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
            return render_template('sin_datos.html', errores = mensajesErroresArchivo)
    else:
        return render_template('sin_permiso.html')
    
#/ClientsByProd - Clientes con sus productos    
@app.route('/ClientsByProd', methods=['GET','POST'])
def clientesPorProducto():
    if 'username' in session:
        tablaRegistros = cargaArchivo()
        if len(mensajesErroresArchivo) == 0:
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
            return render_template('sin_datos.html', errores = mensajesErroresArchivo)
    else:
        return render_template('sin_permiso.html')


#/MostSoldProds - N Productos mas vendidos
@app.route('/MostSoldProds', methods=['GET'])
def productosMasVendidos():
    if 'username' in session:
        tablaRegistros = cargaArchivo()
        if len(mensajesErroresArchivo) == 0:
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
            return render_template('sin_datos.html', errores = mensajesErroresArchivo)
    else:
        return render_template('sin_permiso.html')
  

#/BestClients - Mejores Clientes (Pedidos mas grandes)
@app.route('/BestClients', methods=['GET'])
def mejoresClientes():
    if 'username' in session:
        tablaRegistros = cargaArchivo()
        if len(mensajesErroresArchivo) == 0:
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
            return render_template('sin_datos.html', errores = mensajesErroresArchivo)
    else:
        return render_template('sin_permiso.html')
   
    
def cargaArchivo(): #Guardamos el archivo en una Matriz
    nroLinea = -1
    LineaVenta = LineaTabla('','','','','')
    listaDelArchivo = []
    mensajesErroresArchivo.clear()
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
                                LineaVenta.codigo=registro[i]
                        elif cabeceras[i] == 'PRODUCTO':
                            LineaVenta.producto=registro[i]
                        elif cabeceras[i] == 'CLIENTE':
                            LineaVenta.cliente=registro[i]
                        elif cabeceras[i] == 'CANTIDAD':
                            if validacionCampoCantidad(registro[i], nroLinea+1):#Ponemos +1 porque es para el msj de error
                                LineaVenta.cantidad=registro[i]
                        elif cabeceras[i] == 'PRECIO':
                            if validacionCampoPrecio(registro[i], nroLinea+1):#Ponemos +1 porque es para el msj de error
                                LineaVenta.precioUnitario=registro[i]
                        else:
                            msjError = 'La columna informada no corresponde a un valor esperado'
                            mensajesErroresArchivo.append(msjError)
                            print(mensaje)
                        i = i + 1
                    if LineaVenta.codigo != '' and LineaVenta.producto != '' and  LineaVenta.cliente != '' and  LineaVenta.cantidad != '' and  LineaVenta.precioUnitario != '':
                        listaDelArchivo.append(LineaVenta)
                    LineaVenta = LineaTabla('','','','','')
            registro = next(archivo_csv, None)

    #Finalizada la carga, validamos el largo de lo que cargamos, no sea inferior al archivo leido
    print("Registros en Archivo:", nroLinea, "| Registros Procesados OK:", len(listaDelArchivo))
    if len(listaDelArchivo)< nroLinea:
        #impresion en consola:
        for msjError in mensajesErroresArchivo:
            print (" ♦ {0}".format(msjError))
        mensaje = "Registros en Archivo: {0} | Registros Procesados OK: {1}".format(nroLinea, len(listaDelArchivo))
        mensajesErroresArchivo.append(mensaje)
        return None
    else:
        return listaDelArchivo

    
def validacionCantidadColumnas(registro, nroLinea): #Que sean 5. Y, que ninguna sea repetida.
    if len(registro) != 5:
        msjError = "Error en cantidad de columnas en la linea {0}!".format(nroLinea)
        mensajesErroresArchivo.append(msjError)
        print(msjError)
        return False
    return True
    
def validacionCampoCodigo(campo, nroLinea): #Valida el formato no admite nulo y 3 Letras + 3 numeros (validar que los primeros tres sea tipo string y los ultimos 3 sean numeros. no se debe extender de mas de 6 caracteres.
    #Aca usamos 're' que fue importado al principio para utilizar expresion regular al momento de validar el campo
    if len(campo) == 6 and re.fullmatch(r'[A-Z]+',campo[0:3]) and re.fullmatch(r'[0-9]+',campo[3:6]):
        return True
    else:
        msjError = ("El campo \"CÓDIGO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErroresArchivo.append(msjError)
        return False

def validacionCampoCantidad(campo, nroLinea): #Sólo pueden haber enteros
    if re.fullmatch(r'[0-9]+',campo):
        return True
    else:
        #print("El campo \"CANTIDAD\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        msjError = ("El campo \"CANTIDAD\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErroresArchivo.append(msjError)
        return False

def validacionCampoPrecio(campo, nroLinea): #Flotante con 2 decimales
    if re.fullmatch(r'[0-9]+(\.[0-9][0-9]?)?',campo):
        return True
    else:
        #print("El campo \"PRECIO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        msjError = ("El campo \"PRECIO\" de la Línea {0} no cumple con el formato necesario!".format(nroLinea))
        mensajesErroresArchivo.append(msjError)
        return False
 
 
if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    if os.path.isfile('ventas'): #Con esta libreria nos permite verificar la existencia del archivo
        if os.stat("ventas").st_size == 0:
            mensajesErroresArchivo.append("× El archivo se encuentra VACIO")
        else:
            tablaRegistros = cargaArchivo()
    else:
        mensajesErroresArchivo.append("× El archivo no existe")
    #Impresion de errores por consola que se hayan acumulado. Ojo, esto nos va a servir para controlar los errores generales
    for error in mensajesErroresArchivo:
        print(error)
    manager.run() #Cargado todo, inicializamos el servidor.
    
    
