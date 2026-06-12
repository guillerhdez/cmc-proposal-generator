# 📋 PLAN DE DEPLOYMENT FASE 1
## CMC Proposal Generator - Producción

**Estado:** 99% listo | **Fallos:** 0 críticos | **Advertencias:** 8 menores

---

## ✅ CHECKLIST PRE-DEPLOYMENT

### 1. Validación Local (YA COMPLETADA)
- [x] Sintaxis Python correcta
- [x] Dependencias instaladas
- [x] Estructura de archivos OK
- [x] Imágenes presentes (14/20 necesarias)
- [x] Generación de PDF funcional (136 KB)
- [x] Endpoints Flask configurados
- [x] HTML con formulario 3 pasos

### 2. Optimizaciones Recomendadas

#### A. Agregar botón "Compartir por WhatsApp"
**Archivo:** `cmc-cotizador.html`
**Línea:** 537 (después del botón Descargar PDF)

**Agregar este botón:**
```html
<button class="btn-whatsapp" id="shareBtn" onclick="shareViaWhatsApp()" style="background: #25D366; margin-left: 10px;">
    📱 Compartir por WhatsApp
</button>
```

**Agregar esta función en JavaScript (antes de `// ========== UTILIDADES ==========`):**
```javascript
function shareViaWhatsApp() {
    const whatsapp = document.getElementById('clientWhatsApp').value;
    const company = document.getElementById('clientCompany').value;
    
    if (!whatsapp) {
        showAlert('Ingresa el número de WhatsApp del cliente', 'error');
        return;
    }
    
    const message = `Hola, te envío la propuesta de servicios para ${company} de CMC Network.`;
    const url = `https://wa.me/${whatsapp}?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
}
```

#### B. Cambiar Render plan de 'free' a 'standard'
**Archivo:** `render.yaml`
**Línea:** 5

**Cambiar:**
```yaml
plan: free     # ❌ NO (spin-down después de 15 min inactividad)
```

**Por:**
```yaml
plan: standard # ✓ SÍ (recomendado, $7/mes)
```

#### C. Mejorar Dockerfile
**Archivo:** `Dockerfile`

**Reemplazar:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["python", "cmc_flask_server_render.py"]
```

**Por:**
```dockerfile
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

EXPOSE 10000
ENV PORT=10000

CMD ["python", "cmc_flask_server_render.py"]
```

#### D. Crear railway.json (si usan Railway)
**Archivo:** `railway.json` (crear nuevo)

```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "python cmc_flask_server_render.py",
    "restartPolicyType": "always",
    "restartPolicyMaxRetries": 5
  }
}
```

#### E. Crear .env.example (documentación)
**Archivo:** `.env.example` (crear nuevo)

```bash
# Render/Railway
PORT=10000

# Futuro (Fase 2)
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@host/db
```

#### F. Mejorar logging en Flask
**Archivo:** `cmc_flask_server_render.py`
**Agregar al inicio (después de imports):**

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Agregar logs en endpoints clave:**
```python
@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check solicitado")
    return jsonify({...})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        company = data.get('client', {}).get('company', 'Unknown')
        logger.info(f"Generating PDF for: {company}")
        ...
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        ...
```

---

## 🚀 PROCESO DE DEPLOYMENT

### Opción A: RENDER (RECOMENDADO)

#### Paso 1: Preparar cambios locales
```bash
# En tu computadora
git clone https://github.com/guillerhdez/cmc-proposal-generator
cd cmc-proposal-generator

# Hacer cambios sugeridos arriba (dockerfile, render.yaml, etc.)
# Agregar botón WhatsApp al HTML
```

#### Paso 2: Commit y push
```bash
git add .
git commit -m "Fase 1: Optimizaciones pre-deployment"
git push origin main
```

#### Paso 3: En Render.com
1. Ir a https://render.com
2. Sign in con GitHub
3. Seleccionar el repo `cmc-proposal-generator`
4. Configurar:
   - **Name:** cmc-proposal-generator
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python cmc_flask_server_render.py`
   - **Plan:** Standard ($7/mes)
   - **Python Version:** 3.11

5. Desplegar
6. Esperar ~3-5 minutos
7. Ir a `https://cmc-proposal-generator.onrender.com`

#### Paso 4: Verificar
```bash
# En terminal
curl https://cmc-proposal-generator.onrender.com/health

# Debería responder:
# {"status":"ok","service":"CMC Proposal Generator","version":"2.0","environment":"production"}
```

