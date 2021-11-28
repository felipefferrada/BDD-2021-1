import cx_Oracle

connection = cx_Oracle.connect("ADMIN", "1234", "localhost:1521")
print("Database Version", connection.version)

cursor = connection.cursor()

cursor.execute (
        """
            CREATE TABLE CASOS_POR_COMUNA(
                nombre_comuna VARCHAR(50) NOT NULL,
                codigo_comuna NUMBER NOT NULL,
                poblacion NUMBER NOT NULL,
                casos_confirmados NUMBER NOT NULL,
                PRIMARY KEY(codigo_comuna)
            )
        """
        )

print("TABLA CASOS_POR_COMUNA CREADA")

cursor.execute (
        """
            CREATE TABLE CASOS_POR_REGION(
                nombre_region VARCHAR(50) NOT NULL,
                codigo_region NUMBER NOT NULL,
                codigo_comuna NUMBER NOT NULL,
                poblacion NUMBER NOT NULL,
                casos_confirmados NUMBER NOT NULL,
                PRIMARY KEY(codigo_comuna)
            )
        """
        )

print("TABLA CASOS_POR_REGION CREADA")

connection.close()
