# Imagem base do Python
FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar e definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos da aplicação
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Definir a variável de ambiente para permitir que o Gunicorn ouça em todos os IPs
ENV PORT=8080
ENV HOST=0.0.0.0

EXPOSE 8080

# Comando para rodar o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app"]
