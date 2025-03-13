from fastapi import FastAPI, UploadFile, File, Form, Query
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

@app.get("/", summary="Verifica se l'API è attiva")
def read_root():
    """Endpoint di test per verificare se il server è attivo."""
    return {"message": "GDAL REST API is running!"}

@app.post("/gdalinfo/", response_model=GDALInfoResponse, summary="Ottieni informazioni su un raster")
async def get_gdalinfo(file: UploadFile = File(..., description="File raster da analizzare")):
    """Esegue `gdalinfo` su un raster e restituisce le informazioni."""
    file_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(["gdalinfo", file_path], capture_output=True, text=True)
    os.remove(file_path)

    return {"filename": file.filename, "gdalinfo": result.stdout}

@app.post("/translate/", summary="Converti un raster in un altro formato")
async def translate_raster(
    file: UploadFile = File(..., description="File raster da convertire"), 
    output_format: str = Form("GTiff", description="Formato di output (GTiff, PNG, JPEG)")
):
    """Converte un raster in un altro formato con `gdal_translate`."""
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_converted.{output_format.lower()}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdal_translate", "-of", output_format, input_path, output_path])
    os.remove(input_path)

    return {"message": "Raster converted", "output_file": output_path}

@app.post("/warp/", summary="Riprojettare un raster in un altro sistema di riferimento")
async def warp_raster(
    file: UploadFile = File(..., description="File raster da riproiettare"), 
    epsg: str = Form("4326", description="Codice EPSG del nuovo sistema di riferimento")
):
    """Riprojeta un raster in un altro sistema di coordinate utilizzando `gdalwarp`."""
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_warped.tif"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdalwarp", "-t_srs", f"EPSG:{epsg}", input_path, output_path])
    os.remove(input_path)

    return {"message": "Raster reprojected", "output_file": output_path}

@app.post("/vector_info/", summary="Ottieni informazioni su un file vettoriale")
async def get_vector_info(file: UploadFile = File(..., description="File vettoriale da analizzare")):
    """Esegue `ogrinfo` su un file vettoriale e restituisce le informazioni."""
    file_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(["ogrinfo", file_path], capture_output=True, text=True)
    os.remove(file_path)

    return {"filename": file.filename, "vector_info": result.stdout}

@app.post("/raster_to_vector/", summary="Converti un raster in vettoriale")
async def raster_to_vector(
    file: UploadFile = File(..., description="File raster da convertire"), 
    output_format: str = Form("GeoJSON", description="Formato di output (GeoJSON, Shapefile)")
):
    """Converte un raster in un vettoriale (poligoni) utilizzando `gdal_polygonize.py`."""
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_vectorized.{output_format.lower()}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdal_polygonize.py", input_path, "-f", output_format, output_path])
    os.remove(input_path)

    return {"message": "Raster converted to vector", "output_file": output_path}

@app.get("/wms_to_geotiff/", summary="Scarica un'immagine da un WMS e la converte in GeoTIFF")
async def wms_to_geotiff(
    wms_url: str = Query(..., description="URL del servizio WMS (senza parametri GetMap)"),
    layers: str = Query(..., description="Nome del layer WMS"),
    bbox: str = Query(..., description="Bounding box nel formato xmin,ymin,xmax,ymax"),
    width: int = Query(1024, description="Larghezza dell'immagine in pixel"),
    height: int = Query(1024, description="Altezza dell'immagine in pixel"),
    crs: str = Query("EPSG:4326", description="Codice EPSG del sistema di riferimento"),
    version: str = Query("1.3.0", description="Versione del servizio WMS"),
    format: str = Query("image/png", description="Formato dell'immagine"),
    token: str = Query(None, description="Token di autenticazione per il servizio WMS"),
    user: str = Query(None, description="Nome utente per l'autenticazione"),
    password: str = Query(None, description="Password per l'autenticazione")
):
    """
    Scarica un'immagine da un servizio WMS e la converte in GeoTIFF.
    """
    try:
        # Genera i nomi dei file temporanei
        image_filename = f"{uuid.uuid4()}_wms.png"
        geotiff_filename = f"{uuid.uuid4()}_wms.tif"
        image_path = os.path.join(TEMP_DIR, image_filename)
        geotiff_path = os.path.join(TEMP_DIR, geotiff_filename)

        # Costruisci i parametri della richiesta WMS in modo sicuro
        params = {
            "SERVICE": "WMS",
            "VERSION": version,
            "REQUEST": "GetMap",
            "LAYERS": layers,
            "CRS": crs,
            "BBOX": bbox,
            "WIDTH": width,
            "HEIGHT": height,
            "FORMAT": format
        }
        
        if token:
            params["token"] = token

        wms_request_url = f"{wms_url}?{urlencode(params)}"

        # Scarica l'immagine dal WMS con autenticazione opzionale
        auth = (user, password) if user and password else None
        response = requests.get(wms_request_url, stream=True, auth=auth, timeout=30)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"error": "Errore nel download dell'immagine WMS"})

        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        # Converti l'immagine in GeoTIFF usando rasterio
        bbox_values = list(map(float, bbox.split(",")))  # xmin, ymin, xmax, ymax
        if len(bbox_values) != 4:
            return JSONResponse(status_code=400, content={"error": "Formato del BBOX non valido"})

        transform = from_bounds(*bbox_values, width, height)

        with rasterio.open(image_path) as src:
            meta = src.meta.copy()
            meta.update({
                "driver": "GTiff",
                "crs": crs,
                "transform": transform
            })

            with rasterio.open(geotiff_path, "w", **meta) as dst:
                dst.write(src.read())

        # Ritorna il file GeoTIFF generato
        return FileResponse(geotiff_path, filename="output.tif", media_type="application/octet-stream")

    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=500, content={"error": f"Errore di connessione WMS: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download/{filename}", summary="Scarica un file generato dall'API")
async def download_file(filename: str):
    """
    Permette di scaricare un file generato da un'operazione GDAL.
    """
    # Evita attacchi di path traversal usando solo il nome base del file
    safe_filename = Path(filename).name
    file_path = Path(TEMP_DIR) / safe_filename

    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File non trovato"})

    return FileResponse(file_path, filename=safe_filename, media_type="application/octet-stream")
