"""
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
import logging


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ejecutivos disponibles
EXECUTIVES = {
    'daniel_flores': {
        'name': 'Daniel Flores',
        'title': 'Senior Executive',
        'email': 'dflores@cmcnetworkmx.com',
        'phone': '55 1929 8160'
    },
    'julio_ramirez': {
        'name': 'Julio Ramírez',
        'title': 'Sales Executive',
        'email': 'jramirez@cmcnetworkmx.com',
        'phone': '55 1929 5005'
    },
    'tania_quijada': {
        'name': 'Tania Quijada',
        'title': 'Gerente Comercial',
        'email': 'g.comercial@cmcnetworkmx.com',
        'phone': '55 1930 6882'
    }
}

# Servicios disponibles
SERVICES = [
    {
        'id': 'internet_dedicado',
        'name': 'Internet Dedicado',
        'description': 'Conectividad dedicada con fibra óptica o microondas',
        'default_term': '24 meses',
        'default_rent': '$4,500',
        'default_installation': '$2,800'
    },
    {
        'id': 'internet_eventos',
        'name': 'Internet para Eventos',
        'description': 'Solución temporal para eventos y conferencias',
        'default_term': '1 día - 3 meses',
        'default_rent': 'Desde $500/día',
        'default_installation': 'Sin costo'
    },
    {
        'id': 'internet_satelital',
        'name': 'Internet Satelital',
        'description': 'Cobertura en zonas remotas y de difícil acceso',
        'default_term': '24 meses',
        'default_rent': '$3,500',
        'default_installation': '$2,000'
    },
    {
        'id': 'conectividad_lte',
        'name': 'Conectividad LTE',
        'description': 'Red móvil de alta velocidad',
        'default_term': '12 meses',
        'default_rent': '$2,500',
        'default_installation': '$1,500'
    },
    {
        'id': 'telefonia_ip',
        'name': 'Telefonía IP / Cloud PBX',
        'description': 'Sistema de comunicaciones en la nube',
        'default_term': '12 meses',
        'default_rent': '$1,550',
        'default_installation': 'Sin costo'
    },
    {
        'id': 'ciberseguridad',
        'name': 'Ciberseguridad Integral',
        'description': 'Soluciones Fortinet, WatchGuard y Sophos',
        'default_term': '12 meses',
        'default_rent': '$3,000',
        'default_installation': '$1,000'
    },
    {
        'id': 'soluciones_iot',
        'name': 'Soluciones IoT',
        'description': 'Gestión, automatización y monitoreo',
        'default_term': '12 meses',
        'default_rent': '$2,800',
        'default_installation': '$1,500'
    }
]

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'service': 'CMC Proposal Generator',
        'version': '2.0',
        'environment': 'production'
    }), 200

@app.route('/api/executives', methods=['GET'])
def get_executives():
    """Retorna lista de ejecutivos disponibles"""
    return jsonify(EXECUTIVES), 200

@app.route('/api/services', methods=['GET'])
def get_services():
    """Retorna catálogo de servicios"""
    return jsonify(SERVICES), 200

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Genera PDF de propuesta
    
    Body esperado:
    {
        "executive": {"name": "...", "title": "...", "email": "...", "phone": "..."},
        "client": {
            "company": "...",
            "contact": "...",
            "phone": "...",
            "whatsapp": "...",
            "email": "...",
            "business": "...",
            "fiscal_address": "...",
            "site_address": "..."
        },
        "services": [{"name": "...", "description": "...", "conditions": {...}}]
    }
    """
    try:
        data = request.get_json()
        
        # Validar datos
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'executive' not in data or 'client' not in data or 'services' not in data:
            return jsonify({'error': 'Missing required fields: executive, client, services'}), 400
        
        # Validar cliente
        if not data['client'].get('company'):
            return jsonify({'error': 'Client company name is required'}), 400
        
        # Log de datos del cliente (auditoría / futura integración Odoo)
        client = data['client']
        logger.info(
            "Proposal request | company=%s | contact=%s | phone=%s | whatsapp=%s | "
            "email=%s | business=%s | fiscal_address=%s | site_address=%s | services=%s",
            client.get('company'),
            client.get('contact'),
            client.get('phone'),
            client.get('whatsapp'),
            client.get('email'),
            client.get('business'),
            client.get('fiscal_address'),
            client.get('site_address'),
            [s.get('name') for s in data.get('services', [])]
        )
        
        # Generar PDF
        # images_dir apunta al subdirectorio 'images/' donde están las imágenes de Canva
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        generator = CMCProposalGeneratorV3(images_dir=images_dir)
        pdf_bytes = generator.generate(data)
        
        # Crear nombre de archivo
        company_name = data['client'].get('company', 'Propuesta').replace(' ', '_')
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'CMC_Propuesta_{company_name}_{date_str}.pdf'
        
        # Retornar PDF
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

@app.route('/cmc-cotizador.html', methods=['GET'])
def serve_cotizador():
    """Sirve la app web del cotizador"""
    try:
        with open('cmc-cotizador.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'App not found'}), 404

@app.route('/', methods=['GET'])
def index():
    """Redirige a la app web"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CMC Proposal Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #001F3D 0%, #00BCD4 100%);
            }
            .container {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #001F3D;
                margin: 0 0 10px 0;
            }
            p {
                color: #555;
                margin: 0 0 20px 0;
            }
            a {
                display: inline-block;
                background: #00BCD4;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                transition: background 0.3s;
            }
            a:hover {
                background: #001F3D;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 CMC Proposal Generator</h1>
            <p>Generador de propuestas comerciales</p>
            <a href="/cmc-cotizador.html">Abrir Cotizador →</a>
        </div>
    </body>
    </html>
    '''

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Para Render: escuchar en 0.0.0.0 y puerto desde variable de entorno
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
