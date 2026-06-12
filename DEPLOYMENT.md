# 🚀 Deployment - Railway

**Plataforma única:** Railway (Render fue dado de baja)

**URL de producción:** https://web-production-9371f.up.railway.app

---

## Configuración del servicio

Railway detecta automáticamente `railway.json` y `Dockerfile`:

```json
{
  "build": { "builder": "dockerfile" },
  "deploy": {
    "startCommand": "python cmc_flask_server.py",
    "restartPolicyType": "always",
    "restartPolicyMaxRetries": 5
  }
}
```

## Deploy

1. Push a `main` en GitHub
2. Railway detecta el push y redeploya automáticamente (3-5 min)
3. Verificar:
   ```bash
   curl https://web-production-9371f.up.railway.app/health
   ```
   Respuesta esperada:
   ```json
   {"status":"ok","service":"CMC Proposal Generator","version":"2.0","environment":"production"}
   ```

## Validar la app completa

```
https://web-production-9371f.up.railway.app/cmc-cotizador.html
```

1. Llenar Paso 1 (ejecutivo + datos del cliente)
2. Paso 2: agregar al menos un servicio
3. Paso 3: revisar resumen → "Descargar PDF"

## Variables de entorno

Ver `.env.example`. Actualmente solo se requiere `PORT` (Railway lo provee automáticamente).

## Troubleshooting

| Problema | Causa probable | Solución |
|----------|----------------|----------|
| `ModuleNotFoundError` | Build no instaló dependencias | Verificar que `railway.json` usa `"builder": "dockerfile"` y que el Dockerfile corre `pip install -r requirements.txt` |
| PDF no descarga | Carpeta `images/` faltante en build | Verificar `RUN test -d images` en Dockerfile pasa |
| App no responde | Deploy en progreso o crash | Ver logs en Railway dashboard → servicio → "Deployments" |

## Validar localmente antes de deployar

```bash
python validate_phase1.py
python test_integration.py
```

Ambos deben pasar sin fallos críticos antes de hacer push.
