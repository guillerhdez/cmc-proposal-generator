# CMC Proposal Generator

Generador automático de propuestas comerciales para CMC Network.

## Características

- 📝 Formulario web intuitivo (3 pasos)
- 📄 Generación de PDF profesional
- 📱 Integración con WhatsApp
- 🎨 Diseño responsivo
- ⚡ Rápido y confiable

## Stack Técnico

- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **Backend:** Flask (Python)
- **PDF:** ReportLab + PyPDF2
- **Cloud:** Render o Railway
- **Próximamente:** Claude API + PostgreSQL

## Instalación Local

```bash
git clone https://github.com/guillerhdez/cmc-proposal-generator
cd cmc-proposal-generator
pip install -r requirements.txt
python cmc_flask_server_render.py
```

Abre http://localhost:5000/cmc-cotizador.html

## Deployment

Ver `DEPLOYMENT_GUIDE.md` para instrucciones completas.

### Render (Recomendado)
1. Push a GitHub
2. Conectar a Render
3. Esperar deployment automático

### Railway
1. Crear proyecto desde repo
2. Deploy automático

## API Endpoints

- `GET /health` - Health check
- `GET /api/executives` - Lista de ejecutivos
- `GET /api/services` - Catálogo de servicios
- `POST /generate-pdf` - Generar PDF

## Roadmap

- [ ] Fase 1: Core ✓
- [ ] Fase 2: Claude API (textos personalizados)
- [ ] Fase 3: Base de datos + Auditoría
- [ ] Fase 4: Integración Odoo

## Licencia

© 2026 CMC Network. Todos los derechos reservados.
