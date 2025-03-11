from fastapi import FastAPI, UploadFile, File, Form
import subprocess
import os
import shutil
import uuid

app = FastAPI()

TEMP_DIR = "/tmp/gdal_api"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "GDAL REST API is running!"}

# 🟢 GDALINFO: Ottiene info di un raster
@app.post("/gdalinfo/")
async def get_gdalinfo(file: UploadFile = File(...)):
    file_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(["gdalinfo", file_path], capture_output=True, text=True)

    os.remove(file_path)

    return {"filename": file.filename, "gdalinfo": result.stdout}

# 🟢 TRANSLATE: Converti raster in altro formato (GeoTIFF, PNG, JPEG)
@app.post("/translate/")
async def translate_raster(
    file: UploadFile = File(...), 
    output_format: str = Form("GTiff")
):
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_converted.{output_format.lower()}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdal_translate", "-of", output_format, input_path, output_path])

    os.remove(input_path)

    return {"message": "Raster converted", "output_file": output_path}

# 🟢 WARP: Riprojettare raster (es. WGS84 EPSG:4326)
@app.post("/warp/")
async def warp_raster(
    file: UploadFile = File(...), 
    epsg: str = Form("4326")
):
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_warped.tif"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdalwarp", "-t_srs", f"EPSG:{epsg}", input_path, output_path])

    os.remove(input_path)

    return {"message": "Raster reprojected", "output_file": output_path}

# 🟢 VECTOR INFO: Ottieni informazioni su file vettoriali
@app.post("/vector_info/")
async def get_vector_info(file: UploadFile = File(...)):
    file_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(["ogrinfo", file_path], capture_output=True, text=True)

    os.remove(file_path)

    return {"filename": file.filename, "vector_info": result.stdout}

# 🟢 RASTER TO VECTOR: Converte raster in vettoriale (ES. poligoni)
@app.post("/raster_to_vector/")
async def raster_to_vector(file: UploadFile = File(...), output_format: str = Form("GeoJSON")):
    input_path = f"{TEMP_DIR}/{uuid.uuid4()}_{file.filename}"
    output_path = f"{TEMP_DIR}/{uuid.uuid4()}_vectorized.{output_format.lower()}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["gdal_polygonize.py", input_path, "-f", output_format, output_path])

    os.remove(input_path)

    return {"message": "Raster converted to vector", "output_file": output_path}
