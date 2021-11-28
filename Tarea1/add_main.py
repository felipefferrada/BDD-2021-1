import cx_Oracle

connection = cx_Oracle.connect("ADMIN", "1234", "localhost:1521")
print("Database Version", connection.version)
cursor = connection.cursor()



arch_comunas = open("CasosConfirmadosPorComuna.csv", "r")
arch_comunas.readline()

for linea in arch_comunas:
    
    dato = linea.strip().split(",")
    
    nombre = dato[0]
    codigo = dato[1]
    poblacion = dato[2]
    casos = dato[3]

    entrada = """
        INSERT INTO CASOS_POR_COMUNA (nombre_comuna, codigo_comuna, poblacion, casos_confirmados)
        VALUES (:nombre, :codigo, :poblacion, :casos)
    """
    cursor.execute(entrada, [nombre, codigo, poblacion, casos])
    connection.commit()

arch_comunas.close()



arch_regiones = open("RegionesComunas.csv", "r")
arch_regiones.readline()


for linea in arch_regiones:

    datos = linea.strip().split(",")

    region = datos[0]
    codigo_region = datos[1]
    codigo_comuna = datos[2]


    entrada = """
        INSERT INTO CASOS_POR_REGION (nombre_region, codigo_region, codigo_comuna, poblacion, casos_confirmados)
        VALUES (:region, :codigoR, :codigoC, :poblacion, :casos)
    """

    cursor.execute(entrada, [region, codigo_region, codigo_comuna, 0, 0])
    connection.commit()


arch_regiones.close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Lo mejor para esto es usar diccionarios

re_arch_regiones = open("RegionesComunas.csv", "r")
re_arch_regiones.readline()

arch_comunas = open("CasosConfirmadosPorComuna.csv", "r")
arch_comunas.readline()

diccionario = {}
diccionario2 = {}

for linea in re_arch_regiones:
    datos = linea.strip().split(",")

    code_region = datos[1]
    code_comuna = datos[2]

    if code_region not in diccionario:
        diccionario[code_region] = []

    diccionario[code_region].append(code_comuna)


for linea in arch_comunas:
    datos = linea.strip().split(",")

    comuna = datos[1]
    poblacion = datos[2]
    casos = datos[3]

    if  comuna not in diccionario2:
        diccionario2[comuna] = []

    diccionario2[comuna].append(poblacion)
    diccionario2[comuna].append(casos)


diccionario3 = {}

for region in diccionario:
    poblacion_region = 0
    casos_region = 0

    lista_comuna = diccionario[region]
    for comuna in lista_comuna:
        poblacion_comuna = int(diccionario2[comuna][0])
        casos_comuna = int(diccionario2[comuna][1])

        poblacion_region += poblacion_comuna
        casos_region += casos_comuna

    diccionario3[region] = [poblacion_region, casos_region]


for region in diccionario3:
    entrada = """
            UPDATE CASOS_POR_REGION
            SET poblacion = :personas , casos_confirmados = :casos
            WHERE codigo_region = :region
        """
    cursor.execute(entrada, [diccionario3[region][0], diccionario3[region][1], region])

connection.commit()


"""
funciones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ninguna de las funciones reciben parametros, todo lo que sea necesario se pide por pantalla
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

comando_view = """
    CREATE OR REPLACE VIEW regiones_vista AS
    SELECT nombre_region, poblacion, casos_confirmados
    FROM CASOS_POR_REGION
"""
cursor.execute(comando_view)


#comando_trigger = """
#    CREATE OR REPLACE TRIGGER comunas_trigger
#    BEFORE INSERT OR UPDATE
#    ON CASOS_POR_COMUNA
#    FOR EACH ROW
#    BEGIN
#        IF new.casos_confirmados < 0 THEN
#            new.casos_confirmados = 0
#        END IF
#    END comunas_trigger
#"""
#cursor.execute(comando_trigger)

