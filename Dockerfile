# Multi-stage build para optimizar
FROM python:3.11-slim as builder

WORKDIR /tmp
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias del stage anterior
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copiar aplicación
COPY . .

# Verificar que existen imágenes
RUN test -d images && echo "✓ Images directory found" || (echo "✗ Images directory missing" && exit 1)

# Verificar archivos críticos
RUN test -f cmc-cotizador.html && echo "✓ HTML found" || (echo "✗ HTML missing" && exit 1)

EXPOSE 10000
ENV PORT=10000

CMD ["python", "cmc_flask_server_render.py"]
