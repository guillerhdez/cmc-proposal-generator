#!/usr/bin/env python3
"""
Test de Integración Completa - Fase 1
Inicia el servidor y prueba todos los endpoints
"""

import time
import requests
import subprocess
import os
import signal
import json
from pathlib import Path

class IntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.server_process = None
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def log_pass(self, test_name, message=""):
        msg = f"✓ {test_name}" + (f": {message}" if message else "")
        print(msg)
        self.test_results['passed'].append(test_name)
    
    def log_fail(self, test_name, message=""):
        msg = f"✗ {test_name}" + (f": {message}" if message else "")
        print(msg)
        self.test_results['failed'].append((test_name, message))
    
    def log_warn(self, test_name, message=""):
        msg = f"⚠ {test_name}" + (f": {message}" if message else "")
        print(msg)
        self.test_results['warnings'].append((test_name, message))
    
    def start_server(self):
        """Inicia el servidor Flask"""
        print("\n🚀 Iniciando servidor Flask...")
        print("-" * 50)
        
        try:
            # Cambiar a directorio del proyecto
            os.chdir(self.project_root)
            
            # Iniciar servidor
            self.server_process = subprocess.Popen(
                ['python', 'cmc_flask_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar a que inicie
            time.sleep(3)
            
            # Verificar que está corriendo
            if self.server_process.poll() is None:
                self.log_pass("Servidor Flask iniciado", "PID=" + str(self.server_process.pid))
                return True
            else:
                stderr = self.server_process.stderr.read() if self.server_process.stderr else "Unknown"
                self.log_fail("Servidor Flask", f"Falló al iniciar: {stderr}")
                return False
        
        except Exception as e:
            self.log_fail("Servidor Flask", str(e))
            return False
    
    def stop_server(self):
        """Detiene el servidor Flask"""
        if self.server_process:
            print("\n⏹️  Deteniendo servidor...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✓ Servidor detenido")
    
    def test_health_endpoint(self):
        """Test: GET /health"""
        print("\n📊 TESTS DE ENDPOINTS")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['status', 'service', 'version', 'environment']
                missing = [f for f in required_fields if f not in data]
                
                if not missing:
                    self.log_pass(
                        "GET /health",
                        f"status={data['status']}, version={data['version']}"
                    )
                    return True
                else:
                    self.log_fail("GET /health", f"Campos faltantes: {missing}")
                    return False
            else:
                self.log_fail("GET /health", f"Status {response.status_code}")
                return False
        
        except Exception as e:
            self.log_fail("GET /health", str(e))
            return False
    
    def test_executives_endpoint(self):
        """Test: GET /api/executives"""
        try:
            response = requests.get(f"{self.base_url}/api/executives", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and len(data) >= 3:
                    executive_names = [v.get('name', '') for v in data.values()]
                    self.log_pass(
                        "GET /api/executives",
                        f"{len(data)} ejecutivos: {', '.join(executive_names[:2])}..."
                    )
                    return True
                else:
                    self.log_fail("GET /api/executives", f"Esperaba 3+ ejecutivos, recibió {len(data)}")
                    return False
            else:
                self.log_fail("GET /api/executives", f"Status {response.status_code}")
                return False
        
        except Exception as e:
            self.log_fail("GET /api/executives", str(e))
            return False
    
    def test_services_endpoint(self):
        """Test: GET /api/services"""
        try:
            response = requests.get(f"{self.base_url}/api/services", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) >= 7:
                    service_names = [s.get('name', '') for s in data[:3]]
                    self.log_pass(
                        "GET /api/services",
                        f"{len(data)} servicios: {', '.join(service_names)}..."
                    )
                    return True
                else:
                    self.log_fail("GET /api/services", f"Esperaba 7+ servicios, recibió {len(data)}")
                    return False
            else:
                self.log_fail("GET /api/services", f"Status {response.status_code}")
                return False
        
        except Exception as e:
            self.log_fail("GET /api/services", str(e))
            return False
    
    def test_pdf_generation(self):
        """Test: POST /generate-pdf"""
        print("\n📄 TEST GENERACIÓN PDF")
        print("-" * 50)
        
        test_data = {
            'executive': {
                'name': 'Daniel Flores',
                'title': 'Senior Executive',
                'email': 'dflores@cmcnetworkmx.com',
                'phone': '55 1929 8160'
            },
            'client': {
                'company': 'Empresa Test ABC',
                'contact': 'Juan Pérez García',
                'whatsapp': '5512345678',
                'business': 'Tecnología e Innovación'
            },
            'services': [
                {
                    'name': 'Internet Dedicado',
                    'description': 'Solución de conectividad dedicada',
                    'conditions': {
                        'term': '24 meses',
                        'monthly_rent': '$4,500',
                        'installation': '$2,800'
                    }
                },
                {
                    'name': 'Telefonía IP / Cloud PBX',
                    'description': 'Sistema de comunicaciones en la nube',
                    'conditions': {
                        'term': '12 meses',
                        'monthly_rent': '$1,550',
                        'installation': '$0'
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/generate-pdf",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                pdf_size = len(response.content)
                
                # Validar que es PDF válido
                is_pdf = response.content[:4] == b'%PDF'
                
                if is_pdf and pdf_size > 50000:
                    self.log_pass(
                        "POST /generate-pdf",
                        f"PDF generado: {pdf_size/1024:.0f} KB"
                    )
                    
                    # Guardar PDF para inspección manual
                    pdf_path = os.path.join(self.project_root, 'test_output.pdf')
                    with open(pdf_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.log_pass("PDF guardado", f"→ {pdf_path}")
                    return True
                else:
                    self.log_fail(
                        "POST /generate-pdf",
                        f"PDF inválido o muy pequeño ({pdf_size} bytes)"
                    )
                    return False
            else:
                error_msg = response.text if response.status_code != 500 else "Error interno del servidor"
                self.log_fail("POST /generate-pdf", f"Status {response.status_code}: {error_msg[:100]}")
                return False
        
        except Exception as e:
            self.log_fail("POST /generate-pdf", str(e))
            return False
    
    def test_html_serve(self):
        """Test: GET /cmc-cotizador.html"""
        try:
            response = requests.get(f"{self.base_url}/cmc-cotizador.html", timeout=5)
            
            if response.status_code == 200:
                html = response.text
                
                required_elements = [
                    ('Formulario ejecutivo', 'id="executive"'),
                    ('Botón generar PDF', 'generateAndDownloadPDF'),
                    ('WhatsApp', 'shareViaWhatsApp'),
                    ('Servicios', 'addService')
                ]
                
                all_present = all(element in html for _, element in required_elements)
                
                if all_present:
                    self.log_pass("GET /cmc-cotizador.html", "HTML completo y válido")
                    return True
                else:
                    missing = [name for name, element in required_elements if element not in html]
                    self.log_warn("GET /cmc-cotizador.html", f"Elementos faltantes: {', '.join(missing)}")
                    return False
            else:
                self.log_fail("GET /cmc-cotizador.html", f"Status {response.status_code}")
                return False
        
        except Exception as e:
            self.log_fail("GET /cmc-cotizador.html", str(e))
            return False
    
    def test_cors(self):
        """Test: CORS headers"""
        try:
            response = requests.options(
                f"{self.base_url}/api/services",
                headers={'Origin': 'http://example.com'},
                timeout=5
            )
            
            if 'Access-Control-Allow-Origin' in response.headers:
                self.log_pass("CORS", "Headers configurados correctamente")
                return True
            else:
                self.log_warn("CORS", "Headers CORS no encontrados")
                return False
        
        except Exception as e:
            self.log_fail("CORS", str(e))
            return False
    
    def generate_report(self):
        """Genera reporte final"""
        passed = len(self.test_results['passed'])
        failed = len(self.test_results['failed'])
        warnings = len(self.test_results['warnings'])
        
        print("\n\n" + "="*60)
        print("REPORTE FINAL - TEST DE INTEGRACIÓN")
        print("="*60)
        
        print(f"\n✓ PASADAS:   {passed}")
        print(f"✗ FALLIDAS:  {failed}")
        print(f"⚠ ADVERTENCIAS: {warnings}")
        
        if failed == 0:
            print("\n✅ FASE 1 COMPLETADA EXITOSAMENTE")
            print("\n🎯 Status: LISTA PARA DEPLOYMENT")
            return 0
        else:
            print(f"\n❌ EXISTEN {failed} PROBLEMAS")
            for test, msg in self.test_results['failed']:
                print(f"  - {test}: {msg}")
            return 1
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("\n" + "="*60)
        print("TEST DE INTEGRACIÓN - FASE 1")
        print("="*60)
        
        # Iniciar servidor
        if not self.start_server():
            print("\n❌ No se pudo iniciar el servidor")
            return 1
        
        try:
            # Ejecutar tests
            self.test_health_endpoint()
            self.test_executives_endpoint()
            self.test_services_endpoint()
            self.test_pdf_generation()
            self.test_html_serve()
            self.test_cors()
            
            return self.generate_report()
        
        finally:
            # Detener servidor
            self.stop_server()


if __name__ == '__main__':
    import sys
    tester = IntegrationTest()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