"""
crea una comuna nueva para una region ya existente
"""
def crearComuna():
    codigo_region = int(input("Ingrese el codigo de la region a la cual pertenece la comuna: "))

    entrada = """
        SELECT * FROM CASOS_POR_REGION
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    existe_region = False
    nombre_region = ""
    poblacion_regional = 0
    casos_regionales = 0

    for linea in tabla:
        if codigo_region in linea:

            nombre_region = linea[0]
            poblacion_regional = linea[3]
            casos_regionales = linea[4]
            existe_region = True
            break
    
    if existe_region:
        nueva_comuna = input("Ingrese el nombre de su comuna: ")
        codigo = int(input("Cual es su codigo?: "))
        poblacion = int(input("Cual es la poblacion de su comuna?: "))
        poblacion_regional += poblacion

        entrada1 = """
            INSERT INTO CASOS_POR_COMUNA(nombre_comuna, codigo_comuna, poblacion, casos_confirmados)
            VALUES(:nombre, :codigo, :poblacion, :casos)
        """
        cursor.execute(entrada1, [nueva_comuna, codigo, poblacion, 0])


        entrada2 = """
            INSERT INTO CASOS_POR_REGION(nombre_region, codigo_region, codigo_comuna, poblacion, casos_confirmados)
            VALUES(:nombreR, :codigoR, :codigoC, :poblacion, :casos)
        """
        cursor.execute(entrada2, [nombre_region, codigo_region, codigo, poblacion_regional, casos_regionales])


        entrada3 = """
            UPDATE CASOS_POR_REGION
            SET poblacion = :numero
            WHERE codigo_region = :region
        """
        cursor.execute(entrada3,[poblacion_regional, codigo_region])
        connection.commit()
    else:
        print("Para ingresar la comuna, la region ya debe existir")
      
"""
crea una region nueva y le agrega una comuna
"""
def crearRegion():
    codigo_region = int(input("Ingrese el codigo de la region que desea crear: "))

    entrada = """
        SELECT * FROM CASOS_POR_REGION
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()
    existe_region = False

    for linea in tabla:
        if codigo_region in linea:
            
            existe_region = True
            break

    if not existe_region:
        nombre_region = input("Ingrese el nombre de su region: ")
        nombre_comuna = input("Ingrese el nombre de una comuna perteneciente a su region: ")
        codigo_comuna = int(input("Ingrese el codigo de la comuna ingresada: "))
        poblacion_comuna = int(input("Ingrese la poblacion que tiene la comuna: "))

        entrada1 = """
            INSERT INTO CASOS_POR_COMUNA(nombre_comuna, codigo_comuna, poblacion, casos_confirmados)
            VALUES(:nombre, :codigo, :pobla, :casos)
        """
        cursor.execute(entrada1, [nombre_comuna, codigo_comuna, poblacion_comuna, 0])
    
        entrada2 = """
            INSERT INTO CASOS_POR_REGION(nombre_region, codigo_region, codigo_comuna, poblacion, casos_confirmados)
            VALUES(:nombre, :codigoR, :codigoC, :poblacion, :casos)
        """
        cursor.execute(entrada2,[nombre_region, codigo_region, codigo_comuna, poblacion_comuna, 0])


        connection.commit()

        

    else:
        print("La region ya existe")

"""
muestra la cantidad de casos confirmados para una comuna existente
"""
def verCasosComuna():
    codigo_comuna = int(input("ingrese el codigo de la comuna: "))

    entrada = """
        SELECT * FROM CASOS_POR_COMUNA
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()
    existe_comuna = False

    for linea in tabla:
        if codigo_comuna in linea:
            existe_comuna = True
            break

    if existe_comuna:

        entrada1 = """
            SELECT * FROM CASOS_POR_COMUNA
            WHERE codigo_comuna = :codigo
        """
        cursor.execute(entrada1, [codigo_comuna])

        fila = cursor.fetchall()

        print("Los casos totales de la comuna", (fila[0])[0], "son:",(fila[0])[3])

    else:
        print("La comuna no existe")

"""
muestra la cantidad de casos confirmados para una region existente
"""
def verCasosRegion():
    codigo_region = int(input("Ingrese el codigo de la region: "))

    entrada = """
        SELECT * FROM CASOS_POR_REGION
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()
    existe_region = False

    for linea in tabla:
        if codigo_region in linea:
            existe_region = True
            break

    if existe_region:

        entrada1 = """
            SELECT * FROM CASOS_POR_REGION
            WHERE codigo_region = :codigo
        """
        cursor.execute(entrada1, [codigo_region])

        mini_tabla = cursor.fetchall()

        for fila in mini_tabla:
            print("Los casos totales de la region de", (fila[0]), "son", (fila[4]))
            break

    else:
        print("La region no existe")

"""
muestra la cantidad de casos confirmados para todas las comunas existentes
"""
def verTodasLasComunas():
    entrada = """
        SELECT * FROM CASOS_POR_COMUNA
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    for fila in tabla:
        print("Los casos totales de la comuna de", fila[0], "son", fila[3])

"""
muestra la cantidad de casos confirmados para todas las regiones existentes
"""
def verTodasLasRegiones():
    entrada = """
        SELECT * FROM CASOS_POR_REGION
        ORDER BY codigo_region
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    diccionario = {}

    for fila in tabla:
        if fila[1] not in diccionario:
            diccionario[(fila[1])] = [fila[0], fila[4]]

    for region in diccionario:
        print("Los casos totales de la region de", (diccionario[region][0]), "son", (diccionario[region][1]))

