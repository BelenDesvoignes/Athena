from minio import Minio
from datetime import timedelta
from flask import current_app


def get_site_images(sitio, only_cover=False):
    """
    Obtiene imágenes del sitio y genera URLs presignadas.
    Si only_cover=True, solo devuelve la portada.
    Retorna (cover_url, cover_title, lista_de_imagenes)
    """
    minio_client = Minio(
        endpoint=current_app.config["MINIO_SERVER"],
        access_key=current_app.config["MINIO_ACCESS_KEY"],
        secret_key=current_app.config["MINIO_SECRET_KEY"],
        secure=current_app.config["MINIO_SECURE"]
    )
    bucket_name = current_app.config["MINIO_BUCKET"]

    default_url = "/img/default.jpg"

    if only_cover:
        portada = next((img for img in sitio.imagenes if img.es_portada), None)
        if portada:
            try:
                cover_url = minio_client.presigned_get_object(bucket_name, portada.ruta, expires=timedelta(hours=2))
            except:
                cover_url = default_url
            cover_title = portada.titulo
        else:
            cover_url = default_url
            cover_title = ""
        return cover_url, cover_title, []

    imagenes_data = []
    for img in sitio.imagenes:
        try:
            image_url = minio_client.presigned_get_object(bucket_name, img.ruta, expires=timedelta(hours=2))
        except:
            image_url = default_url

        imagenes_data.append({
            "id": img.id,
            "url": image_url,
            "title": img.titulo,
            "is_cover": img.es_portada
        })

    imagenes_data.sort(key=lambda x: not x["is_cover"])
    cover_url = imagenes_data[0]["url"] if imagenes_data else default_url
    cover_title = imagenes_data[0]["title"] if imagenes_data else ""

    return cover_url, cover_title, imagenes_data