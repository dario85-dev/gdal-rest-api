# 🌍 GDAL REST API 🚀
A **lightweight REST API** for **geospatial data processing** using **GDAL** and **FastAPI**.  
It provides endpoints for **raster and vector operations**, such as extracting metadata, format conversions, reprojections, and raster-to-vector transformations.  

---

## 📌 **Features**
✅ **`gdalinfo`** → Get metadata of raster files  
✅ **`translate`** → Convert raster formats (GeoTIFF, PNG, JPEG, etc.)  
✅ **`warp`** → Reproject rasters to a different coordinate system  
✅ **`vector_info`** → Extract metadata from vector files (e.g., Shapefiles)  
✅ **`raster_to_vector`** → Convert raster files to vector polygons  

---

## ⚡ **Requirements**
- 🐍 Python 3.8+  
- 📦 GDAL (`osgeo/gdal`)  
- 🚀 FastAPI & Uvicorn  
- 🐳 Docker *(optional for containerization)*  
- ☁️ Kubernetes *(optional for deployment)*  

---

## 🏗 **Installation & Setup**

### sou **Using Conda
```sh
conda env create --prefix .venv -f environment.yml

conda activate .venv/

```

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-username/gdal-rest-api.git
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

## 📌 **API Endpoints & Requests**

### 🔹 1️⃣ Get Raster Metadata (`gdalinfo`)
```sh
curl -X 'POST' \
  'http://localhost:8000/gdalinfo/' \
  -F 'file=@/path/to/raster.tif'
```
#### 🔹 Response:
```json
{
  "filename": "raster.tif",
  "gdalinfo": "...metadata output..."
}
```

### 🔹 2️⃣ Convert Raster Format (`translate`)
```sh
curl -X 'POST' \
  'http://localhost:8000/translate/' \
  -F 'file=@/path/to/raster.tif' \
  -F 'output_format=PNG'
```
#### 🔹 Response:
```json
{
  "message": "Raster converted",
  "output_file": "/tmp/...converted.png"
}
```

### 🔹 3️⃣ Reproject Raster (`warp`)
```sh
curl -X 'POST' \
  'http://localhost:8000/warp/' \
  -F 'file=@/path/to/raster.tif' \
  -F 'epsg=4326'
```
#### 🔹 Response:
```json
{
  "message": "Raster reprojected",
  "output_file": "/tmp/...warped.tif"
}
```

### 🔹 4️⃣ Get Vector File Metadata (`vector_info`)
```sh
curl -X 'POST' \
  'http://localhost:8000/vector_info/' \
  -F 'file=@/path/to/vector.shp'
```
#### 🔹 Response:
```json
{
  "filename": "vector.shp",
  "vector_info": "...OGR metadata output..."
}
```

### 🔹 5️⃣ Convert Raster to Vector (`raster_to_vector`)
```sh
curl -X 'POST' \
  'http://localhost:8000/raster_to_vector/' \
  -F 'file=@/path/to/raster.tif' \
  -F 'output_format=GeoJSON'
```
#### 🔹 Response:
```json
{
  "message": "Raster converted to vector",
  "output_file": "/tmp/...vectorized.geojson"
}
```

---

### 📬 **Contributing**
Contributions are welcome! Please submit issues and pull requests.

### 📄 **License**
This project is licensed under the **MIT License**.

🚀 **Happy Mapping!** 🌍