"""
suma casos confirmados a una comuna
"""        
def agregarCasosNuevosComuna():
    codigo_comuna = int(input("Ingrese el codigo de la comuna: "))

    entrada = """
        SELECT * FROM CASOS_POR_COMUNA
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()
    casos = 0

    existe_comuna = False
    for linea in tabla:
        if codigo_comuna in linea:
            existe_comuna = True
            casos = linea[3]
            
            break

    if existe_comuna:
        casos_nuevos = int(input("Cuantos casos desea agregar?: "))
        total = casos + casos_nuevos
    
        entrada1 = """
            UPDATE CASOS_POR_COMUNA
            SET casos_confirmados = :casos
            WHERE codigo_comuna = :codigo
        """
        cursor.execute(entrada1, [total, codigo_comuna])

        entrada2 = """
            SELECT * FROM CASOS_POR_REGION
            WHERE codigo_comuna = :codigo
        """
        cursor.execute(entrada2, [codigo_comuna])

        fila = cursor.fetchall()
        casosR = fila[0][4]
        casos_totales = casosR + casos_nuevos
        codigo_region = fila[0][1]

        entrada3 = """
            UPDATE CASOS_POR_REGION
            SET casos_confirmados = :casos
            WHERE codigo_region = :codigo
        """
        cursor.execute(entrada3, [casos_totales, codigo_region])
        connection.commit()

    else:
        print("La comuna no existe")
    
"""
resta casos confirmados a una comuna. Si es que esta resta llega a ser negativa, los casos se definen como 0
"""
def eliminarCasosNuevosComuna():
    codigo_comuna = int(input("Ingrese el codigo de la comuna: "))

    entrada = """
        SELECT * FROM CASOS_POR_COMUNA
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()
    casos = 0

    existe_comuna = False
    for linea in tabla:
        if codigo_comuna in linea:
            existe_comuna = True
            casos = linea[3]
            break
    

    if existe_comuna:
        casos_nuevos = int(input("Cuantos casos desea eliminar?: "))
        total = casos - casos_nuevos
        if total < 0:
            total = 0

        entrada1 = """
            UPDATE CASOS_POR_COMUNA
            SET casos_confirmados = :casos
            WHERE codigo_comuna = :codigo
        """
        cursor.execute(entrada1, [total, codigo_comuna])

        entrada2 = """
            SELECT * FROM CASOS_POR_REGION
            WHERE codigo_comuna = :codigo
        """
        cursor.execute(entrada2, [codigo_comuna])

        fila = cursor.fetchall()
        casosR = fila[0][4]
        casos_totales = casosR - casos_nuevos
        if casos_totales < 0:
            casos_totales = 0

        codigo_region = fila[0][1]

        entrada3 = """
            UPDATE CASOS_POR_REGION
            SET casos_confirmados = :casos
            WHERE codigo_region = :codigo
        """
        cursor.execute(entrada3, [casos_totales, codigo_region])
        connection.commit()

    else:
        print("La comuna no existe")

"""
muestra las 5 comunas con mayor porcentaje de casos confirmados 
"""
def top5comunas():
    entrada = """
        SELECT * FROM CASOS_POR_COMUNA
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    diccionario = {}

    for linea in tabla:
        nombre = linea[0]
        poblacion = linea[2]
        casos = linea[3]

        if nombre not in diccionario:
            diccionario[nombre] = []
        
        diccionario[nombre].append(poblacion)
        diccionario[nombre].append(casos)

    lista_porcentajes = []

    for comuna in diccionario:
        lista = []
        porcentaje = int((diccionario[comuna][1] / diccionario[comuna][0]) * 100)
        nombre_comuna = comuna
        
        lista.append(porcentaje)
        lista.append(nombre_comuna)
        lista_porcentajes.append(lista)
    
    lista_porcentajes.sort()
    lista_porcentajes.reverse()

    print("Las 5 comunas con mayor porcentaje de casos son:")

    for x in range(0, 5):
        print("La comuna de",lista_porcentajes[x][1],"con un" ,str(lista_porcentajes[x][0])+"%")

"""
muestra las 5 regiones con mayor porcentaje de casos confirmados
"""  
def top5regiones():
    entrada = """
        SELECT * FROM CASOS_POR_REGION
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    diccionario = {}

    for linea in tabla:
        nombre = linea[0]
        poblacion = linea[3]
        casos = linea[4]

        if nombre not in diccionario:
            diccionario[nombre] = []

            diccionario[nombre].append(poblacion)
            diccionario[nombre].append(casos)

    lista_porcentajes = []

    for region in diccionario:
        lista = []
        porcentaje = int((diccionario[region][1] / diccionario[region][0]) * 100)
        nombre_comuna = region
        
        lista.append(porcentaje)
        lista.append(nombre_comuna)
        lista_porcentajes.append(lista)
    
    lista_porcentajes.sort()
    lista_porcentajes.reverse()


    print("Las 5 regiones con mayor porcentaje de casos son:")

    for x in range(0, 5):
        print("La region de",lista_porcentajes[x][1],"con un" ,str(lista_porcentajes[x][0])+"%")

