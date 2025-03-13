# GDAL API

## Descrizione
GDAL API è un'API REST basata su [FastAPI](https://fastapi.tiangolo.com/) che fornisce strumenti per l'elaborazione di file raster e vettoriali utilizzando [GDAL](https://gdal.org/).

## Caratteristiche principali
- **gdalinfo**: Ottieni informazioni su un file raster.
- **translate**: Converti un raster in un altro formato.
- **warp**: Riprojettare un raster in un altro sistema di riferimento.
- **vector_info**: Ottieni informazioni su un file vettoriale.
- **raster_to_vector**: Converti un raster in un file vettoriale.
- **wms_to_geotiff**: Scarica un'immagine da un WMS e la converte in GeoTIFF.
- **Monitoraggio dello stato**: Controlla lo stato di un'operazione e scarica il file risultante.

## Installazione

### Prerequisiti
- Python 3.8+
- GDAL installato nel sistema
- FastAPI e dipendenze

## 🏗 **Installation & Setup**

### sou **Using Conda
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

## Utilizzo

L'API espone diversi endpoint per l'elaborazione di dati raster e vettoriali. Puoi testare gli endpoint tramite l'interfaccia interattiva di Swagger disponibile su:
```
http://localhost:8000/docs
```

### Endpoint disponibili

#### Verifica lo stato dell'API
```http
GET /
```
Risposta:
```json
{"message": "GDAL REST API is running!"}
```

#### Ottieni informazioni su un raster
```http
POST /gdalinfo/
```
- **Parametri**: file raster come `multipart/form-data`
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Converti un raster in un altro formato
```http
POST /translate/
```
- **Parametri**: file raster, formato di output
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Riprojettare un raster in un altro sistema di riferimento
```http
POST /warp/
```
- **Parametri**: file raster, EPSG di destinazione
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Ottieni informazioni su un file vettoriale
```http
POST /vector_info/
```
- **Parametri**: file vettoriale
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Converti un raster in vettoriale
```http
POST /raster_to_vector/
```
- **Parametri**: file raster, formato di output
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Scarica un'immagine WMS e convertila in GeoTIFF
```http
GET /wms_to_geotiff/
```
- **Parametri**: URL WMS, strati, bbox, dimensioni, CRS, formato
- **Risposta**:
```json
{"process_id": "UUID univoco"}
```

#### Controlla lo stato di un'operazione
```http
GET /status/{process_id}
```
- **Risposta**:
```json
{"status": "success", "output": "Dettagli"}
```

#### Scarica il file generato
```http
GET /download/{process_id}
```
- **Risposta**: Il file elaborato in output.

## Pulizia dei file temporanei
L'API elimina automaticamente i file temporanei più vecchi di un'ora per evitare l'accumulo di dati inutilizzati.

## Licenza
Questa API è rilasciata sotto la licenza MIT.
