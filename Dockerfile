# Utilitzem una imatge lleugera de Python oficial
FROM python:3.10-slim

# Establim la carpeta de treball dins del contenidor
WORKDIR /app

# Copiem el fitxer de requeriments i instal·lem les llibreries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem tot el contingut del nostre projecte actual dins del contenidor
# Això inclourà server.py, la carpeta templates/, credentials.json i el token.json que ja vas generar
COPY . .

# Exposem el port 8000 que és el que fa servir Flask
EXPOSE 8000

# Executem l'aplicació
CMD ["python", "server.py"]