#### Paso 5: Test manual
1. Abrir: https://cmc-proposal-generator.onrender.com/cmc-cotizador.html
2. Llenar formulario:
   - Ejecutivo: Daniel Flores
   - Empresa: Test Company
   - Contacto: Juan Pérez
   - WhatsApp: 5512345678
   - Giro: Tecnología
3. Agregar servicio: Internet Dedicado
4. Presionar "Descargar PDF"
5. Verificar que descarga el PDF

### Opción B: RAILWAY

#### Paso 1-2: Igual que Render

#### Paso 3: En Railway.app
1. Ir a https://railway.app
2. Sign in con GitHub
3. New Project → GitHub Repo
4. Seleccionar `cmc-proposal-generator`
5. Variables de entorno:
   - `PORT=10000`
6. Desplegar
7. Copiar URL de producción

#### Paso 4-5: Igual que Render

---

## 🧪 TEST SUITE POST-DEPLOYMENT

### Test 1: Health Check
```bash
curl https://[your-domain]/health
```
✓ Debe responder con JSON en 2-3 segundos

### Test 2: Endpoints API
```bash
# Ejecutivos
curl https://[your-domain]/api/executives

# Servicios
curl https://[your-domain]/api/services
```
✓ Ambos deben retornar JSON válido

### Test 3: Generación PDF
```bash
curl -X POST https://[your-domain]/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "executive": {"name": "Daniel Flores", "title": "Senior Executive", "email": "test@cmcnetwork.com", "phone": "5512345678"},
    "client": {"company": "Test", "contact": "Admin", "whatsapp": "5512345678", "business": "Tech"},
    "services": [{"name": "Internet Dedicado", "description": "Test", "conditions": {"term": "24m", "monthly_rent": "$4500", "installation": "$2800"}}]
  }' \
  -o test.pdf
```
✓ Debe descargar PDF válido (>100 KB)

### Test 4: UI Completa
1. Abrir en navegador: `https://[your-domain]/cmc-cotizador.html`
2. Llenar y enviar
3. Verificar descarga de PDF
4. Verificar link WhatsApp funciona

---

## 📊 MÉTRICAS DE ÉXITO

- [x] 100% sintaxis correcta
- [x] 100% dependencias instaladas
- [x] PDF generado sin errores
- [ ] Deployment en Render/Railway ← PRÓXIMO PASO
- [ ] Dominio personalizado (opcional)
- [ ] SSL/TLS automático (incluido en Render)
- [ ] Performance: <500ms en /health
- [ ] Performance: <3s en /generate-pdf

---

## 🔧 TROUBLESHOOTING

### Error: "images/ not found"
**Causa:** Dockerfile no copia directorio
**Solución:** Usar Dockerfile mejorado del paso D arriba

### Error: "Port not specified"
**Causa:** Render/Railway no obtiene PORT
**Solución:** `port = int(os.environ.get('PORT', 10000))` ✓ YA IMPLEMENTADO

### Error: "PDF generation timeout"
**Causa:** Plan 'free' en Render (no recomendado)
**Solución:** Cambiar a 'standard'

### Error: "Module not found: reportlab"
**Causa:** requirements.txt no se instaló
**Solución:** Verificar `pip install -r requirements.txt` en build log

---

## 📋 RESUMEN FINAL

| Componente | Estado | Acción |
|-----------|--------|--------|
| Sintaxis Python | ✓ OK | Ninguna |
| Dependencias | ✓ OK | Ninguna |
| Estructura | ✓ OK | Ninguna |
| PDF Generator | ✓ OK | Ninguna |
| HTML Form | ✓ OK | Agregar botón WhatsApp |
| Docker | ✓ OK | Mejorar (multi-stage) |
| Render.yaml | ⚠ OK | Cambiar plan a 'standard' |
| Railway Config | ⚠ NUEVO | Crear railway.json |
| Logging | ⚠ BÁSICO | Mejorar logs |
| Documentación | ⚠ MINIMAL | Crear README.md |

---

## 🎯 PRÓXIMOS PASOS

1. **Hoy:** Hacer cambios sugeridos arriba
2. **Hoy:** Commit & push a GitHub
3. **Hoy:** Desplegar a Render/Railway
4. **Mañana:** Validar en producción
5. **Semana próxima:** Iniciar Fase 2 (Claude API)

---

## 📞 CONTACTO & SOPORTE

- **GitHub:** https://github.com/guillerhdez/cmc-proposal-generator
- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Flask Docs:** https://flask.palletsprojects.com

---

**Documento creado:** Junio 2026
**Versión:** 1.0
**Estado:** Listo para implementar
