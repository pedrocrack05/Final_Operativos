# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat, constr
import boto3
from botocore.exceptions import ClientError
import csv
import io
import os
from dotenv import load_dotenv


load_dotenv()


app = FastAPI(title="Sistemas Operativos - Final 2025")

# === Configuración S3 desde variables de entorno ===
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "tu-bucket-eia")
S3_KEY = os.getenv("S3_OBJECT_KEY", "personas.csv")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

s3_client = boto3.client("s3", region_name=AWS_REGION)

# === Modelo Pydantic para validar entrada ===
class Persona(BaseModel):
    nombre: constr(strip_whitespace=True, min_length=1)
    edad: conint(ge=0, le=120)
    altura: confloat(gt=0)  # en cm o m, como definas

# === Funciones auxiliares ===

def descargar_csv_desde_s3() -> list:
    """Descarga el CSV de S3 y retorna una lista de filas (dicts). Si no existe, retorna lista vacía."""
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        contenido = obj["Body"].read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(contenido))
        return list(reader)
    except ClientError as e:
        # Si no existe el archivo, empezamos desde cero
        if e.response["Error"]["Code"] in ("NoSuchKey", "NoSuchBucket"):
            return []
        raise

def subir_csv_a_s3(filas: list):
    """Sobrescribe en S3 el archivo CSV con las filas dadas."""
    if not filas:
        # Si está vacío, creamos solo encabezados
        headers = ["nombre", "edad", "altura"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
    else:
        headers = ["nombre", "edad", "altura"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for fila in filas:
            writer.writerow({
                "nombre": fila["nombre"],
                "edad": fila["edad"],
                "altura": fila["altura"],
            })

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

# === Endpoints ===

@app.post("/personas", summary="Guarda persona en CSV de S3")
def crear_persona(persona: Persona):
    # Descarga filas existentes (si hay)
    filas = descargar_csv_desde_s3()

    # Agrega nueva fila
    filas.append({
        "nombre": persona.nombre,
        "edad": str(persona.edad),
        "altura": str(persona.altura),
    })

    # Sube el mismo recurso CSV (un solo archivo vigente)
    try:
        subir_csv_a_s3(filas)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar en S3: {str(e)}")

    return {"mensaje": "Persona guardada correctamente", "total_registros": len(filas)}

@app.get("/personas/count", summary="Retorna número de filas del CSV en S3")
def contar_personas():
    filas = descargar_csv_desde_s3()
    # Si no hay archivo, 0 filas (sin drama)
    return {"filas": len(filas)}
