#!/bin/bash
# ============================================================
# Script: deploy.sh
# Descripción: Construye, etiqueta y sube la imagen Docker a AWS ECR.
# Lee credenciales desde .env (sin requerir aws configure)
# ============================================================

# Cargar variables de entorno desde .env
if [ -f "../.env" ]; then
  export $(grep -v '^#' ../.env | xargs)
elif [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ No se encontró archivo .env con credenciales AWS"
  exit 1
fi

# Variables base
AWS_REGION=${AWS_REGION:-"us-east-1"}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_NAME="fastapi-lambda"
IMAGE_TAG="latest"

echo "🔧 Región: $AWS_REGION"
echo "🔧 Cuenta AWS: $ACCOUNT_ID"

# 1️⃣ Crear repositorio si no existe
aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION >/dev/null 2>&1 || \
aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION

# 2️⃣ Construir imagen Docker
echo "🐳 Construyendo imagen Docker..."
docker build -t $REPO_NAME .

echo "📦 AWS_ACCOUNT_ID: $ACCOUNT_ID"
echo "🌍 AWS_REGION: $AWS_REGION"

# 3️⃣ Etiquetar imagen
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

# 4️⃣ Login en ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 5️⃣ Subir imagen
echo "🚀 Subiendo imagen a ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo "✅ Imagen publicada correctamente en AWS ECR."
