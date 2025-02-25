## Diccionario de Datos: Participación de Deportistas en Eventos Deportivos Internacionales

### Datos del Dataset

*   **FECHA_CORTE:** Día en que se generó el Dataset.
    *   Tipo de dato: Numérico
    *   Tamaño: 8
    *   Formato: aaaammdd
*   **ITEM:** Número correlativo.
    *   Tipo de dato: Numérico
    *   Tamaño: 5
*   **FECHA_PUBLICACION:** Día en que se publicó el Dataset.
    *   Tipo de dato: Numérico
    *   Tamaño: 8
    *   Formato: aaaammdd

### Datos del Evento Deportivo

*   **FEDERACION:** Federación Deportiva Nacional o Asociación Deportiva que registra la participación del evento deportivo internacional.
    *   Tipo de dato: Texto
    *   Tamaño: 50
*   **EVENTO:** Nombre del evento deportivo internacional en donde se registra la participación del deportista.
    *   Tipo de dato: Texto
    *   Tamaño: 200
*   **PAIS_EVENTO:** País en donde se realiza el evento deportivo internacional.
    *   Tipo de dato: Texto
    *   Tamaño: 50
*   **CIUDAD_EVENTO:** Ciudad del país en donde se realiza en evento deportivo internacional.
    *   Tipo de dato: Texto
    *   Tamaño: 50
*   **FECHA_INICIO:** Fecha de inicio del evento deportivo internacional.
    *   Tipo de dato: Numérico
    *   Tamaño: 8
    *   Formato: aaaammdd
*   **FECHA_FIN:** Fecha de término del evento deportivo internacional.
    *   Tipo de dato: Numérico
    *   Tamaño: 8
    *   Formato: aaaammdd

### Datos del Deportista

*   **DEPORTISTA:** Nombres completos del deportista.
    *   Tipo de dato: Texto
    *   Tamaño: 100
*   **PUESTO:** Posición alcanzada por el deportista en el evento deportivo internacional en el que participó.
    *   Tipo de dato: Numérico
    *   Tamaño: 3
    *   Información Adicional: Se considera el valor 0 para una participación sin posición específica. Asimismo, los puestos 1, 2 y 3 son equivalentes a las medallas de Oro, Plata y Bronce, correspondientemente.
*   **ESPECIALIDAD:** Modalidad o categoría específica en la que participó el deportista en el evento deportivo internacional.
    *   Tipo de dato: Texto
    *   Tamaño: 50
*   **COLECTIVO:** Tipo de agrupación que define la participación de los deportistas en el evento deportivo internacional.
    *   Tipo de dato: Texto
    *   Tamaño: 50

### Ubicación de la Sede Central del IPD

*   **DEPARTAMENTO:** Departamento donde se encuentra ubicada la sede central del IPD.
    *   Tipo de dato: Texto
    *   Tamaño: 20
    *   Recurso Relacionado: Catálogo del INEI
*   **PROVINCIA:** Provincia donde se encuentra ubicada la sede central del IPD.
    *   Tipo de dato: Texto
    *   Tamaño: 100
    *   Recurso Relacionado: Catálogo del INEI
*   **DISTRITO:** Distrito donde se encuentra ubicada la sede central del IPD.
    *   Tipo de dato: Texto
    *   Tamaño: 100
    *   Recurso Relacionado: Catálogo del INEI
*   **UBIGEO:** Código de ubicación geográfica donde se encuentra ubicada la sede central del IPD.
    *   Tipo de dato: Alfanumérico
    *   Tamaño: 6
    *   Recurso Relacionado: Catálogo del INEI