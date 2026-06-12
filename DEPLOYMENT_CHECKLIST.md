# 📋 CHECKLIST DE DEPLOYMENT - FASE 1
## CMC Proposal Generator → Producción

---

## ✅ PRE-DEPLOYMENT (En tu computadora)

### Paso 1: Verificar cambios locales
- [ ] Ejecutar validador local: `python validate_phase1.py`
- [ ] Confirmar que dice "✅ FASE 1 LISTA PARA DEPLOYMENT"
- [ ] Ejecutar tests de integración: `python test_integration.py`
- [ ] Confirmar que todos los tests pasan (8/8)

### Paso 2: Git Operations
```bash
# Ver cambios
git status

# Debe mostrar archivos modificados:
# - cmc_flask_server_render.py (logging agregado)
# - render.yaml (plan: standard)
# - cmc-cotizador.html (botón WhatsApp)

# Archivos nuevos:
# - railway.json
# - .env.example
# - README.md
# - DEPLOYMENT_GUIDE.md
# - VALIDATION_REPORT.md
# - validate_phase1.py
# - test_integration.py
# - apply_optimizations.py
```

### Paso 3: Commit a GitHub
```bash
# Agregar todos los cambios
git add .

# Commit con mensaje descriptivo
git commit -m "Fase 1: Validación completada - Listo para deployment

- ✅ 71/71 tests pasados
- ✅ PDF generation funcional
- ✅ Todos los endpoints validados
- ✅ Dockerfile optimizado
- ✅ Render.yaml con plan standard
- ✅ Botón WhatsApp agregado
- ✅ Logging mejorado
- ✅ Documentación completa"

# Push a GitHub
git push origin main

# Verificar en GitHub
# https://github.com/guillerhdez/cmc-proposal-generator/commits
```

---

## 🚀 DEPLOYMENT A RENDER (OPCIÓN A - RECOMENDADA)

### Paso 1: Crear cuenta Render
- [ ] Ir a https://render.com
- [ ] Click "Sign Up"
- [ ] Conectar con GitHub
- [ ] Autorizar acceso a repositorios

### Paso 2: Crear nuevo servicio
- [ ] Dashboard → "New +" → "Web Service"
- [ ] Seleccionar repositorio: `cmc-proposal-generator`
- [ ] Click "Connect"

### Paso 3: Configurar servicio
```
Name:                    cmc-proposal-generator
Environment:             Python
Region:                  (dejar por defecto)
Branch:                  main
Build Command:           pip install -r requirements.txt
Start Command:           python cmc_flask_server_render.py
Plan:                    Standard ($7/mes)
Python Version:          3.11
```

### Paso 4: Variables de entorno (opcional)
```
PORT=10000
FLASK_ENV=production
```

### Paso 5: Deploy
- [ ] Click "Create Web Service"
- [ ] Esperar 3-5 minutos por deploy
- [ ] Verás en logs: "=== Application is live ==="
- [ ] URL será: `https://cmc-proposal-generator.onrender.com`

### Paso 6: Verificar deployment
```bash
# Test health endpoint
curl https://cmc-proposal-generator.onrender.com/health

# Respuesta esperada:
# {"status":"ok","service":"CMC Proposal Generator",...}

# Abrir en navegador
# https://cmc-proposal-generator.onrender.com/cmc-cotizador.html
```

---

## 🚂 DEPLOYMENT A RAILWAY (OPCIÓN B)

### Paso 1: Crear cuenta Railway
- [ ] Ir a https://railway.app
- [ ] Click "Start Project"
- [ ] Conectar con GitHub
- [ ] Autorizar acceso

### Paso 2: Crear nuevo proyecto
- [ ] Dashboard → "New Project"
- [ ] GitHub Repo → `cmc-proposal-generator`
- [ ] Click "Deploy"

### Paso 3: Configurar variables
```
PORT=10000
FLASK_ENV=production
```

### Paso 4: Deploy automático
- [ ] Railway detecta `railway.json`
- [ ] Inicia build automáticamente
- [ ] Esperar 3-5 minutos

### Paso 5: Obtener URL
- [ ] En Railway dashboard
- [ ] Click en servicio
- [ ] Ver "Domains" → URL pública

---

## ✅ POST-DEPLOYMENT (Validar en producción)

### Test 1: Health Check
```bash
# Reemplazar [DOMAIN] con tu URL
curl https://[DOMAIN]/health

# Debe retornar:
# {"status":"ok","service":"CMC Proposal Generator","version":"2.0",...}
# En menos de 500ms
```

### Test 2: API Endpoints
```bash
# Ejecutivos
curl https://[DOMAIN]/api/executives
# Debe retornar JSON con 3 ejecutivos

# Servicios
curl https://[DOMAIN]/api/services
# Debe retornar JSON con 7 servicios
```

