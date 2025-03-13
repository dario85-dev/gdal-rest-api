from fastapi import FastAPI, UploadFile, File, Form, Query, BackgroundTasks
import requests
from pydantic import BaseModel
import subprocess
import os
import shutil
import uuid
import rasterio
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from rasterio.transform import from_bounds
from urllib.parse import urlencode
import time

app = FastAPI(
    title="GDAL API",
    description="Un'API REST basata su GDAL per l'elaborazione di raster e vettoriali",
    version="1.0.0"
)

TEMP_DIR = "/tmp/gdal_api"
os.makedirs(TEMP_DIR, exist_ok=True)

class GDALInfoResponse(BaseModel):
    filename: str
    gdalinfo: str

def cleanup_temp_files():
    """Pulisce i file temporanei più vecchi di 1 ora."""
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > 3600:
            os.remove(file_path)

@app.get("/", summary="Verifica se l'API è attiva")
def read_root():
    return {"message": "GDAL REST API is running!"}

@app.get("/wms_to_geotiff/", summary="Scarica un'immagine da un WMS e la converte in GeoTIFF")
async def wms_to_geotiff(
    wms_url: str = Query(...),
    layers: str = Query(...),
    bbox: str = Query(...),
    width: int = Query(1024),
    height: int = Query(1024),
    crs: str = Query("EPSG:4326"),
    version: str = Query("1.3.0"),
    format: str = Query("image/png"),
    token: str = Query(None),
    user: str = Query(None),
    password: str = Query(None)
):
    allowed_formats = {"image/png", "image/jpeg", "image/tiff"}
    if format not in allowed_formats:
        return JSONResponse(status_code=400, content={"error": "Formato non supportato"})
    
    try:
        image_filename = f"{uuid.uuid4()}_wms.png"
        geotiff_filename = f"{uuid.uuid4()}_wms.tif"
        image_path = os.path.join(TEMP_DIR, image_filename)
        geotiff_path = os.path.join(TEMP_DIR, geotiff_filename)

        params = {
            "SERVICE": "WMS", "VERSION": version, "REQUEST": "GetMap",
            "LAYERS": layers, "CRS": crs, "BBOX": bbox, "WIDTH": width,
            "HEIGHT": height, "FORMAT": format
        }
        if token:
            params["token"] = token
        
        wms_request_url = f"{wms_url}?{urlencode(params)}"
        auth = (user, password) if user and password else None
        response = requests.get(wms_request_url, stream=True, auth=auth, timeout=30)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"error": "Errore nel download dell'immagine WMS"})

        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        bbox_values = list(map(float, bbox.split(",")))
        if len(bbox_values) != 4:
            return JSONResponse(status_code=400, content={"error": "Formato del BBOX non valido"})

        # Converti l'immagine in GeoTIFF e assegna la georeferenziazione
        subprocess.run([
            "gdal_translate",
            "-a_ullr", str(bbox_values[0]), str(bbox_values[3]), str(bbox_values[2]), str(bbox_values[1]),
            "-a_srs", crs,
            image_path, geotiff_path
        ], check=True)

        # Assicura la proiezione corretta con gdalwarp
        subprocess.run(["gdalwarp", "-t_srs", crs, geotiff_path, geotiff_path], check=True)

        return FileResponse(geotiff_path, filename="output.tif", media_type="application/octet-stream")

    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=500, content={"error": f"Errore di connessione WMS: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
