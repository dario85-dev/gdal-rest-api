from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import subprocess
import os
import shutil
import uuid

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