### Test 3: HTML/UI
- [ ] Abrir: `https://[DOMAIN]/cmc-cotizador.html`
- [ ] Debe cargar interfaz web
- [ ] Llenar formulario:
  - Ejecutivo: Daniel Flores
  - Empresa: Test Company
  - Contacto: Juan Pérez
  - WhatsApp: 5512345678
  - Giro: Tecnología
- [ ] Agregar servicio: Internet Dedicado
- [ ] Completar condiciones
- [ ] Click "Descargar PDF"
- [ ] Debe descargar PDF válido

### Test 4: PDF Generation
- [ ] PDF debe tener:
  - ✓ Tamaño > 100 KB
  - ✓ 4+ páginas
  - ✓ Datos del cliente visibles
  - ✓ Datos del ejecutivo visibles
  - ✓ Tabla de servicios

### Test 5: WhatsApp Integration
- [ ] Click "Compartir por WhatsApp"
- [ ] Debe abrir WhatsApp (si está instalado)
- [ ] Link debe contener: `wa.me/[numero]`

### Test 6: Performance
```bash
# Health check debe ser < 500ms
time curl https://[DOMAIN]/health

# PDF generation debe ser < 3 segundos
time curl -X POST https://[DOMAIN]/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 🔍 TROUBLESHOOTING

### Error: "Build failed"
**Solución:**
- [ ] Verificar que requirements.txt está en raíz
- [ ] Verificar que no hay errores en Python
- [ ] Revisar logs: `git push` → ver build logs en Render/Railway

### Error: "Application not loading"
**Solución:**
- [ ] Verificar que Puerto es 10000 (env PORT)
- [ ] Verificar logs en Render/Railway dashboard
- [ ] Ejecutar `python cmc_flask_server_render.py` localmente

### Error: "PDF no se descarga"
**Solución:**
- [ ] Verificar carpeta `images/` existe en servidor
- [ ] Revisar logs: buscar "Error generating PDF"
- [ ] Probar POST /generate-pdf con curl

### Error: "CORS no funciona"
**Solución:**
- [ ] Verificar `CORS(app)` está en Flask server
- [ ] Verificar headers: `Access-Control-Allow-Origin`

---

## 📊 CHECKLIST FINAL

### Antes de ir a Producción
- [ ] Código pushed a GitHub
- [ ] Validador pasado: 63/63 ✅
- [ ] Tests pasados: 8/8 ✅
- [ ] PDF generado correctamente
- [ ] Render/Railway configurado
- [ ] Variables de entorno correctas

### Después del Deployment
- [ ] Health check responde
- [ ] API endpoints funcionan
- [ ] HTML carga correctamente
- [ ] PDF se genera sin errores
- [ ] WhatsApp integration funciona
- [ ] Performance < 500ms health check
- [ ] Performance < 3s PDF generation

### Monitoreo Permanente
- [ ] Revisar logs diarios (primeros días)
- [ ] Configurar alertas en Render/Railway
- [ ] Monitorear uptime
- [ ] Revisar uso de recursos

---

## 🎯 ROLLBACK (Si algo falla)

### Quick Fix en Código
```bash
# Si necesitas revertir cambios:
git revert HEAD
git push

# Render/Railway redeploy automáticamente
```

### Reset Completo
```bash
# Si todo se arruinó:
git reset --hard HEAD~1
git push --force

# O deletear servicio en Render/Railway y recrear
```

---

## 📞 SOPORTE

### Si tienes problemas:

1. **Error en build:**
   - Ver logs en Render/Railway dashboard
   - Ejecutar `python validate_phase1.py` localmente
   - Revisar requirements.txt

2. **Error en runtime:**
   - Ver logs en Render/Railway dashboard
   - Buscar "Error" o "Exception"
   - Ejecutar `python test_integration.py` localmente

3. **Performance lenta:**
   - Cambiar a plan superior en Render
   - Revisar CSV en logs
   - Optimizar imágenes si es necesario

4. **CORS/API issues:**
   - Verificar CORS(app) en Flask
   - Ver headers en browser DevTools
   - Ejecutar curl para debugging

---

## 📋 RESUMEN

**Estado Actual:** ✅ LISTO PARA DEPLOYMENT

**Próximos pasos:**
1. Hacer commit a GitHub
2. Elegir Render o Railway
3. Seguir pasos de deployment
4. Validar en producción
5. ¡Listo! 🚀

---

**¿Necesitas ayuda?**
- Lee DEPLOYMENT_GUIDE.md para más detalles
- Ejecuta validate_phase1.py para verificar localmente
- Ejecuta test_integration.py para test completo

---

✅ **CHECKLIST COMPLETADO - ¡A PRODUCCIÓN!**
