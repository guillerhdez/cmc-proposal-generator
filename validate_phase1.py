#!/usr/bin/env python3
"""
Validación Completa Fase 1 - CMC Proposal Generator
Verifica todos los componentes del proyecto antes de deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class Phase1Validator:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def log_pass(self, message):
        print(f"✓ {message}")
        self.results['passed'].append(message)
    
    def log_fail(self, message):
        print(f"✗ {message}")
        self.results['failed'].append(message)
    
    def log_warn(self, message):
        print(f"⚠ {message}")
        self.results['warnings'].append(message)
    
    # ========== VALIDACIONES ==========
    
    def check_file_structure(self):
        """Verifica que todos los archivos necesarios existan"""
        print("\n📁 ESTRUCTURA DE ARCHIVOS")
        print("-" * 50)
        
        required_files = {
            'cmc_flask_server.py': 'Servidor Flask',
            'cmc_pdf_generator_visual_v3.py': 'Generador PDF',
            'cmc-cotizador.html': 'Frontend HTML',
            'requirements.txt': 'Dependencias',
            'runtime.txt': 'Versión Python',
            'Dockerfile': 'Configuración Docker',
            'railway.json': 'Configuración Railway',
            'Procfile': 'Configuración Railway/Heroku'
        }
        
        for filename, description in required_files.items():
            filepath = os.path.join(self.project_root, filename)
            if os.path.exists(filepath):
                self.log_pass(f"{filename} - {description}")
            else:
                self.log_fail(f"{filename} FALTA - {description}")
        
        # Verifica imágenes
        print("\n🖼️  IMÁGENES NECESARIAS")
        print("-" * 50)
        
        images_dir = os.path.join(self.project_root, 'images')
        required_images = [
            '1.jpeg', '2.jpeg', '3.jpeg', '4.jpeg', '5.jpeg', '6.jpeg',
            '01-internet-dedicado.jpg', '02-internet-eventos.jpg',
            '03-internet-satelital.jpg', '04-conectividad-lte.jpg',
            '05-telefonia-ip.jpg', '06-ciberseguridad.jpg',
            '07-iot-cctv.jpg', 'cobertura.jpg', 'portada.jpg'
        ]
        
        if not os.path.exists(images_dir):
            self.log_fail(f"Directorio 'images/' no existe")
            return
        
        self.log_pass(f"Directorio 'images/' encontrado")
        
        for img in required_images:
            img_path = os.path.join(images_dir, img)
            if os.path.exists(img_path):
                self.log_pass(f"  → {img}")
            else:
                self.log_warn(f"  → {img} FALTA (puede ser fallback)")
    
    def check_python_syntax(self):
        """Verifica sintaxis Python"""
        print("\n🐍 SINTAXIS PYTHON")
        print("-" * 50)
        
        python_files = [
            'cmc_flask_server.py',
            'cmc_pdf_generator_visual_v3.py'
        ]
        
        for pyfile in python_files:
            filepath = os.path.join(self.project_root, pyfile)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    compile(f.read(), filepath, 'exec')
                self.log_pass(f"{pyfile} - Sintaxis correcta")
            except SyntaxError as e:
                self.log_fail(f"{pyfile} - Error de sintaxis: {e}")
    
    def check_dependencies(self):
        """Verifica que las dependencias estén instaladas"""
        print("\n📦 DEPENDENCIAS")
        print("-" * 50)
        
        required_packages = [
            ('flask', 'Flask'),
            ('flask_cors', 'Flask-CORS'),
            ('reportlab', 'ReportLab'),
            ('PyPDF2', 'PyPDF2'),
            ('requests', 'requests'),
            ('werkzeug', 'Werkzeug'),
            ('jinja2', 'Jinja2')
        ]
        
        for import_name, package_name in required_packages:
            try:
                __import__(import_name)
                self.log_pass(f"{package_name} instalado")
            except ImportError:
                self.log_fail(f"{package_name} NO instalado")
    
    def check_requirements_txt(self):
        """Verifica contenido de requirements.txt"""
        print("\n📋 REQUIREMENTS.TXT")
        print("-" * 50)
        
        req_file = os.path.join(self.project_root, 'requirements.txt')
        try:
            with open(req_file, 'r') as f:
                requirements = f.read().strip().split('\n')
                self.log_pass(f"requirements.txt contiene {len(requirements)} paquetes")
                for req in requirements:
                    if req.strip():
                        self.log_pass(f"  → {req}")
        except Exception as e:
            self.log_fail(f"Error leyendo requirements.txt: {e}")
    
    def check_flask_config(self):
        """Verifica configuración del servidor Flask"""
        print("\n🔧 CONFIGURACIÓN FLASK")
        print("-" * 50)
        
        flask_file = os.path.join(self.project_root, 'cmc_flask_server.py')
        with open(flask_file, 'r') as f:
            content = f.read()
        
        # Verificar CORS
        if 'CORS(app)' in content:
            self.log_pass("CORS habilitado")
        else:
            self.log_warn("CORS no explícitamente habilitado")
        
        # Verificar endpoints
        endpoints = [
            ('/health', 'Health check'),
            ('/api/executives', 'Ejecutivos'),
            ('/api/services', 'Servicios'),
            ('/generate-pdf', 'Generador PDF'),
            ('/', 'Página inicio')
        ]
        
        for endpoint, description in endpoints:
            if f"@app.route('{endpoint}'" in content or f'@app.route("{endpoint}"' in content:
                self.log_pass(f"Endpoint {endpoint} - {description}")
            else:
                self.log_fail(f"Endpoint {endpoint} NO encontrado - {description}")
        
        # Verificar manejo de PORT
        if "os.environ.get('PORT'" in content:
            self.log_pass("Lee PORT de variable de entorno")
        else:
            self.log_warn("No lee PORT de variable de entorno (necesario para Railway)")
        
        # Verificar host
        if "host='0.0.0.0'" in content:
            self.log_pass("Host configurado a 0.0.0.0")
        else:
            self.log_warn("Host NO configurado a 0.0.0.0")
    
    def check_pdf_generator(self):
        """Verifica configuración del generador PDF"""
        print("\n📄 GENERADOR PDF")
        print("-" * 50)
        
        pdf_file = os.path.join(self.project_root, 'cmc_pdf_generator_visual_v3.py')
        with open(pdf_file, 'r') as f:
            content = f.read()
        
        checks = [
            ('Canvas', 'from reportlab.pdfgen import canvas'),
            ('Platypus', 'from reportlab.platypus import'),
            ('PdfMerger', 'from PyPDF2 import PdfMerger'),
            ('Clase principal', 'class CMCProposalGeneratorV3'),
            ('Método generate', 'def generate(self, proposal_data)'),
            ('Método merge', 'def _merge_pdfs')
        ]
        
        for name, code in checks:
            if code in content:
                self.log_pass(f"{name} implementado")
            else:
                self.log_fail(f"{name} NO encontrado")
    
    def check_html_structure(self):
        """Verifica estructura del HTML"""
        print("\n🌐 ESTRUCTURA HTML")
        print("-" * 50)
        
        html_file = os.path.join(self.project_root, 'cmc-cotizador.html')
        with open(html_file, 'r') as f:
            content = f.read()
        
        checks = [
            ('Formulario ejecutivo', 'id="executive"'),
            ('Formulario cliente', 'clientCompany'),
            ('Gestión servicios', 'addService'),
            ('Generador PDF', "fetch('/generate-pdf'"),
            ('Descarga PDF', 'createObjectURL'),
            ('WhatsApp integration', 'shareViaWhatsApp'),
        ]
        
        for name, selector in checks:
            if selector in content:
                self.log_pass(f"{name} presente")
            else:
                self.log_fail(f"{name} FALTA")
    
    def check_docker_config(self):
        """Verifica Dockerfile"""
        print("\n🐳 DOCKER")
        print("-" * 50)
        
        dockerfile = os.path.join(self.project_root, 'Dockerfile')
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        checks = [
            ('Imagen Python 3.11', 'python:3.11'),
            ('pip install requirements', 'pip install'),
            ('Copia código', 'COPY'),
            ('CMD Flask', 'cmc_flask_server.py')
        ]
        
        for name, text in checks:
            if text in content:
                self.log_pass(f"{name}")
            else:
                self.log_warn(f"{name} NO encontrado")
    
    def check_railway_config(self):
        """Verifica railway.json"""
        print("\n🚂 RAILWAY.JSON")
        print("-" * 50)
        
        railway_file = os.path.join(self.project_root, 'railway.json')
        with open(railway_file, 'r') as f:
            content = f.read()
        
        if '"builder": "dockerfile"' in content:
            self.log_pass("Builder configurado (dockerfile)")
        else:
            self.log_warn("Builder NO especificado")
        
        if 'python cmc_flask_server.py' in content:
            self.log_pass("Start command configurado")
        else:
            self.log_fail("Start command NO configurado")
        
        if '"restartPolicyType": "always"' in content:
            self.log_pass("Restart policy configurada")
        else:
            self.log_warn("Restart policy NO configurada")
    
    def test_pdf_generation(self):
        """Test de generación de PDF"""
        print("\n🧪 TEST GENERACIÓN PDF")
        print("-" * 50)
        
        try:
            from cmc_pdf_generator_visual_v3 import CMCProposalGeneratorV3
            
            # Test data
            test_data = {
                'executive': {
                    'name': 'Daniel Flores',
                    'title': 'Senior Executive',
                    'email': 'test@cmcnetworkmx.com',
                    'phone': '55 1929 8160'
                },
                'client': {
                    'company': 'Empresa Test',
                    'contact': 'Juan Pérez',
                    'whatsapp': '5512345678',
                    'business': 'Tecnología'
                },
                'services': [
                    {
                        'name': 'Internet Dedicado',
                        'description': 'Conectividad dedicada',
                        'conditions': {
                            'term': '24 meses',
                            'monthly_rent': '$4,500',
                            'installation': '$2,800'
                        }
                    }
                ]
            }
            
            # Intentar generar
            images_dir = os.path.join(self.project_root, 'images')
            generator = CMCProposalGeneratorV3(images_dir=images_dir)
            pdf_bytes = generator.generate(test_data)
            
            if isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 1000:
                self.log_pass(f"PDF generado exitosamente ({len(pdf_bytes)} bytes)")
            else:
                self.log_fail(f"PDF generado pero tamaño sospechoso: {len(pdf_bytes)} bytes")
        
        except Exception as e:
            self.log_fail(f"Error generando PDF: {str(e)}")
    
    # ========== REPORTE ==========
    
    def generate_report(self):
        """Genera reporte final"""
        print("\n\n" + "="*60)
        print("RESUMEN FASE 1 - CMC PROPOSAL GENERATOR")
        print("="*60)
        
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"\n✓ PASADAS:  {passed}")
        print(f"✗ FALLIDAS: {failed}")
        print(f"⚠ ADVERTENCIAS: {warnings}")
        
        if failed == 0:
            print("\n✅ FASE 1 LISTA PARA DEPLOYMENT")
            return 0
        else:
            print(f"\n❌ EXISTEN {failed} PROBLEMAS A SOLUCIONAR")
            print("\nProblemas encontrados:")
            for i, issue in enumerate(self.results['failed'], 1):
                print(f"  {i}. {issue}")
            return 1
    
    def run_all_checks(self):
        """Ejecuta todas las validaciones"""
        print("\n" + "="*60)
        print("VALIDACIÓN FASE 1 - CMC PROPOSAL GENERATOR")
        print("="*60)
        
        self.check_file_structure()
        self.check_python_syntax()
        self.check_dependencies()
        self.check_requirements_txt()
        self.check_flask_config()
        self.check_pdf_generator()
        self.check_html_structure()
        self.check_docker_config()
        self.check_railway_config()
        self.test_pdf_generation()
        
        return self.generate_report()


if __name__ == '__main__':
    validator = Phase1Validator()
    exit_code = validator.run_all_checks()
    sys.exit(exit_code)
