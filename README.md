# CMC Proposal Generator

Generador automático de propuestas comerciales para CMC Network.

**Producción:** https://web-production-9371f.up.railway.app/cmc-cotizador.html

## Características

- 📝 Formulario web en 3 pasos (Ejecutivo & Cliente → Servicios → Resumen y descarga)
- 🧾 Datos completos del cliente (contacto, direcciones) listos para integración con Odoo
- 📄 Generación de PDF profesional con resumen de servicios y datos del cliente
- 📱 Integración con WhatsApp (compartir propuesta directamente)
- 🎨 Diseño responsivo
- ⚡ Rápido y confiable

## Stack Técnico

- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **Backend:** Flask (Python 3.11)
- **PDF:** ReportLab + PyPDF2
- **Cloud:** Railway (Docker)
- **Próximamente:** Claude API + PostgreSQL + integración Odoo

## Instalación Local

```bash
git clone https://github.com/guillerhdez/cmc-proposal-generator
cd cmc-proposal-generator
pip install -r requirements.txt
python cmc_flask_server.py
```

Abre http://localhost:5000/cmc-cotizador.html

## Deployment

Ver `DEPLOYMENT.md` para instrucciones de Railway.

## API Endpoints

- `GET /health` - Health check
- `GET /api/executives` - Lista de ejecutivos
- `GET /api/services` - Catálogo de servicios
- `POST /generate-pdf` - Generar PDF de propuesta

## Validación

```bash
python validate_phase1.py    # Validación estática (sintaxis, estructura, config)
python test_integration.py   # Tests de integración (levanta el servidor y prueba endpoints)
```

## Roadmap

- [x] Fase 1: Core (formulario, PDF, deploy)
- [x] Fase 1.5: Datos completos del cliente (para Odoo)
- [ ] Fase 2: Claude API (textos personalizados por servicio)
- [ ] Fase 3: Base de datos + Auditoría
- [ ] Fase 4: Integración Odoo (creación automática de contacto/oportunidad)

## Licencia

© 2026 CMC Network. Todos los derechos reservados.
