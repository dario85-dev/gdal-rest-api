# GDAL API

## Description
GDAL API is a REST API based on [FastAPI](https://fastapi.tiangolo.com/) that provides tools for processing raster and vector files using [GDAL](https://gdal.org/).

## Main Features
- **gdalinfo**: Get information about a raster file.
- **translate**: Convert a raster into another format.
- **warp**: Reproject a raster to another reference system.
- **vector_info**: Get information about a vector file.
- **raster_to_vector**: Convert a raster into a vector file.
- **wms_to_geotiff**: Download an image from a WMS and convert it to GeoTIFF.
- **Process Monitoring**: Check the status of an operation and download the resulting file.

## Installation

### Prerequisites
- Python 3.8+
- GDAL installed on the system
- FastAPI and dependencies

## 🏗 **Installation & Setup**

### 🔧 **Using Conda**
```sh
conda env create --prefix .venv -f environment.yml

conda activate .venv/
```

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/dario85-dev/gdal-rest-api.git
cd gdal-rest-api
```

### 2️⃣ **Install Dependencies**
```sh
pip install -r app/requirements.txt
```

### 3️⃣ **Run the API**
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 🐳 **Docker Setup** *(Optional)*
```sh
docker build -t gdal-rest-api .
docker run -p 8000:8000 gdal-rest-api
```

### ☁️ **Kubernetes Deployment** *(Optional)*
```sh
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get svc gdal-api-service
```

Once deployed, access the API at:
```
http://<EXTERNAL-IP>/gdalinfo/
```

---

## Usage

The API exposes several endpoints for processing raster and vector data. You can test the endpoints using the interactive Swagger interface available at:
```
http://localhost:8000/docs
```

### Available Endpoints

#### Check API Status
```http
GET /
```
Response:
```json
{"message": "GDAL REST API is running!"}
```

#### Get Information about a Raster
```http
POST /gdalinfo/
```
- **Parameters**: Raster file as `multipart/form-data`
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Convert a Raster into Another Format
```http
POST /translate/
```
- **Parameters**: Raster file, output format
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Reproject a Raster to Another Reference System
```http
POST /warp/
```
- **Parameters**: Raster file, target EPSG
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Get Information about a Vector File
```http
POST /vector_info/
```
- **Parameters**: Vector file
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Convert a Raster into a Vector File
```http
POST /raster_to_vector/
```
- **Parameters**: Raster file, output format
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Download a WMS Image and Convert it to GeoTIFF
```http
GET /wms_to_geotiff/
```
- **Parameters**: WMS URL, layers, bbox, dimensions, CRS, format
- **Response**:
```json
{"process_id": "Unique UUID"}
```

#### Check the Status of an Operation
```http
GET /status/{process_id}
```
- **Response**:
```json
{"status": "success", "output": "Details"}
```

#### Download the Processed File
```http
GET /download/{process_id}
```
- **Response**: The processed output file.

## Temporary File Cleanup
The API automatically deletes temporary files older than one hour to prevent unnecessary data accumulation.

## License
This API is released under the MIT license.
