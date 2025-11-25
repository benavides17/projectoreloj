# Reloj Java – Despliegue

Aplicación de escritorio Swing que muestra un reloj digital y analógico con selector de idioma, zona horaria y tema claro/oscuro.

## Requisitos
- Java JDK 8 o superior instalado
- Sistema Windows (funciona también en macOS/Linux)

## Estructura del proyecto
- `Reloj.java`: código fuente principal

## Ejecutar en desarrollo
1. Abrir una terminal en el directorio del proyecto
2. Compilar:
   - `javac Reloj.java`
3. Ejecutar:
   - `java Reloj`

## Empaquetar en JAR ejecutable
1. Compilar para generar los `.class`:
   - `javac Reloj.java`
2. Crear el JAR indicando la clase principal (`Reloj`):
   - `jar cfe reloj.jar Reloj Reloj.class`
3. Ejecutar el JAR:
   - `java -jar reloj.jar`

## Crear script para doble clic (Windows)
- Crear un archivo `run.bat` junto al código con el contenido:
```
@echo off
javac Reloj.java
java Reloj
```
- Doble clic en `run.bat` para compilar y ejecutar.

## Opciones de la aplicación
- `24h`: alterna formato 24h/12h (muestra `AM/PM` en 12h)
- `Oscuro`: alterna tema claro/oscuro
- `Idioma`: `es`, `en`, `pt`, `fr` (actualiza la fecha localizada)
- `Zona`: `local`, `UTC`, `Europe/Madrid`, `Europe/Paris`, `America/Mexico_City`, `America/Bogota`, `America/Sao_Paulo`
- Campanada: beep al inicio de cada hora

## Solución de problemas
- No abre la ventana:
  - Verificar instalación de Java: `java -version` y `javac -version`
  - Ejecutar desde una terminal del sistema (no headless)
- `Error: Could not find or load main class Reloj`:
  - Ejecutar `java Reloj` desde el mismo directorio donde se compiló
  - Asegurarse de que no hay paquete declarado en `Reloj.java`
- Al crear el JAR:
  - Compilar antes (`javac Reloj.java`) y usar `jar cfe reloj.jar Reloj Reloj.class`

## Despliegue en otros sistemas
- En macOS/Linux los comandos son iguales
- Para crear un `.desktop` o script `.sh`, usar `java -jar reloj.jar`

