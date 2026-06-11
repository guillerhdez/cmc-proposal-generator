"""
CMC Network - Generador de PDF Visual V2
Dibuja imágenes base + texto dinámico directamente en Canvas (sin PIL)
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

class CMCProposalGeneratorVisualV2:
    """Generador que dibuja imagen + texto dinámico en Canvas"""
    
    def __init__(self, images_dir=None):
        self.images_dir = images_dir or os.path.dirname(__file__)
        
        # Tamaño de página (1456x840 píxeles = 728x420 puntos @ 72 DPI)
        self.page_width = 728
        self.page_height = 420
        
        # Registrar fuentes
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        except:
            pass
    
    def generate(self, proposal_data):
        """Genera PDF visual con Canvas"""
        
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(self.page_width, self.page_height))
        c.setFont('DejaVuSans', 10)
        
        # Lista de páginas (imagen + función para dibujar texto dinámico)
        pages = [
            ('1.jpeg', self._draw_portada),
            ('2.jpeg', None),  # Estática
            ('3.jpeg', None),  # Estática
            ('4.jpeg', None),  # Estática
        ]
        
        # Agregar páginas de servicios
        for service in proposal_data.get('services', []):
            pages.append(('5.jpeg', lambda c, data=service: self._draw_servicio(c, data)))
        
        # Agregar página de resumen
        pages.append(('6.jpeg', lambda c, data=proposal_data: self._draw_resumen(c, data)))
        
        # Dibujar todas las páginas
        for i, (image_file, draw_func) in enumerate(pages):
            if i > 0:
                c.showPage()
            
            image_path = os.path.join(self.images_dir, image_file)
            if os.path.exists(image_path):
                # Dibujar imagen de fondo
                c.drawImage(image_path, 0, 0, width=self.page_width, height=self.page_height)
                
                # Dibujar texto dinámico si existe función
                if draw_func and i > 0:  # Saltar portada por ahora
                    draw_func(c, proposal_data if 'draw_resumen' in str(draw_func) else None)
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _draw_portada(self, c, proposal_data):
        """Dibuja datos dinámicos en portada"""
        executive = proposal_data.get('executive', {})
        
        c.setFont('DejaVuSans-Bold', 12)
        c.setFillColor('white')
        
        # Posiciones en puntos (728x420)
        # Abajo a la izquierda
        y_start = 50
        
        c.drawString(50, y_start + 30, executive.get('name', 'Ejecutivo'))
        c.setFont('DejaVuSans', 10)
        c.setFillColor('cyan')
        c.drawString(50, y_start + 15, executive.get('title', 'Senior Executive'))
        c.setFillColor('white')
        c.drawString(50, y_start, executive.get('email', 'email@cmcnetwork.com'))
        c.drawString(50, y_start - 15, executive.get('phone', '+55 1234 5678'))
    
    def _draw_servicio(self, c, service):
        """Dibuja datos del servicio"""
        c.setFont('DejaVuSans-Bold', 14)
        c.setFillColor('black')
        
        conditions = service.get('conditions', {})
        
        # Abajo de la imagen
        y = 100
        c.drawString(50, y, service.get('name', 'Servicio'))
        c.setFont('DejaVuSans', 9)
        c.drawString(50, y - 20, f"Plazo: {conditions.get('term', '')}")
        c.drawString(50, y - 35, f"Renta: {conditions.get('monthly_rent', '')}")
        c.drawString(50, y - 50, f"Instalación: {conditions.get('installation', '')}")
    
    def _draw_resumen(self, c, proposal_data):
        """Dibuja tabla de resumen"""
        services = proposal_data.get('services', [])
        
        c.setFont('DejaVuSans', 8)
        c.setFillColor('black')
        
        # Encabezados
        y = 350
        c.drawString(50, y, "SERVICIO")
        c.drawString(250, y, "PLAZO")
        c.drawString(400, y, "RENTA")
        c.drawString(550, y, "INSTAL.")
        
        y -= 20
        
        # Filas de servicios
        total_monthly = 0
        total_installation = 0
        
        for service in services:
            conditions = service.get('conditions', {})
            
            # Extraer números
            try:
                rent = float(conditions.get('monthly_rent', '0').replace('$', '').replace(',', ''))
                total_monthly += rent
            except:
                rent = 0
            
            try:
                install = float(conditions.get('installation', '0').replace('$', '').replace(',', ''))
                total_installation += install
            except:
                install = 0
            
            name = service.get('name', '')[:20]
            term = conditions.get('term', '')
            
            c.drawString(50, y, name)
            c.drawString(250, y, term)
            c.drawString(400, y, f"${rent:,.0f}")
            c.drawString(550, y, f"${install:,.0f}")
            
            y -= 15
        
        # TOTAL
        y -= 10
        c.setFont('DejaVuSans-Bold', 10)
        c.setFillColor('white')
        c.drawString(50, y, "TOTAL MENSUAL")
        c.drawString(400, y, f"${total_monthly:,.0f} MXN")
        c.drawString(550, y, f"${total_installation:,.0f}")


def generate_visual_pdf(proposal_data, images_dir=None):
    """Wrapper para generar PDF visual desde Flask"""
    generator = CMCProposalGeneratorVisualV2(images_dir)
    return generator.generate(proposal_data)
