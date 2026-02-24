FROM python:3.11-slim

# Evita arquivos .pyc e logs desnecessários
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Porta da API
EXPOSE 8000

# Comando para subir a API
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]