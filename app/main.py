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

# Dizionario per memorizzare lo stato dei processi
process_status = {}

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

@app.post("/gdalinfo/", summary="Ottieni informazioni su un raster")
async def get_gdalinfo(file: UploadFile = File(...)):
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output": None, "error": None}
    
    file_path = os.path.join(TEMP_DIR, f"{process_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = subprocess.run(["gdalinfo", file_path], capture_output=True, text=True, check=True)
        process_status[process_id] = {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(file_path)
    
    return {"process_id": process_id}

@app.post("/translate/", summary="Converti un raster in un altro formato")
async def translate_raster(
    file: UploadFile = File(...),
    output_format: str = Form("GTiff")
):
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output_path": None, "error": None}
    
    input_path = os.path.join(TEMP_DIR, f"{process_id}_{file.filename}")
    output_path = os.path.join(TEMP_DIR, f"{process_id}_converted.{output_format.lower()}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(["gdal_translate", "-of", output_format, input_path, output_path], check=True)
        process_status[process_id] = {"status": "success", "output_path": output_path}
    except subprocess.CalledProcessError as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(input_path)
    
    return {"process_id": process_id}

@app.post("/warp/", summary="Riprojettare un raster in un altro sistema di riferimento")
async def warp_raster(
    file: UploadFile = File(...), 
    epsg: str = Form("4326")
):
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output_path": None, "error": None}

    input_path = os.path.join(TEMP_DIR, f"{process_id}_{file.filename}")
    output_path = os.path.join(TEMP_DIR, f"{process_id}_warped.tif")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(["gdalwarp", "-t_srs", f"EPSG:{epsg}", input_path, output_path], check=True)
        process_status[process_id] = {"status": "success", "output_path": output_path}
    except subprocess.CalledProcessError as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(input_path)
    
    return {"process_id": process_id}

@app.post("/vector_info/", summary="Ottieni informazioni su un file vettoriale")
async def get_vector_info(file: UploadFile = File(...)):
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output": None, "error": None}

    file_path = os.path.join(TEMP_DIR, f"{process_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = subprocess.run(["ogrinfo", file_path], capture_output=True, text=True, check=True)
        process_status[process_id] = {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(file_path)

    return {"process_id": process_id}

@app.post("/raster_to_vector/", summary="Converti un raster in vettoriale")
async def raster_to_vector(
    file: UploadFile = File(...),
    output_format: str = Form("GeoJSON")
):
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output_path": None, "error": None}

    input_path = os.path.join(TEMP_DIR, f"{process_id}_{file.filename}")
    output_path = os.path.join(TEMP_DIR, f"{process_id}_vectorized.{output_format.lower()}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(["gdal_polygonize.py", input_path, "-f", output_format, output_path], check=True)
        process_status[process_id] = {"status": "success", "output_path": output_path}
    except subprocess.CalledProcessError as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(input_path)
    
    return {"process_id": process_id}

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
    process_id = str(uuid.uuid4())
    process_status[process_id] = {"status": "pending", "output_path": None, "error": None}

    try:
        image_filename = f"{process_id}_wms.png"
        geotiff_filename = f"{process_id}_wms.tif"
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
            process_status[process_id] = {"status": "failed", "error": "Errore nel download dell'immagine WMS"}
            return {"process_id": process_id}

        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        bbox_values = list(map(float, bbox.split(",")))
        if len(bbox_values) != 4:
            process_status[process_id] = {"status": "failed", "error": "Formato del BBOX non valido"}
            return {"process_id": process_id}

        # Converti l'immagine in GeoTIFF e assegna la georeferenziazione
        subprocess.run([
            "gdal_translate",
            "-a_ullr", str(bbox_values[0]), str(bbox_values[3]), str(bbox_values[2]), str(bbox_values[1]),
            "-a_srs", crs,
            image_path, geotiff_path
        ], check=True)

        # Assicura la proiezione corretta con gdalwarp
        subprocess.run(["gdalwarp", "-t_srs", crs, geotiff_path, geotiff_path], check=True)

        process_status[process_id] = {"status": "success", "output_path": geotiff_path}

    except requests.exceptions.RequestException as e:
        process_status[process_id] = {"status": "failed", "error": f"Errore di connessione WMS: {str(e)}"}
    except Exception as e:
        process_status[process_id] = {"status": "failed", "error": str(e)}
    
    return {"process_id": process_id}

@app.get("/status/{process_id}", summary="Controlla lo stato della trasformazione")
def get_process_status(process_id: str):
    if process_id not in process_status:
        return JSONResponse(status_code=404, content={"error": "Process ID non trovato"})
    return process_status[process_id]

@app.get("/download/{process_id}", summary="Scarica il file generato")
def download_file(process_id: str):
    if process_id not in process_status:
        return JSONResponse(status_code=404, content={"error": "Process ID non trovato"})
    if process_status[process_id]["status"] != "success":
        return JSONResponse(status_code=400, content={"error": "Il file non è pronto"})
    return FileResponse(process_status[process_id]["output_path"], filename="output.tif", media_type="application/octet-stream")
