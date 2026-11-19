import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# El archivo JSON está en la misma carpeta que este archivo Python.
RUTA_JSON = Path(__file__).parent / "peliculas.json"


class Pelicula(BaseModel):
    """Datos que se pueden enviar al crear o editar una película (sin id)."""

    titulo: str = Field(min_length=1, max_length=100)
    director: str = Field(min_length=1, max_length=80)
    anio: int = Field(ge=1888, le=2100)
    genero: str = Field(min_length=1, max_length=50)
    duracion_min: int = Field(gt=0, le=500)


class PeliculaRespuesta(Pelicula):
    """Datos que devuelve la API, incluido el id."""

    id: int


def cargar_peliculas() -> list[dict]:
    """Lee las películas guardadas en el archivo JSON."""
    if not RUTA_JSON.exists():
        return []

    with RUTA_JSON.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_peliculas() -> None:
    """Guarda la lista actual en el archivo JSON."""
    with RUTA_JSON.open("w", encoding="utf-8") as archivo:
        json.dump(peliculas, archivo, ensure_ascii=False, indent=4)


# Al iniciar el servidor se cargan los datos que ya existen en el JSON.
peliculas: list[dict] = cargar_peliculas()

app = FastAPI(
    title="API de películas de acción",
    description="Catálogo personal de películas. Los datos se guardan en peliculas.json.",
    version="1.0.0",
)


@app.get("/peliculas", response_model=list[PeliculaRespuesta], tags=["Películas"])
def listar_peliculas(
    director: str | None = None,
    genero: str | None = None,
):
    """Devuelve todas las películas o las filtra por director y/o género."""
    resultado = peliculas

    if director is not None:
        resultado = [
            pelicula
            for pelicula in resultado
            if director.casefold() in pelicula["director"].casefold()
        ]

    if genero is not None:
        resultado = [
            pelicula
            for pelicula in resultado
            if genero.casefold() in pelicula["genero"].casefold()
        ]

    return resultado


@app.get(
    "/peliculas/{pelicula_id}",
    response_model=PeliculaRespuesta,
    tags=["Películas"],
)
def buscar_pelicula(pelicula_id: int):
    """Busca una película por su id."""
    for pelicula in peliculas:
        if pelicula["id"] == pelicula_id:
            return pelicula

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No existe una película con ese id",
    )


@app.post(
    "/peliculas",
    response_model=PeliculaRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Películas"],
)
def agregar_pelicula(pelicula: Pelicula):
    """Añade una película y calcula su id automáticamente."""
    for existente in peliculas:
        if existente["titulo"].casefold() == pelicula.titulo.casefold():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una película con ese título",
            )

    nuevo_id = max((item["id"] for item in peliculas), default=0) + 1
    nueva_pelicula = {"id": nuevo_id, **pelicula.model_dump()}
    peliculas.append(nueva_pelicula)
    guardar_peliculas()
    return nueva_pelicula


@app.put(
    "/peliculas/{pelicula_id}",
    response_model=PeliculaRespuesta,
    tags=["Películas"],
)
def editar_pelicula(pelicula_id: int, datos_actualizados: Pelicula):
    """Sustituye todos los datos de una película existente."""
    for indice, existente in enumerate(peliculas):
        if existente["id"] == pelicula_id:
            for otra in peliculas:
                if (
                    otra["id"] != pelicula_id
                    and otra["titulo"].casefold() == datos_actualizados.titulo.casefold()
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Ya existe otra película con ese título",
                    )

            pelicula_editada = {
                "id": pelicula_id,
                **datos_actualizados.model_dump(),
            }
            peliculas[indice] = pelicula_editada
            guardar_peliculas()
            return pelicula_editada

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No existe una película con ese id",
    )


@app.delete("/peliculas/{pelicula_id}", tags=["Películas"])
def borrar_pelicula(pelicula_id: int):
    """Elimina una película por su id."""
    for indice, pelicula in enumerate(peliculas):
        if pelicula["id"] == pelicula_id:
            pelicula_eliminada = peliculas.pop(indice)
            guardar_peliculas()
            return {
                "mensaje": "Película eliminada correctamente",
                "pelicula": pelicula_eliminada["titulo"],
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No existe una película con ese id",
    )
