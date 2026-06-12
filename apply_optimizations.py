#!/usr/bin/env python3
"""
Aplicador automático de optimizaciones Fase 1
Ejecutar en el directorio raíz del proyecto
"""

import os
import re

class Phase1Optimizer:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.changes_made = []
    
    def log_change(self, message):
        print(f"✓ {message}")
        self.changes_made.append(message)
    
    def optimize_render_yaml(self):
        """Cambiar plan de 'free' a 'standard'"""
        print("\n📦 Optimizando render.yaml...")
        
        render_file = os.path.join(self.project_root, 'render.yaml')
        with open(render_file, 'r') as f:
            content = f.read()
        
        original = content
        content = content.replace('plan: free', 'plan: standard')
        
        if content != original:
            with open(render_file, 'w') as f:
                f.write(content)
            self.log_change("render.yaml: plan cambiado a 'standard'")
        else:
            print("⚠️  render.yaml ya tiene plan correcto o no contiene 'plan: free'")
    
    def optimize_dockerfile(self):
        """Mejorar Dockerfile con multi-stage build"""
        print("\n🐳 Optimizando Dockerfile...")
        
        dockerfile = os.path.join(self.project_root, 'Dockerfile')
        
        new_dockerfile = '''# Multi-stage build para optimizar
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
'''
        
        with open(dockerfile, 'w') as f:
            f.write(new_dockerfile)
        
        self.log_change("Dockerfile: Mejorado con multi-stage build")
    
    def create_railway_json(self):
        """Crear railway.json si no existe"""
        print("\n🚂 Creando railway.json...")
        
        railway_file = os.path.join(self.project_root, 'railway.json')
        
        if os.path.exists(railway_file):
            print("⚠️  railway.json ya existe")
            return
        
        railway_config = '''{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "python cmc_flask_server_render.py",
    "restartPolicyType": "always",
    "restartPolicyMaxRetries": 5
  }
}
'''
        
        with open(railway_file, 'w') as f:
            f.write(railway_config)
        
        self.log_change("railway.json: Creado para Railway deployment")
    
    def create_env_example(self):
        """Crear .env.example"""
        print("\n🔑 Creando .env.example...")
        
        env_file = os.path.join(self.project_root, '.env.example')
        
        if os.path.exists(env_file):
            print("⚠️  .env.example ya existe")
            return
        
        env_content = '''# Configuración Render/Railway
PORT=10000
FLASK_ENV=production

# Fase 2: Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Fase 3: Base de Datos
DATABASE_URL=postgresql://user:pass@host/db
'''
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        self.log_change(".env.example: Creado")
    
    def optimize_flask_server(self):
        """Mejorar logging en Flask"""
        print("\n🔧 Optimizando cmc_flask_server_render.py...")
        
        flask_file = os.path.join(self.project_root, 'cmc_flask_server_render.py')
        
        with open(flask_file, 'r') as f:
            content = f.read()
        
        # Verificar si ya tiene logging
        if 'import logging' in content:
            print("⚠️  Logging ya está configurado")
            return
        
        # Agregar logging después de imports
        import_section = '''"""
CMC Network - Servidor Flask para Render.com
Generador de propuestas comerciales PDF

Versión optimizada para producción en la nube.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from cmc_pdf_generator_visual_v3 import CMCProposalGeneratorV3
import io
import os
from datetime import datetime
import logging'''
        
        content = content.replace(
            '''"""
CMC Network - Servidor Flask para Render.com
Generador de propuestas comerciales PDF

Versión optimizada para producción en la nube.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from cmc_pdf_generator_visual_v3 import CMCProposalGeneratorV3
import io
import os
from datetime import datetime''',
            import_section
        )
        
        # Agregar configuración de logging
        logging_config = '''
# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)'''
        
        app_creation = 'app = Flask(__name__)\nCORS(app)'
        content = content.replace(
            'app = Flask(__name__)\nCORS(app)',
            logging_config + '\n\napp = Flask(__name__)\nCORS(app)'
        )
        
        with open(flask_file, 'w') as f:
            f.write(content)
        
        self.log_change("Flask: Logging mejorado")
    
    def optimize_html_whatsapp(self):
        """Agregar botón de compartir por WhatsApp"""
        print("\n🌐 Optimizando cmc-cotizador.html...")
        
        html_file = os.path.join(self.project_root, 'cmc-cotizador.html')
        
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Verificar si ya tiene el botón
        if 'shareViaWhatsApp' in content:
            print("⚠️  Botón WhatsApp ya existe")
            return
        
        # Agregar botón después del botón Descargar PDF
        old_button = '''<button class="btn-success" id="downloadBtn" onclick="generateAndDownloadPDF()">📥 Descargar PDF</button>
            </div>
        </div>'''
        
        new_button = '''<button class="btn-success" id="downloadBtn" onclick="generateAndDownloadPDF()">📥 Descargar PDF</button>
                <button class="btn-whatsapp" id="shareBtn" onclick="shareViaWhatsApp()" style="background: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-left: 10px;">📱 Compartir por WhatsApp</button>
            </div>
        </div>'''
        
        content = content.replace(old_button, new_button)
        
        # Agregar función JavaScript
        old_script_end = '''    function showLoading(show) {
        document.getElementById('loading').classList.toggle('active', show);
    }

    // ========== INICIALIZACIÓN =========='''
        
        new_script = '''    function showLoading(show) {
        document.getElementById('loading').classList.toggle('active', show);
    }

    function shareViaWhatsApp() {
        const whatsapp = document.getElementById('clientWhatsApp').value;
        const company = document.getElementById('clientCompany').value;
        
        if (!whatsapp) {
            showAlert('Ingresa el número de WhatsApp del cliente', 'error');
            return;
        }
        
        // Formatear número (remover espacios, guiones)
        const cleanWhatsApp = whatsapp.replace(/[^0-9]/g, '');
        const message = `Hola, te envío la propuesta de servicios para ${company} de CMC Network 🚀`;
        const url = `https://wa.me/${cleanWhatsApp}?text=${encodeURIComponent(message)}`;
        window.open(url, '_blank');
    }

    // ========== INICIALIZACIÓN =========='''
        
        content = content.replace(old_script_end, new_script)
        
        with open(html_file, 'w') as f:
            f.write(content)
        
        self.log_change("HTML: Botón WhatsApp agregado")
    
    def create_readme(self):
        """Crear README.md"""
        print("\n📖 Creando README.md...")
        
        readme_file = os.path.join(self.project_root, 'README.md')
        
        if os.path.exists(readme_file):
            print("⚠️  README.md ya existe")
            return
        
        readme = '''# CMC Proposal Generator

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
'''
        
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        self.log_change("README.md: Creado")
    
    def run_all_optimizations(self):
        """Ejecutar todas las optimizaciones"""
        print("\n" + "="*60)
        print("OPTIMIZADOR FASE 1 - CMC PROPOSAL GENERATOR")
        print("="*60)
        
        self.optimize_render_yaml()
        self.optimize_dockerfile()
        self.create_railway_json()
        self.create_env_example()
        self.optimize_flask_server()
        self.optimize_html_whatsapp()
        self.create_readme()
        
        # Resumen
        print("\n" + "="*60)
        print(f"✅ COMPLETADO: {len(self.changes_made)} cambios aplicados")
        print("="*60)
        
        for change in self.changes_made:
            print(f"  ✓ {change}")
        
        print("\n📋 Próximos pasos:")
        print("  1. Revisar cambios: git diff")
        print("  2. Commit: git add . && git commit -m 'Fase 1: Optimizaciones pre-deployment'")
        print("  3. Push: git push origin main")
        print("  4. Deploy a Render o Railway")
        print("  5. Ver DEPLOYMENT_GUIDE.md para detalles")


if __name__ == '__main__':
    optimizer = Phase1Optimizer()
    optimizer.run_all_optimizations()
