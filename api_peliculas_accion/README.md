# API de películas de acción

## ¿De qué trata?

Esta API permite gestionar un catálogo de películas de acción. Cada película tiene un título, director, año de estreno, género y duración en minutos. Cada elemento también tiene un `id`, que calcula automáticamente la API.

Los datos iniciales están en `peliculas.json`. Cuando se agrega, edita o borra una película, los cambios se guardan en ese archivo y se mantienen al reiniciar el servidor.

## Cómo arrancar el proyecto

Necesitas tener Python instalado.

1. Abre una terminal en la carpeta del proyecto.
2. Crea un entorno virtual:

   ```bash
   py -m venv .venv
   ```

3. Activa el entorno virtual en Windows:

   ```bash
   .venv\Scripts\activate
   ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Arranca el servidor:

   ```bash
   uvicorn main:app --reload
   ```

6. Abre la documentación interactiva en el navegador:

   <http://127.0.0.1:8000/docs>

Para detener el servidor, pulsa `Ctrl + C` en la terminal.

## Rutas de la API

| Método | Ruta | Función |
|---|---|---|
| GET | `/peliculas` | Lista todas las películas. |
| GET | `/peliculas/{pelicula_id}` | Busca una película por su id. |
| POST | `/peliculas` | Agrega una película y calcula su id. |
| PUT | `/peliculas/{pelicula_id}` | Edita todos los datos de una película. |
| DELETE | `/peliculas/{pelicula_id}` | Borra una película. |

### Filtros adicionales

Se puede filtrar por director o género:

- `/peliculas?director=Christopher Nolan`
- `/peliculas?genero=Acción`
- `/peliculas?director=Christopher Nolan&genero=crimen`

### Ejemplo para agregar una película

En `POST /peliculas`, envía este JSON en el cuerpo de la petición:

```json
{
    "titulo": "Misión imposible: Sentencia mortal",
    "director": "Christopher McQuarrie",
    "anio": 2023,
    "genero": "Acción y espionaje",
    "duracion_min": 163
}
```

No incluyas el `id`: lo genera la API.

## Validaciones y errores

- Las búsquedas, ediciones y eliminaciones devuelven `404` si el id no existe.
- Se devuelve `409` si se intenta añadir otra película con un título que ya existe.
- Pydantic valida los campos: el año debe estar entre 1888 y 2100, la duración debe ser mayor que 0 y los textos tienen límites de longitud.
