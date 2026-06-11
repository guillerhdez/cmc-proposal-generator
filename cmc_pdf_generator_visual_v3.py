"""
CMC Network - Generador de PDF Visual V3 CORREGIDO
Usa ReportLab Canvas + Platypus:
- Páginas 1-4: Imágenes estáticas
- Páginas 5+: Imagen 5.jpeg + texto dinámico (Canvas)
- Última: Tabla resumen (Platypus)
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from PyPDF2 import PdfMerger
import io
import os
import tempfile

class CMCProposalGeneratorV3:
    """Generador: Canvas (imágenes + servicios) + Platypus (tabla)"""
    
    # Mapeo de servicios a imágenes extraídas de Canva
    SERVICE_IMAGES = {
        'Internet Dedicado': '01-internet-dedicado.jpg',
        'Internet para Eventos': '02-internet-eventos.jpg',
        'Internet Satelital': '03-internet-satelital.jpg',
        'Conectividad LTE': '04-conectividad-lte.jpg',
        'Telefonía IP': '05-telefonia-ip.jpg',
        'Telefonía IP / Cloud PBX': '05-telefonia-ip.jpg',
        'Ciberseguridad Integral': '06-ciberseguridad.jpg',
        'Soluciones IoT': '07-iot-cctv.jpg',
        'CCTV Cableado y redes de WIFI': '07-iot-cctv.jpg',
    }
    
    def __init__(self, images_dir=None):
        self.images_dir = images_dir or os.path.dirname(__file__)
        self.dark_blue = HexColor('#001F3D')
        self.cyan = HexColor('#00BCD4')
    
    def generate(self, proposal_data):
        """Genera PDF combinando Canvas + Platypus"""
        
        # Parte 1: Canvas (páginas 1-5+)
        canvas_pdf = self._generate_canvas_pdf(proposal_data)
        
        # Parte 2: Platypus (tabla resumen)
        platypus_pdf = self._generate_summary_pdf(proposal_data)
        
        # Combinar
        return self._merge_pdfs(canvas_pdf, platypus_pdf)
    
    def _generate_canvas_pdf(self, proposal_data):
        """Genera PDF con Canvas: imágenes + servicios"""
        
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        page_height = 11 * inch
        
        # Páginas 1-4: Imágenes estáticas
        for i, img_file in enumerate(['1.jpeg', '2.jpeg', '3.jpeg', '4.jpeg']):
            img_path = os.path.join(self.images_dir, img_file)
            if os.path.exists(img_path):
                c.drawImage(img_path, 0, page_height - 8.5*inch, width=8.5*inch, height=8.5*inch)
            if i < 3:  # No showPage en la última
                c.showPage()
        
        # Páginas 5+: Servicios
        services = proposal_data.get('services', [])
        for service in services:
            c.showPage()
            
            # Obtener imagen específica del servicio
            service_name = service.get('name', '')
            img_filename = self.SERVICE_IMAGES.get(service_name, '05-telefonia-ip.jpg')  # fallback
            img_path = os.path.join(self.images_dir, img_filename)
            
            if os.path.exists(img_path):
                c.drawImage(img_path, 0, page_height - 8.5*inch, width=8.5*inch, height=8.5*inch)
            
            self._draw_service_on_canvas(c, service)
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _draw_service_on_canvas(self, c, service):
        """Dibuja datos dinámicos sobre imagen 5.jpeg"""
        
        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(self.dark_blue)
        
        y_start = 2.5 * inch
        
        service_name = service.get('name', 'Servicio')
        conditions = service.get('conditions', {})
        
        c.drawString(0.7*inch, y_start, f"Servicio: {service_name}")
        c.setFont('Helvetica', 10)
        c.drawString(0.7*inch, y_start - 0.25*inch, f"Plazo: {conditions.get('term', '')}")
        c.drawString(0.7*inch, y_start - 0.5*inch, f"Renta: {conditions.get('monthly_rent', '')}")
        c.drawString(0.7*inch, y_start - 0.75*inch, f"Instalación: {conditions.get('installation', '')}")
    
    def _generate_summary_pdf(self, proposal_data):
        """Genera PDF con tabla resumen (Platypus)"""
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        services = proposal_data.get('services', [])
        
        # Encabezados
        data = [['SERVICIO', 'PLAZO', 'RENTA MENSUAL (MXN)', 'INSTALACIÓN']]
        
        total_monthly = 0
        total_installation = 0
        
        # Filas de servicios
        for service in services:
            conditions = service.get('conditions', {})
            
            service_name = service.get('name', '')
            term = conditions.get('term', '')
            rent_str = conditions.get('monthly_rent', '0')
            install_str = conditions.get('installation', '0')
            
            # Extraer números
            try:
                rent_num = float(rent_str.replace('$', '').replace(',', ''))
                total_monthly += rent_num
            except:
                rent_num = 0
            
            try:
                install_num = float(install_str.replace('$', '').replace(',', ''))
                total_installation += install_num
            except:
                install_num = 0
            
            data.append([
                service_name,
                term,
                f'${rent_num:,.0f}',
                f'${install_num:,.0f}'
            ])
        
        # TOTAL
        data.append([
            'TOTAL MENSUAL',
            '',
            f'${total_monthly:,.0f} MXN + IVA',
            f'${total_installation:,.0f}'
        ])
        
        # Tabla
        table = Table(data, colWidths=[2*inch, 1.3*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [white, HexColor('#F5F5F5')]),
            ('BACKGROUND', (0, -1), (-1, -1), self.dark_blue),
            ('TEXTCOLOR', (0, -1), (-1, -1), white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        doc.build([table])
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _merge_pdfs(self, pdf1_bytes, pdf2_bytes):
        """Combina dos PDFs"""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f1:
            f1.write(pdf1_bytes)
            f1_path = f1.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f2:
            f2.write(pdf2_bytes)
            f2_path = f2.name
        
        merger = PdfMerger()
        merger.append(f1_path)
        merger.append(f2_path)
        
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        
        # Limpiar
        os.unlink(f1_path)
        os.unlink(f2_path)
        
        output.seek(0)
        return output.getvalue()
