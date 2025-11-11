# Imagen base oficial de AWS Lambda para Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# Copiamos los archivos necesarios
COPY app.py requirements.txt ./

# Instalamos dependencias
RUN pip install -r requirements.txt

# Definimos el handler compatible con Lambda
CMD ["app.mangum"]
