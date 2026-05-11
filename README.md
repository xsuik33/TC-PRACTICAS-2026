# TC-PRACTICAS-2026

## Descripción
Este repositorio contiene las prácticas de laboratorio desarrolladas para la unidad de aprendizaje de **Teoría de la Computación** en la **Escuela Superior de Cómputo (ESCOM)** del Instituto Politécnico Nacional.

El proyecto está diseñado para ejecutarse en entornos virtuales aislados, garantizando que no se realicen modificaciones en la instalación global de Python del sistema y asegurando la portabilidad entre diferentes plataformas.

## Requisitos Previos
* Python 3.10 o superior.
* Gestor de paquetes `pip`.
* Módulo `venv` (incluido por defecto en instalaciones estándar de Python).

## Guía de Configuración y Ejecución

Para revisar y ejecutar las prácticas, se recomienda seguir estos pasos en la terminal para mantener un entorno limpio:

### 1. Clonar el Repositorio
````bash
git clone [https://github.com/xsuik33/TC-PRACTICAS-2026.git](https://github.com/xsuik33/TC-PRACTICAS-2026.git)
cd TC-PRACTICAS-2026
````
### 2. Crear el Entorno Virtual (venv)
````bash
python -m venv venv
````
### 3. Activar el Entorno Virtual (venv)
* En Windows:
````bash
.\venv\Scripts\activate
````
* En Linux/macOS
````bash
source venv/bin/activate
````
### 4. Instalar Dependencias
````bash
pip install -r requirements.txt
````
### 5. Ejecutar la Prácica
````bash
python "PRACTICA".py
````

### Estructura del Proyecto
* requirements.txt: Lista de dependencias del proyecto.
* .gitignore: Configuracion para excluir archivos temporales y la carpeta del entorno virtual (venv/).
* README.md: Instrucciones de uso y documentacion.
## Autor: Iker Saul Gonzalez Ortiz
## Grupo: 4CM2
## Escuela: Escuela Superior de Cómputo (ESCOM) - IPN
