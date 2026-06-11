"""
CMC Network - Generador de PDF Réplica Visual Exacta
Superpone texto dinámico sobre imágenes JPEG base
"""

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak, Spacer
from reportlab.lib.colors import HexColor
import io
import os
from datetime import datetime

class CMCProposalGeneratorVisual:
    """Generador que superpone texto dinámico sobre imágenes base"""
    
    def __init__(self, images_dir=None):
        self.images_dir = images_dir or os.path.dirname(__file__)
        self.page_width = 1456
        self.page_height = 840
        
        # Colores CMC
        self.dark_blue = (0, 31, 61)  # #001F3D
        self.cyan = (0, 188, 212)      # #00BCD4
        self.white = (255, 255, 255)
        self.text_gray = (85, 85, 85)
        
    def generate(self, proposal_data):
        """Genera PDF visual exacto"""
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            topMargin=0,
            bottomMargin=0,
            leftMargin=0,
            rightMargin=0
        )
        
        story = []
        
        # ===== PÁGINA 1: PORTADA (con datos dinámicos) =====
        portada = self._create_portada(proposal_data)
        if portada:
            story.append(RLImage(portada, width=7.5*inch, height=4.35*inch))
            story.append(PageBreak())
        
        # ===== PÁGINA 2: ¿QUIÉNES SOMOS? (estática) =====
        try:
            quienes_path = self._get_image_path('2.jpeg')
            if os.path.exists(quienes_path):
                story.append(RLImage(quienes_path, width=7.5*inch, height=4.35*inch))
                story.append(PageBreak())
        except:
            pass
        
        # ===== PÁGINA 3: COBERTURA (estática) =====
        try:
            cobertura_path = self._get_image_path('3.jpeg')
            if os.path.exists(cobertura_path):
                story.append(RLImage(cobertura_path, width=7.5*inch, height=4.35*inch))
                story.append(PageBreak())
        except:
            pass
        
        # ===== PÁGINA 4: PORTAFOLIO (estática) =====
        try:
            portafolio_path = self._get_image_path('4.jpeg')
            if os.path.exists(portafolio_path):
                story.append(RLImage(portafolio_path, width=7.5*inch, height=4.35*inch))
                story.append(PageBreak())
        except:
            pass
        
        # ===== PÁGINAS 5+: SERVICIOS (con datos dinámicos) =====
        for i, service in enumerate(proposal_data.get('services', [])):
            servicio_img = self._create_servicio_page(service)
            if servicio_img:
                story.append(RLImage(servicio_img, width=7.5*inch, height=4.35*inch))
                if i < len(proposal_data.get('services', [])) - 1:
                    story.append(PageBreak())
        
        story.append(PageBreak())
        
        # ===== ÚLTIMA PÁGINA: RESUMEN (con datos dinámicos) =====
        resumen_img = self._create_resumen_page(proposal_data)
        if resumen_img:
            story.append(RLImage(resumen_img, width=7.5*inch, height=4.35*inch))
        
        # Compilar PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    def _get_image_path(self, filename):
        """Obtiene ruta de imagen"""
        return os.path.join(self.images_dir, filename)
    
    def _create_portada(self, proposal_data):
        """Crea portada con datos dinámicos superpuestos"""
        try:
            # Cargar imagen base
            base_path = self._get_image_path('1.jpeg')
            if not os.path.exists(base_path):
                return None
            
            img = Image.open(base_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Intentar cargar fuentes
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            executive = proposal_data.get('executive', {})
            client = proposal_data.get('client', {})
            
            # Superponer datos del ejecutivo (esquina inferior izquierda)
            x_pos = 100
            y_start = 680
            
            text_lines = [
                (executive.get('name', 'Ejecutivo'), font_text, self.white),
                (executive.get('title', 'Senior Executive'), font_small, self.cyan),
                (executive.get('email', 'email@cmcnetwork.com'), font_small, self.white),
                (executive.get('phone', '+55 1234 5678'), font_small, self.white)
            ]
            
            for i, (line, font, color) in enumerate(text_lines):
                y_pos = y_start + (i * 35)
                draw.text((x_pos, y_pos), line, fill=color, font=font)
            
            # Guardar imagen modificada en buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Error creando portada: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_servicio_page(self, service):
        """Crea página de servicio con datos dinámicos superpuestos"""
        try:
            # Cargar imagen base (plantilla de servicio)
            base_path = self._get_image_path('5.jpeg')
            if not os.path.exists(base_path):
                return None
            
            img = Image.open(base_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Intentar cargar fuentes
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            service_name = service.get('name', 'Servicio')
            conditions = service.get('conditions', {})
            
            # Superponer nombre del servicio (abajo de la imagen)
            # En área blanca/clara para mejor legibilidad
            draw.text((100, 700), service_name, fill=self.dark_blue, font=font_title)
            
            # Tabla de condiciones (abajo del servicio)
            y_table = 750
            
            # Plazo
            draw.text((100, y_table), "Plazo: " + conditions.get('term', '12 meses'), 
                     fill=self.dark_blue, font=font_small)
            
            # Renta
            draw.text((100, y_table + 30), "Renta: " + conditions.get('monthly_rent', '$0'), 
                     fill=self.dark_blue, font=font_small)
            
            # Instalación
            draw.text((100, y_table + 60), "Instalación: " + conditions.get('installation', '$0'), 
                     fill=self.dark_blue, font=font_small)
            
            # Guardar imagen modificada
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Error creando página servicio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_resumen_page(self, proposal_data):
        """Crea página de resumen con datos dinámicos superpuestos"""
        try:
            # Cargar imagen base (plantilla de resumen)
            base_path = self._get_image_path('6.jpeg')
            if not os.path.exists(base_path):
                return None
            
            img = Image.open(base_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Intentar cargar fuentes
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            services = proposal_data.get('services', [])
            total_monthly = 0
            total_installation = 0
            
            # Calcular totales
            for service in services:
                conditions = service.get('conditions', {})
                try:
                    rent = float(conditions.get('monthly_rent', '0').replace('$', '').replace(',', ''))
                    total_monthly += rent
                except:
                    pass
                
                try:
                    install = float(conditions.get('installation', '0').replace('$', '').replace(',', ''))
                    total_installation += install
                except:
                    pass
            
            # Superponer tabla de servicios (en área blanca/clara)
            y = 200
            
            # Encabezado de tabla
            draw.text((100, y), "SERVICIO", fill=self.dark_blue, font=font_text)
            draw.text((600, y), "PLAZO", fill=self.dark_blue, font=font_text)
            draw.text((900, y), "RENTA", fill=self.dark_blue, font=font_text)
            draw.text((1150, y), "INSTALACIÓN", fill=self.dark_blue, font=font_text)
            
            y += 40
            
            # Filas de servicios
            for service in services:
                conditions = service.get('conditions', {})
                
                draw.text((100, y), service.get('name', '')[:25], fill=self.text_gray, font=font_small)
                draw.text((600, y), conditions.get('term', ''), fill=self.text_gray, font=font_small)
                draw.text((900, y), conditions.get('monthly_rent', ''), fill=self.text_gray, font=font_small)
                draw.text((1150, y), conditions.get('installation', ''), fill=self.text_gray, font=font_small)
                
                y += 35
            
            # Fila de TOTAL
            y += 20
            draw.text((100, y), "TOTAL MENSUAL", fill=self.white, font=font_title)
            draw.text((900, y), f"${total_monthly:,.0f} MXN", fill=self.white, font=font_text)
            draw.text((1150, y), f"${total_installation:,.0f}", fill=self.white, font=font_text)
            
            # Guardar imagen modificada
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Error creando página resumen: {e}")
            import traceback
            traceback.print_exc()
            return None


def generate_visual_pdf(proposal_data, images_dir=None):
    """Wrapper para generar PDF visual desde Flask"""
    generator = CMCProposalGeneratorVisual(images_dir)
    return generator.generate(proposal_data)
