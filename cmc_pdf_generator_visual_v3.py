"""
CMC Network - Generador de PDF Visual V3
Páginas 1-4: Imágenes estáticas (portada, quiénes somos, cobertura, portafolio)
Páginas 5+: Páginas NUEVAS con datos dinámicos del formulario
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
import os

class CMCProposalGeneratorV3:
    """Generador: imágenes fijas + páginas dinámicas nuevas"""
    
    def __init__(self, images_dir=None):
        self.images_dir = images_dir or os.path.dirname(__file__)
        self.dark_blue = HexColor('#001F3D')
        self.cyan = HexColor('#00BCD4')
    
    def generate(self, proposal_data):
        """Genera PDF: páginas 1-4 (imágenes), 5+ (dinámicas)"""
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # ===== PÁGINAS 1-4: IMÁGENES ESTÁTICAS =====
        image_files = ['1.jpeg', '2.jpeg', '3.jpeg', '4.jpeg']
        
        for img_file in image_files:
            img_path = os.path.join(self.images_dir, img_file)
            if os.path.exists(img_path):
                story.append(RLImage(img_path, width=7.5*inch, height=4.35*inch))
                story.append(PageBreak())
        
        # ===== PÁGINAS 5+: SERVICIOS DINÁMICOS =====
        for service in proposal_data.get('services', []):
            story.append(self._create_service_page(service, styles))
            story.append(PageBreak())
        
        # ===== ÚLTIMA PÁGINA: RESUMEN DINÁMICO =====
        story.append(self._create_summary_page(proposal_data, styles))
        
        # Compilar PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _create_service_page(self, service, styles):
        """Crea página de servicio con datos dinámicos"""
        
        story = []
        
        # Encabezado del servicio
        service_name = service.get('name', 'Servicio')
        style = ParagraphStyle(
            'ServiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.dark_blue,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(service_name, style))
        
        # Descripción
        description = service.get('description', '')
        if description:
            desc_style = ParagraphStyle(
                'Description',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                textColor=HexColor('#555555')
            )
            story.append(Paragraph(description, desc_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Tabla de condiciones
        conditions = service.get('conditions', {})
        
        data = [
            ['Plazo del contrato', conditions.get('term', '')],
            ['Renta mensual', conditions.get('monthly_rent', '')],
            ['Instalación / Equipo', conditions.get('installation', '')],
            ['Condiciones especiales', service.get('notes', 'Sin condiciones especiales')]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.dark_blue),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F5F5F5')]),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_summary_page(self, proposal_data, styles):
        """Crea página de resumen con tabla de servicios"""
        
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'SummaryTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=self.dark_blue,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph('RESUMEN ECONÓMICO CONSOLIDADO', title_style))
        
        # Tabla de servicios
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
        
        # Fila de TOTAL
        data.append([
            'TOTAL MENSUAL',
            '',
            f'${total_monthly:,.0f} MXN + IVA',
            f'${total_installation:,.0f}'
        ])
        
        # Crear tabla
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
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Nota de vigencia
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#999999'),
            alignment=TA_LEFT
        )
        story.append(Paragraph(
            '<i>Todos los precios son + IVA. Vigencia de esta propuesta: 30 días naturales.</i>',
            note_style
        ))
        
        return story


def generate_visual_pdf(proposal_data, images_dir=None):
    """Wrapper para generar PDF desde Flask"""
    generator = CMCProposalGeneratorV3(images_dir)
    return generator.generate(proposal_data)
