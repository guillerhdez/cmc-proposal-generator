"""
CMC Network - Generador de PDF Profesional
Replica del diseño PROPUESTA_FORMAL_CMC_3.pdf
Versión 3.0 - Con estructura profesional y datos dinámicos
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
import io
from datetime import datetime

class CMCProposalGeneratorProfessional:
    """Generador de propuestas profesionales con imágenes base"""
    
    def __init__(self):
        self.page_width, self.page_height = letter
        
        # Colores CMC
        self.dark_blue = HexColor('#001F3D')
        self.cyan = HexColor('#00BCD4')
        self.white = HexColor('#FFFFFF')
        
    def generate(self, proposal_data):
        """
        Genera PDF profesional
        
        Args:
            proposal_data: {
                'executive': {'name': '', 'title': '', 'email': '', 'phone': ''},
                'client': {'company': '', 'contact': '', 'whatsapp': '', 'industry': ''},
                'services': [
                    {
                        'name': '',
                        'description': '',
                        'conditions': {
                            'term': '',
                            'monthly_rent': '',
                            'installation': '',
                            'special_conditions': ''
                        }
                    }
                ]
            }
        """
        
        pdf_buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        story = []
        
        # ===== PÁGINA 1: PORTADA =====
        story.extend(self._create_cover_page(proposal_data))
        story.append(PageBreak())
        
        # ===== PÁGINA 2: ¿QUIÉNES SOMOS? =====
        story.extend(self._create_about_page())
        story.append(PageBreak())
        
        # ===== PÁGINA 3: COBERTURA =====
        story.extend(self._create_coverage_page())
        story.append(PageBreak())
        
        # ===== PÁGINA 4: PORTAFOLIO =====
        story.extend(self._create_portfolio_page())
        story.append(PageBreak())
        
        # ===== PÁGINAS 5+: SERVICIOS =====
        for i, service in enumerate(proposal_data.get('services', [])):
            story.extend(self._create_service_page(service, i+1))
            if i < len(proposal_data.get('services', [])) - 1:
                story.append(PageBreak())
        
        story.append(PageBreak())
        
        # ===== ÚLTIMA PÁGINA: RESUMEN ECONÓMICO =====
        story.extend(self._create_summary_page(proposal_data))
        
        # Compilar PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    def _create_cover_page(self, proposal_data):
        """Página de portada"""
        styles = getSampleStyleSheet()
        executive = proposal_data.get('executive', {})
        
        elements = []
        
        # Logo CMC (simulado con texto)
        logo_style = ParagraphStyle(
            'LogoStyle',
            fontSize=36,
            textColor=self.cyan,
            fontName='Helvetica-Bold',
            alignment=1
        )
        elements.append(Spacer(1, 1.5*inch))
        elements.append(Paragraph("CMC Network", logo_style))
        
        # Título
        title_style = ParagraphStyle(
            'TitleStyle',
            fontSize=24,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            alignment=1,
            spaceAfter=0.5*inch
        )
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("SOLUCIONES INTEGRALES<br/>EN TELECOMUNICACIONES", title_style))
        
        # Subtítulo
        elements.append(Spacer(1, 1*inch))
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            fontSize=11,
            textColor=self.dark_blue,
            fontName='Helvetica',
            alignment=0
        )
        
        exec_text = f"""
        <b>{executive.get('name', 'Ejecutivo')}</b><br/>
        {executive.get('title', 'Título')}<br/>
        <br/>
        {executive.get('email', 'email@cmcnetwork.com')}<br/>
        {executive.get('phone', '+55 1234 5678')}
        """
        
        elements.append(Paragraph(exec_text, subtitle_style))
        elements.append(Spacer(1, 2*inch))
        
        return elements
    
    def _create_about_page(self):
        """Página: ¿Quiénes somos?"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        title_style = ParagraphStyle(
            'SectionTitle',
            fontSize=20,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            spaceAfter=0.3*inch
        )
        elements.append(Paragraph("¿Quiénes somos?", title_style))
        
        # Contenido
        body_style = ParagraphStyle(
            'BodyText',
            fontSize=10,
            textColor=black,
            fontName='Helvetica',
            alignment=4,
            spaceAfter=0.2*inch
        )
        
        about_text = """
        Somos una empresa líder en telecomunicaciones, con más de 30 años en el medio, 
        concesionados por la IFT y cobertura nacional. Contamos con infraestructura propia 
        y un equipo de expertos en diseño, integración y operación de soluciones tecnológicas, 
        así como los mejores aliados.
        <br/><br/>
        Ofrecemos servicios a la medida para todo tipo de negocio, empresa o proyecto, 
        con enfoque en alta disponibilidad, confiabilidad e innovación.
        """
        
        elements.append(Paragraph(about_text, body_style))
        
        return elements
    
    def _create_coverage_page(self):
        """Página: Cobertura"""
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            fontSize=20,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            spaceAfter=0.3*inch
        )
        elements.append(Paragraph("Nuestra cobertura", title_style))
        
        body_style = ParagraphStyle(
            'BodyText',
            fontSize=10,
            textColor=black,
            fontName='Helvetica',
            spaceAfter=0.2*inch
        )
        
        coverage_text = """
        <b>Internet Dedicado:</b> Cobertura total (Fibra Óptica y Microondas)<br/>
        <b>Satelital o LTE:</b> Disponible en toda la república<br/>
        <br/>
        Verificar disponibilidad en tu zona: www.cmcnetworkmx.com
        """
        
        elements.append(Paragraph(coverage_text, body_style))
        
        return elements
    
    def _create_portfolio_page(self):
        """Página: Portafolio de Soluciones"""
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            fontSize=20,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            spaceAfter=0.3*inch
        )
        elements.append(Paragraph("Portafolio de Soluciones", title_style))
        
        body_style = ParagraphStyle(
            'BodyText',
            fontSize=10,
            textColor=black,
            fontName='Helvetica',
            spaceAfter=0.15*inch
        )
        
        services = [
            ("Internet Dedicado", "Cobertura por M.O y F.O"),
            ("Internet para Eventos", "Ideal para cubrir cualquier evento, servicio desde 1 día"),
            ("Internet Satelital", "Diseñado para zonas de difícil acceso, respaldos, obras, etc."),
            ("Conectividad LTE", "Ideal para proyectos básicos que requieren alta conectividad"),
            ("Telefonía IP", "Infraestructura propia con conmutador físico o en la nube"),
            ("Ciberseguridad Integral", "Expertos en soluciones Fortinet, WatchGuard y Sophos"),
            ("Soluciones IoT", "Soluciones específicas para gestión, automatización y monitoreo")
        ]
        
        for name, desc in services:
            text = f"<b>{name}</b><br/><font size=9>{desc}</font><br/>"
            elements.append(Paragraph(text, body_style))
        
        return elements
    
    def _create_service_page(self, service, number):
        """Página de servicio individual"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Título del servicio
        title_style = ParagraphStyle(
            'ServiceTitle',
            fontSize=16,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            spaceAfter=0.2*inch
        )
        elements.append(Paragraph(f"{service.get('name', 'Servicio')}", title_style))
        
        # Descripción
        desc_style = ParagraphStyle(
            'Description',
            fontSize=9,
            textColor=black,
            fontName='Helvetica',
            spaceAfter=0.3*inch
        )
        elements.append(Paragraph(service.get('description', ''), desc_style))
        
        # Tabla de condiciones
        conditions = service.get('conditions', {})
        
        table_data = [
            ['Concepto', 'Valor'],
            ['Plazo del contrato', conditions.get('term', '')],
            ['Renta mensual', conditions.get('monthly_rent', '')],
            ['Instalación / Equipo', conditions.get('installation', '')],
            ['Condiciones especiales', conditions.get('special_conditions', '')]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0F0F0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F8F8')])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_summary_page(self, proposal_data):
        """Página: Resumen Económico Consolidado"""
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            fontSize=16,
            textColor=self.dark_blue,
            fontName='Helvetica-Bold',
            spaceAfter=0.3*inch
        )
        elements.append(Paragraph("RESUMEN ECONÓMICO CONSOLIDADO", title_style))
        
        # Tabla de servicios
        services = proposal_data.get('services', [])
        
        table_data = [
            ['Servicio', 'Plazo', 'Renta Mensual (MXN + IVA)', 'Instalación']
        ]
        
        total_monthly = 0
        total_installation = 0
        
        for service in services:
            conditions = service.get('conditions', {})
            term = conditions.get('term', '')
            rent_str = conditions.get('monthly_rent', '$0')
            install_str = conditions.get('installation', '—')
            
            # Extraer valores numéricos
            try:
                rent_val = float(rent_str.replace('$', '').replace(',', ''))
                total_monthly += rent_val
            except:
                pass
            
            try:
                install_val = float(install_str.replace('$', '').replace(',', '')) if install_str != '—' else 0
                total_installation += install_val
            except:
                pass
            
            table_data.append([
                service.get('name', ''),
                term,
                rent_str,
                install_str
            ])
        
        # Fila total
        table_data.append([
            'TOTAL MENSUAL',
            '',
            f'${total_monthly:,.0f} MXN + IVA',
            f'${total_installation:,.0f}' if total_installation > 0 else '—'
        ])
        
        table = Table(table_data, colWidths=[1.8*inch, 1.2*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), self.cyan),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.dark_blue),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [white, HexColor('#F8F8F8')])
        ]))
        
        elements.append(table)
        
        # Nota de vigencia
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=8,
            textColor=HexColor('#666666'),
            fontName='Helvetica',
            alignment=0
        )
        elements.append(Paragraph(
            "Todos los precios son + IVA. Vigencia de esta propuesta: 30 días naturales.",
            footer_style
        ))
        
        return elements


# Función para uso desde Flask
def generate_professional_pdf(proposal_data):
    """Wrapper para generar PDF desde Flask"""
    generator = CMCProposalGeneratorProfessional()
    return generator.generate(proposal_data)