"""
verifica si el porcentaje de casos confirmados para una region, segun la poblacion, es mayor a 15%. Si esto llega a ser
asi, la region se elimina
"""
def eliminar15Porciento():
    entrada = """
        SELECT * FROM CASOS_POR_REGION
    """
    cursor.execute(entrada)

    tabla = cursor.fetchall()

    diccionario = {}

    for linea in tabla:
        nombre = linea[0]
        codigo_region = linea[1]
        poblacion = linea[3]
        casos = linea[4]

        if nombre not in diccionario:
            diccionario[nombre] = []
        
            diccionario[nombre].append(poblacion)
            diccionario[nombre].append(casos)
            diccionario[nombre].append(codigo_region)

    lista_porcentajes = []

    for region in diccionario:
        lista = []
        porcentaje = int((diccionario[region][1] / diccionario[region][0]) * 100)
        nombre_region = region
        codigo_region = diccionario[region][2]
        
        lista.append(porcentaje)
        lista.append(nombre_region)
        lista.append(codigo_region)
        lista_porcentajes.append(lista)
    
    lista_porcentajes.sort()
    lista_porcentajes.reverse()


    for lista in lista_porcentajes:
        porcentaje = lista[0]
        nombre = lista[1]
        codigoR = lista[2]
        
        if porcentaje > 15:

            print("La region de", nombre, "pasara a FASE DE ELIMINACION por tener un", str(porcentaje)+"%"+" de casos")
            
            entrada1 = """
                SELECT * FROM CASOS_POR_REGION
                WHERE codigo_region = :codigo
            """
            cursor.execute(entrada1, [codigoR])

            mini_tabla = cursor.fetchall()
            
            lista_comunas = []

            for fila in mini_tabla:
                codigo_comuna = fila[2]
                lista_comunas.append(codigo_comuna)

            for comuna in lista_comunas:
                entrada2 = """
                    DELETE FROM CASOS_POR_COMUNA
                    WHERE codigo_comuna = :codigo
                """
                cursor.execute(entrada2, [comuna])

            entrada3 = """
                DELETE FROM CASOS_POR_REGION
                WHERE codigo_region = :codigo
            """
            cursor.execute(entrada3, [codigoR])

    connection.commit()



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN~MENU~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BIENVENIDO ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")

print("""
SELECCIONA UNA OPCION:

1.- CREAR UNA COMUNA
2.- CREAR UNA REGION
3.- VER CASOS DE UNA COMUNA
4.- VER CASOS DE UNA REGION
5.- VER LOS CASOS DE TODAS LAS COMUNAS
6.- VER LOS CASOS DE TODAS LAS REGIONES
7.- AGREGAR CASOS NUEVOS A UNA COMUNA
8.- QUITAR CASOS A UNA COMUNA
9.- VER EL TOP 5 DE COMUNAS CON MAS CASOS
10.- VER EL TOP 5 DE REGIONES CON MAS CASOS
11.- SALIR
""")

entrada = input(": ")

while entrada != "11":

    if entrada == "1":
        crearComuna()
    
    elif entrada == "2":
        crearRegion()

    elif entrada == "3":
        verCasosComuna()

    elif entrada == "4":
        verCasosRegion()

    elif entrada == "5":
        verTodasLasComunas()

    elif entrada == "6":
        verTodasLasRegiones()
        
    elif entrada == "7":
        agregarCasosNuevosComuna()

    elif entrada == "8":
        eliminarCasosNuevosComuna()

    elif entrada == "9":
        top5comunas()

    elif entrada == "10":
        top5regiones()

    eliminar15Porciento()

    print("""
    SELECCIONA UNA OPCION:

    1.- CREAR UNA COMUNA
    2.- CREAR UNA REGION
    3.- VER CASOS DE UNA COMUNA
    4.- VER CASOS DE UNA REGION
    5.- VER LOS CASOS DE TODAS LAS COMUNAS
    6.- VER LOS CASOS DE TODAS LAS REGIONES
    7.- AGREGAR CASOS NUEVOS A UNA COMUNA
    8.- QUITAR CASOS A UNA COMUNA
    9.- VER EL TOP 5 DE COMUNAS CON MAS CASOS
    10.- VER EL TOP 5 DE REGIONES CON MAS CASOS
    11.- SALIR
    """)

    entrada = input(": ")

print("""
QUE TENGA UN BUEN DIA
""")

connection.close()