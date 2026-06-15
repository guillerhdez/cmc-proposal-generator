"""
CMC Network - Servidor Flask
Generador de propuestas comerciales PDF

Versión optimizada para producción en la nube (Railway).
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from cmc_pdf_generator_visual_v3 import CMCProposalGeneratorV3
import io
import os
import re
import json
import gzip
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

# Catálogo de códigos postales (SEPOMEX), cargado en memoria una sola vez.
# Fuente: https://github.com/IcaliaLabs/sepomex (datos oficiales).
# Se usa un dataset local en lugar de un API externo porque
# sepomex.icalialabs.com resultó no ser confiable en producción.
POSTAL_CODES = {}
_postal_codes_path = os.path.join(os.path.dirname(__file__), 'data', 'postal_codes.json.gz')
try:
    with gzip.open(_postal_codes_path, 'rt', encoding='utf-8') as f:
        POSTAL_CODES = json.load(f)
    logger.info(f"Catálogo de códigos postales cargado: {len(POSTAL_CODES)} CPs")
except Exception as e:
    logger.error(f"No se pudo cargar el catálogo de códigos postales: {e}")

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

@app.route('/api/postal-code/<cp>', methods=['GET'])
def get_postal_code_info(cp):
    """
    Devuelve Colonia(s)/Municipio/Estado a partir de un código postal
    mexicano, usando el catálogo local (SEPOMEX) cargado en memoria.

    Respuesta:
    {
        "found": true,
        "zip_code": "01000",
        "state": "Ciudad de México",
        "municipality": "Álvaro Obregón",
        "neighborhoods": ["San Ángel", "San Ángel Inn", ...]
    }
    """
    cp = (cp or '').strip()

    if not re.fullmatch(r'\d{5}', cp):
        return jsonify({'found': False, 'error': 'invalid_format', 'message': 'El código postal debe tener 5 dígitos'}), 400

    info = POSTAL_CODES.get(cp)

    if not info:
        return jsonify({'found': False, 'zip_code': cp, 'message': 'Código postal no encontrado'}), 200

    return jsonify({
        'found': True,
        'zip_code': cp,
        'state': info.get('state', ''),
        'municipality': info.get('municipality', ''),
        'neighborhoods': info.get('neighborhoods', [])
    }), 200

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
        services_summary = [
            {'name': s.get('name'), 'coordinates': s.get('coordinates', '')}
            for s in data.get('services', [])
        ]
        logger.info(
            "Proposal request | company=%s | contact=%s | phone=%s | whatsapp=%s | "
            "email=%s | business=%s | fiscal_address=%s | site_address=%s | "
            "fiscal_address_structured=%s | site_address_structured=%s | services=%s",
            client.get('company'),
            client.get('contact'),
            client.get('phone'),
            client.get('whatsapp'),
            client.get('email'),
            client.get('business'),
            client.get('fiscal_address'),
            client.get('site_address'),
            client.get('fiscal_address_structured'),
            client.get('site_address_structured'),
            services_summary
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


@app.route('/api/odoo/login', methods=['POST'])
def odoo_login():
    """Verifica ejecutivo con email+contraseña. Usa API Key del admin para operaciones."""
    try:
        import xmlrpc.client
        data      = request.get_json()
        email     = data.get('email', '').strip()
        password  = data.get('password', '').strip()

        odoo_url   = os.environ.get('ODOO_URL', 'https://cmc-network.odoo.com')
        admin_key  = os.environ.get('ODOO_API_KEY', '')
        admin_user = os.environ.get('ODOO_USER', 'ghernandez@cmcnetwork.mx')
        found_db   = os.environ.get('ODOO_DB_INTERNAL', '')

        common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')

        # Detectar DB interna usando admin key
        if not found_db:
            for candidate in ['', 'cmc-network', 'cmc_network']:
                try:
                    r = common.authenticate(candidate, admin_user, admin_key, {})
                    if r:
                        found_db = candidate
                        logger.info(f"DB interna: '{found_db}'")
                        break
                except:
                    pass

        # Verificar credenciales del ejecutivo
        exec_uid = common.authenticate(found_db, email, password, {})
        if not exec_uid:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        # Obtener nombre usando admin key
        admin_uid = common.authenticate(found_db, admin_user, admin_key, {})
        models    = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
        user_data = models.execute_kw(found_db, admin_uid, admin_key, 'res.users', 'read',
            [[exec_uid]], {'fields': ['name', 'login']})
        user = user_data[0] if user_data else {}

        logger.info(f"Login OK: {email} (uid={exec_uid})")
        return jsonify({
            'success': True,
            'uid':   exec_uid,
            'db':    found_db,
            'name':  user.get('name', email),
            'email': email,
        })

    except Exception as e:
        logger.error(f"Odoo login error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500



@app.route('/api/odoo/sync', methods=['POST'])
def odoo_sync():
    """Crea contacto y oportunidad en Odoo usando XML-RPC con API Key."""
    try:
        import xmlrpc.client
        data     = request.get_json()
        odoo_url   = os.environ.get('ODOO_URL', 'https://cmc-network.odoo.com')
        odoo_db    = data.get('odoo_db', os.environ.get('ODOO_DB_INTERNAL', ''))
        admin_key  = os.environ.get('ODOO_API_KEY', '')
        admin_user = os.environ.get('ODOO_USER', 'ghernandez@cmcnetwork.mx')
        exec_uid   = data.get('odoo_uid')

        common    = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
        admin_uid = common.authenticate(odoo_db, admin_user, admin_key, {})
        if not admin_uid:
            return jsonify({'error': 'Error de configuración del servidor'}), 500

        api_key = admin_key
        uid     = admin_uid

        models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')

        # Verificar acceso
        if not uid:
            common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
            uid = common.authenticate(odoo_db, email, api_key, {})
        if not uid:
            return jsonify({'error': 'No autenticado'}), 401

        uid = int(uid)
        client   = data.get('client', {})
        services = data.get('services', [])

        company_name = client.get('company', '')
        contact_name = client.get('contact', '')
        phone        = client.get('whatsapp', '')
        email_client = client.get('email', '')

        # 1. Buscar o crear empresa
        existing = models.execute_kw(odoo_db, uid, api_key, 'res.partner', 'search',
            [[['name', '=', company_name]]])
        partner_vals = {
            'name': company_name, 'is_company': True,
            'phone': phone, 'mobile': phone,
            'comment': f'Giro: {client.get("sector", "")}',
        }
        if existing:
            models.execute_kw(odoo_db, uid, api_key, 'res.partner', 'write', [existing, partner_vals])
            partner_id = existing[0]
            partner_action = 'actualizado'
        else:
            partner_id = models.execute_kw(odoo_db, uid, api_key, 'res.partner', 'create', [partner_vals])
            partner_action = 'creado'

        # 2. Contacto persona
        contact_ex = models.execute_kw(odoo_db, uid, api_key, 'res.partner', 'search',
            [[['name', '=', contact_name], ['parent_id', '=', partner_id]]])
        if not contact_ex:
            models.execute_kw(odoo_db, uid, api_key, 'res.partner', 'create', [{
                'name': contact_name, 'parent_id': partner_id,
                'type': 'contact', 'mobile': phone, 'email': email_client,
            }])

        # 3. Oportunidad CRM
        desc = '\n'.join([
            f"• {s.get('name','')}: {s.get('conditions',{}).get('monthly_rent','—')}/mes "
            f"({s.get('conditions',{}).get('term','—')})"
            for s in services
        ])
        total = sum(
            float(''.join(c for c in str(s.get('conditions',{}).get('monthly_rent','0'))
                if c.isdigit() or c == '.') or '0')
            for s in services
        )
        stages = models.execute_kw(odoo_db, uid, api_key, 'crm.stage', 'search_read',
            [[]], {'fields': ['id'], 'limit': 1, 'order': 'sequence asc'})
        stage_id = stages[0]['id'] if stages else False

        lead_vals = {
            'name': f"Propuesta {company_name} — {', '.join(s.get('name','') for s in services)}",
            'partner_id': partner_id, 'contact_name': contact_name,
            'phone': phone, 'email_from': email_client,
            'description': desc, 'expected_revenue': total,
            'user_id': exec_uid or admin_uid,
        }
        if stage_id:
            lead_vals['stage_id'] = stage_id

        lead_id = models.execute_kw(odoo_db, uid, api_key, 'crm.lead', 'create', [lead_vals])
        logger.info(f"Odoo sync OK: partner={partner_id}, lead={lead_id}")

        return jsonify({
            'success': True,
            'partner_id': partner_id,
            'lead_id': lead_id,
            'message': f'Contacto {partner_action} y oportunidad #{lead_id} creada en Odoo'
        })

    except Exception as e:
        logger.error(f"Odoo sync error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

        odoo_url    = os.environ.get('ODOO_URL', 'https://cmc-network.odoo.com')
        session_id  = data.get('odoo_session_id', '')
        client      = data.get('client', {})
        services    = data.get('services', [])

        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'session_id={session_id}' if session_id else '',
        }

        def odoo_call(model, method, args=None, kwargs=None):
            r = req.post(f'{odoo_url}/web/dataset/call_kw', headers=headers, json={
                'jsonrpc': '2.0', 'method': 'call',
                'params': {
                    'model': model, 'method': method,
                    'args': args or [], 'kwargs': kwargs or {}
                }
            }, timeout=15)
            result = r.json()
            if result.get('error'):
                raise Exception(result['error'].get('data', {}).get('message', str(result['error'])))
            return result.get('result')

        company_name = client.get('company', '')
        contact_name = client.get('contact', '')
        phone        = client.get('whatsapp', '')
        email        = client.get('email', '')

        logger.info(f"Odoo sync: company={company_name}, contact={contact_name}")

        # 1. Buscar o crear empresa
        existing = odoo_call('res.partner', 'search', [[['name', '=', company_name]]], {'limit': 1})
        partner_vals = {
            'name': company_name, 'is_company': True,
            'phone': phone, 'mobile': phone,
            'comment': f'Giro: {client.get("sector", "")}',
        }
        if existing:
            odoo_call('res.partner', 'write', [[existing[0]], partner_vals])
            partner_id = existing[0]
            partner_action = 'actualizado'
        else:
            partner_id = odoo_call('res.partner', 'create', [partner_vals])
            partner_action = 'creado'

        # 2. Crear contacto persona
        contact_existing = odoo_call('res.partner', 'search',
            [[['name', '=', contact_name], ['parent_id', '=', partner_id]]], {'limit': 1})
        if not contact_existing:
            odoo_call('res.partner', 'create', [{
                'name': contact_name, 'parent_id': partner_id,
                'type': 'contact', 'mobile': phone, 'email': email,
            }])

        # 3. Crear oportunidad
        desc = '\n'.join([
            f"• {s.get('name','')}: {s.get('conditions',{}).get('monthly_rent','—')}/mes ({s.get('conditions',{}).get('term','—')})"
            for s in services
        ])
        total = sum(
            float(''.join(c for c in str(s.get('conditions',{}).get('monthly_rent','0')) if c.isdigit() or c == '.') or '0')
            for s in services
        )

        stages = odoo_call('crm.stage', 'search_read', [[]], {'fields': ['id'], 'limit': 1, 'order': 'sequence asc'})
        stage_id = stages[0]['id'] if stages else False

        lead_vals = {
            'name': f"Propuesta {company_name} — {', '.join(s.get('name','') for s in services)}",
            'partner_id': partner_id, 'contact_name': contact_name,
            'phone': phone, 'email_from': email,
            'description': desc, 'expected_revenue': total,
        }
        if stage_id:
            lead_vals['stage_id'] = stage_id

        lead_id = odoo_call('crm.lead', 'create', [lead_vals])
        logger.info(f"Odoo sync OK: partner_id={partner_id}, lead_id={lead_id}")

        return jsonify({
            'success': True,
            'partner_id': partner_id,
            'partner_action': partner_action,
            'lead_id': lead_id,
            'message': f'Contacto {partner_action} y oportunidad #{lead_id} creada en Odoo'
        })

    except Exception as e:
        logger.error(f"Odoo sync error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'detail': repr(e)}), 500


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
    # Escuchar en 0.0.0.0 y puerto desde variable de entorno (Railway)
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
