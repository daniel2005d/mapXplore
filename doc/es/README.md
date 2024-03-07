# mapXplore

[English](../../README.md)

<img src="../images/Logo.jpg" width="180px">

**mapXplore** es una aplicación modular, que importa los datos extraidos de sqlmap, a una base de datos postgres o sqlite.

Sus principales caracteristicas son:

* Importación de información extraida de sqlmap a postgres o sqlite para su posterior consulta.
* Información sanitizada, lo que significa que al momento de importar esta se decodifica o transforma información no legible a información legible.
* Búsqueda de información en todas las tablas, como es el caso de contraseñas, usuarios e información que asi se desee.
* Exportación automatica de información almacenada en **base64**, como pueden ser:
    * Archivos Word, Excel, Powerpoint
    * Archivos .zip
    * Archivos de texto o información en texto plano
    * Imágenes

* Filtrar tablas y columnas por criterios.
* Filtrar por diferentes tipos de funciones hash sin requerir su previa conversión.
* Exportar la información relevante a Excel o HTML

# Instalación

## Requrimientos
* python-3.11

```
git clone https://github.com/daniel2005d/mapXplore
cd mapXplore
pip install -r requirements
```

# Uso

Es una aplicación que es modular, y consta de lo siguiente:

* **config**: Se encarga de la configuración, como motor de base de datos a usar, rutas de importación entre otros.
* **import**: Se encarga de realizar la importación y tratamiento de la información extraida de **sqlmap**
* **query**: Es el modulo principal capaz de filtrar y extraer la información que se requiere.
    * Filtro por tablas
    * Filtro por columnas
    * Filtro por una o varias palabras
    * Filtro por una o varias funciones Hash dentro de las cuales se encuentran:
        * MD5
        * SHA1
        * SHA256
        * SHA3
        * ....

### Inicio
> Permite cargar una configuración por defecto al inicio del programa

```
python engine.py [--config config.json]
```
<img src="../screenshot/start.png" >

## Modulos

- [config](configuration.md)
- [import](import.md)
- [principal|search](main.md)