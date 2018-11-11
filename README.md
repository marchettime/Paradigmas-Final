# Parcial de Paradigmas de Programación
#
#• A grandes rasgos, ¿cómo será el flujo del programa?
#Una vez habilitado el servidor y habiendose cargado un archivo de Ventas válido, El usuario ingresará al Link "http://localhost:5000/".
#Allí tendrá una pantalla de inicio con un mensaje de bienvenida, y una opcion de Login.
#
#De ingresar como Administrador (usuario: admin) tendrá en su barra de navegación la opcion de dar de alta usuarios.
#El resto de los usuarios contará con:
# - Productos X Cliente
# - Clientes X Producto
# - Productos Más Vendidos
# - Mejores Clientes
# - Salir
#En las primeras dos, se encontrara con un filtro de texto a aplicar, correspondiente al cliente o producto, segun corresponda, y en caso de encontrar más de un item, tendra un desplegable para obtener el resultado deseado.
#Las otras dos opciones, permitirà al usuario obtener un top 5 de los productos con mayor cantidad de ventas; y el de clientes, los que mayores compras hayan registrado en el archivo de ventas.
#• ¿Qué estructura se utilizará para representar la información del archivo?
#La estructura de representacion, mostrara al archivo con las columnas: CODIGO, PRODUCTO, CLIENTE, CANTIDAD, PRECIO UNITARIO. 
#No obstante, segun la pantalla en la que se encuentre, podrá ver totales de compra o por producto que se hayan pedido.
#
#La estructura de presentacion, es independiente a cómo se encuentren las estructuras del archivo "ventas" que se usa como entrada. 
#El mismo sera validado tanto en su estructura como los tipos de datos informados, segun lo solicitado en las consignas y propuesta funcional.
#
#• ¿Cómo se usa el programa?
#El programa se utiliza mediante un explorador web, el cual mediante el acceso al Link y credenciales validas, tendra distintas opciones en un menu superior.
#Algunas de ellas incluyen filtros.
#• ¿Qué clases y funciones se diseñaron? ¿Por qué?
#Se han diseñado 2 clases: una correspondiente al formulario de Busqueda (debido a que se reutilizó para la aplicación de filtros, y otra para determinar la estructura de la lista/tabla que ha sido creada para la administración de la infomación.
#En cuanto a funciones/metodos: se generó una para la carga del archivo de ventas, y otras para validación de estructura (validacionCantidadColumnas) y columnas informadas (validacion del campo código con: CampoCodigo y otras llamadas validacionCampoPrecio y validacionCampoCantidad respectivamente )