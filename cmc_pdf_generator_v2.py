#!/usr/bin/env python3
"""
CMC Network - Generador de Propuestas PDF v2
Diseño profesional similar a Canva (ReportLab)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Frame, PageTemplate, BaseDocTemplate
)
from reportlab.pdfgen import canvas
from datetime import datetime
import io

# ============================================================================
# CONFIGURACIÓN CMC
# ============================================================================

COLORS = {
    'dark_blue': HexColor('#001F3D'),
    'cyan': HexColor('#00BCD4'),
    'light_blue': HexColor('#004D7A'),
    'white': white,
    'light_gray': HexColor('#F8F9FA'),
    'dark_gray': HexColor('#333333'),
    'text_gray': HexColor('#555555'),
}

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.5 * inch

# ============================================================================
# PLANTILLAS DE PÁGINA CON CANVAS
# ============================================================================

class CMCPageTemplate(PageTemplate):
    """Plantilla personalizada para cada tipo de página"""
    
    def __init__(self, page_type='normal', **kwargs):
        self.page_type = page_type
        super().__init__(**kwargs)
    
    def beforeDrawPage(self, canvas, doc):
        """Se ejecuta antes de dibujar la página"""
        if self.page_type == 'cover':
            self._draw_cover_background(canvas)
        elif self.page_type == 'normal':
            self._draw_normal_background(canvas)
        elif self.page_type == 'summary':
            self._draw_summary_background(canvas)
    
    def _draw_cover_background(self, canvas):
        """Fondo para portada"""
        # Fondo oscuro
        canvas.setFillColor(COLORS['dark_blue'])
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Línea decorativa arriba
        canvas.setStrokeColor(COLORS['cyan'])
        canvas.setLineWidth(3)
        canvas.line(0, PAGE_HEIGHT - 0.3*inch, PAGE_WIDTH, PAGE_HEIGHT - 0.3*inch)
    
    def _draw_normal_background(self, canvas):
        """Fondo para páginas normales"""
        # Fondo blanco
        canvas.setFillColor(COLORS['white'])
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Línea azul lateral izquierda
        canvas.setFillColor(COLORS['dark_blue'])
        canvas.rect(0, 0, 5*mm, PAGE_HEIGHT, fill=1, stroke=0)
    
    def _draw_summary_background(self, canvas):
        """Fondo para página de resumen"""
        # Degradado visual (simulado)
        canvas.setFillColor(COLORS['light_gray'])
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Línea superior
        canvas.setFillColor(COLORS['dark_blue'])
        canvas.rect(0, PAGE_HEIGHT - 0.2*inch, PAGE_WIDTH, 0.2*inch, fill=1, stroke=0)

# ============================================================================
# GENERADOR CON DISEÑO MEJORADO
# ============================================================================

class CMCProposalGeneratorV2:
    """Generador de propuestas con diseño profesional"""
    
    def __init__(self, filename=None):
        self.filename = filename
        self.story = []
        self.styles = self._create_styles()
        self.doc = None
    
    def _create_styles(self):
        """Estilos personalizados para CMC"""
        styles = getSampleStyleSheet()
        
        # TÍTULOS Y HEADINGS
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Normal'],
            fontSize=52,
            textColor=COLORS['white'],
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=60
        ))
        
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=styles['Normal'],
            fontSize=28,
            textColor=COLORS['cyan'],
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=35
        ))
        
        styles.add(ParagraphStyle(
            name='PageTitle',
            parent=styles['Normal'],
            fontSize=36,
            textColor=COLORS['dark_blue'],
            spaceAfter=24,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=COLORS['cyan'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # CUERPO DE TEXTO
        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontSize=11,
            textColor=COLORS['dark_gray'],
            alignment=TA_JUSTIFY,
            spaceAfter=14,
            leading=15
        ))
        
        # INFORMACIÓN EJECUTIVO
        styles.add(ParagraphStyle(
            name='ExecName',
            parent=styles['Normal'],
            fontSize=14,
            textColor=COLORS['white'],
            fontName='Helvetica-Bold',
            spaceAfter=3
        ))
        
        styles.add(ParagraphStyle(
            name='ExecTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=COLORS['cyan'],
            fontName='Helvetica',
            spaceAfter=3
        ))
        
        styles.add(ParagraphStyle(
            name='ExecInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['text_gray'],
            fontName='Helvetica',
            spaceAfter=2
        ))
        
        # TABLAS
        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['white'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='TableValue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['dark_gray'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        return styles
    
    def _add_cover_page(self, executive):
        """Portada con datos del ejecutivo"""
        # Espaciador para centrar verticalmente
        self.story.append(Spacer(1, 1.5*inch))
        
        # Logo/Título principal
        self.story.append(Paragraph(
            "CMC Network",
            self.styles['CoverTitle']
        ))
        
        # Subtítulo
        self.story.append(Paragraph(
< truncated lines 220-290 >
            ],
            [
                Paragraph('Renta mensual', self.styles['TableValue']),
                Paragraph(conditions.get('monthly_rent', '—'), self.styles['TableValue'])
            ],
            [
                Paragraph('Instalación / Equipo', self.styles['TableValue']),
                Paragraph(conditions.get('installation', '—'), self.styles['TableValue'])
            ],
            [
                Paragraph('Condiciones especiales', self.styles['TableValue']),
                Paragraph(conditions.get('special_conditions', '—'), self.styles['TableValue'])
            ],
        ]
        
        table = Table(table_data, colWidths=[3.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['dark_blue']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Filas alternas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], COLORS['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 1, COLORS['dark_blue']),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
    
    def _add_summary_page(self, proposal_data):
        """Página final: Resumen económico"""
        self.story.append(Paragraph(
            "RESUMEN ECONÓMICO CONSOLIDADO",
            self.styles['PageTitle']
        ))
        
        services = proposal_data.get('services', [])
        
        # Construir tabla de resumen
        table_data = [
            [
                Paragraph('Servicio', self.styles['TableHeader']),
                Paragraph('Plazo', self.styles['TableHeader']),
                Paragraph('Renta Mensual<br/>(MXN + IVA)', self.styles['TableHeader']),
                Paragraph('Instalación', self.styles['TableHeader'])
            ]
        ]
        
        total_monthly = 0
        total_installation = 0
        
        for service in services:
            conditions = service.get('conditions', {})
            rent_str = conditions.get('monthly_rent', '0')
            install_str = conditions.get('installation', '0')
            
            # Extrae valores numéricos
            try:
                rent = float(rent_str.replace('$', '').replace(',', ''))
                total_monthly += rent
            except:
                rent = 0
            
            try:
                install = float(install_str.replace('$', '').replace(',', ''))
                total_installation += install
            except:
                install = 0
            
            table_data.append([
                Paragraph(service.get('name', '—'), self.styles['TableValue']),
                Paragraph(conditions.get('term', '—'), self.styles['TableValue']),
                Paragraph(f"${rent:,.0f}", self.styles['TableValue']),
                Paragraph(
                    f"${install:,.0f}" if install > 0 else '—',
                    self.styles['TableValue']
                )
            ])
        
        # Fila de totales
        table_data.append([
            Paragraph('<b>TOTAL MENSUAL</b>', self.styles['TableValue']),
            Paragraph('', self.styles['TableValue']),
            Paragraph(f"<b>${total_monthly:,.0f} MXN + IVA</b>", self.styles['TableValue']),
            Paragraph(f"<b>${total_installation:,.0f}</b>", self.styles['TableValue'])
        ])
        
        table = Table(table_data, colWidths=[2*inch, 1.3*inch, 2.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['dark_blue']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Fila de totales (último)
            ('BACKGROUND', (0, -1), (-1, -1), COLORS['cyan']),
            ('TEXTCOLOR', (0, -1), (-1, -1), COLORS['white']),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Filas de datos
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [COLORS['white'], COLORS['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['dark_blue']),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        
        # Footer
        self.story.append(Spacer(1, 0.4*inch))
        footer_text = "Todos los precios son + IVA. Vigencia de esta propuesta: 30 días naturales."
        self.story.append(Paragraph(footer_text, self.styles['ExecInfo']))
    
    def generate(self, proposal_data):
        """Genera el PDF y retorna bytes"""
        # Limpiar story para cada generación
        self.story = []
        
        # Agregar portada
        self._add_cover_page(proposal_data.get('executive', {}))
        self.story.append(PageBreak())
        
        # Agregar página "Quiénes somos"
        self._add_about_page()
        self.story.append(PageBreak())
        
        # Agregar una página por servicio
        services = proposal_data.get('services', [])
        for service in services:
            self._add_service_page(service)
            self.story.append(PageBreak())
        
        # Agregar resumen económico
        self._add_summary_page(proposal_data)
        
        # Generar PDF en buffer de memoria
        pdf_buffer = io.BytesIO()
        self.doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            title='CMC Network - Propuesta Comercial'
        )
        self.doc.build(self.story)
        
        # Retornar bytes del PDF
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

# ============================================================================
# FUNCIÓN GENERADORA
# ============================================================================

def generate_proposal(output_path, proposal_data):
    """Genera propuesta PDF"""
    generator = CMCProposalGeneratorV2(output_path)
    pdf_bytes = generator.generate(proposal_data)
    
    # Si se proporciona output_path, guardar en archivo
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    return pdf_bytes

# ============================================================================
# EJEMPLO
# ============================================================================

if __name__ == '__main__':
    data = {
        'executive': {
            'name': 'Daniel Flores',
            'title': 'Senior Executive',
            'email': 'dflores@cmcnetworkmx.com',
            'phone': '55 1929 8160'
        },
        'services': [
            {
                'name': 'Internet Dedicado',
                'description': 'Internet Dedicado es la solución ideal para empresas con alto volumen de operaciones y la necesidad de conectividad estable. Con cobertura por fibra óptica y microondas, CMC Network garantiza latencias bajas y redundancia de ruta. El contrato incluye SLA del 99.9%, soporte técnico 24/7 y tiempo de respuesta menor a 4 horas ante cualquier falla.',
                'conditions': {
                    'term': '24 meses',
                    'monthly_rent': '$4,500',
                    'installation': '$2,800',
                    'special_conditions': 'SLA 99.9%, soporte 24/7, instalación en 5 días hábiles'
                }
            },
            {
                'name': 'Telefonía IP / Cloud PBX',
                'description': 'La Telefonía IP con PBX en la nube moderniza las comunicaciones sin inversión en infraestructura física. Concesionados por la IFT, operamos nuestro propio PBX con mayor control, seguridad y reducción de costos. Incluye 10 extensiones, llamadas nacionales sin límite, app Thirdlane Connect y portabilidad de números en menos de 48 horas hábiles.',
                'conditions': {
                    'term': '12 meses',
                    'monthly_rent': '$1,550',
                    'installation': 'Sin costo',
                    'special_conditions': 'Incluye 10 extensiones, portabilidad en 48h'
                }
            }
        ]
    }
    
    generate_proposal('/mnt/user-data/outputs/CMC_Propuesta_Demo_v2.pdf', data)
    print("✓ PDF generado exitosamente")
