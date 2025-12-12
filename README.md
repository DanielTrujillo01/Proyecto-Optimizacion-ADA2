# Proyecto-Optimización-ADA2

Este proyecto está desarrollado para solucionar el problema de la optimización de la polarización de un conjunto de opiniones de una población.

Este proyecto usa Programación Entera Mixta y el método branch and bound para resolver el problema. El modelo está implementado en MiniZinc y para poder ejecutarlo siga la siguiente guía de uso.

## Guía de uso

### 1. Crear ambiente virtual

Para ejecutar pruebas primero cree un ambiente virtual para instalar las dependencias:

```bash
python -m venv .venv
```

### 2. Activar el ambiente

```bash
# Windows
.\.venv\Scripts\activate

# Linux
./.venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python gui.py
```

### 5. Convertir TXT a DZN

En la primera pestaña de la aplicación **Convertir TXT a DZN**:

- Dé clic en **Seleccionar Directorio** si desea convertir todos los archivos `.txt` de prueba de un directorio específico, o si solo desea convertir un solo archivo seleccione **Seleccionar TXT y Convertir**.
- Ahora seleccione el directorio de destino donde desea guardar los archivos `.dzn` generados y espere mientras se convierten.

### 6. Ejecutar Modelo

Ahora diríjase a la pestaña **Ejecutar Modelo**:

- Seleccione **Buscar** para buscar el modelo `.mzn` en el directorio raíz. Los modelos se encuentran en el directorio **modelos**. Aquí encontrará tres modelos, el modelo oficial del proyecto es **Proyecto_mejorado.mzn**, el cual es para entregar. Los otros modelos son optimizaciones de este modelo en las cuales se utilizan escalas en los valores de los parámetros para que los solvers trabajen con números enteros y puedan resolver el problema de forma rápida, pero el modelo más confiable y claro es el modelo **Proyecto_mejorado.mzn**.
- Seleccione **Carpeta** para ejecutar todas las pruebas `.dzn` dentro de un directorio específico, o seleccione **Archivo** para ejecutar un solo archivo `.dzn`. Escoja el directorio adecuado o el archivo adecuado en la ventana que se desplegó. No seleccione ambos, es decir la carpeta y también un archivo, porque puede haber conflictos.
- Seleccione el **solver** del menú desplegable. Para pruebas que no sean exigentes seleccione **gecode**, pero para pruebas exigentes o complejas seleccione **gurobi** si ya lo tiene instalado en su máquina local.
- Clic en **EJECUTAR MODELO Y GUARDAR**.
- Seleccione un directorio de destino donde desea guardar los resultados.
- Espere mientras se ejecutan las pruebas.
- Vaya al directorio de destino seleccionado previamente y abra los archivos solución.

---

Para visualizar más claramente los anteriores pasos puede ver el siguiente video:
