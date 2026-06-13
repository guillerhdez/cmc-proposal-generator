"""
CMC Network - Generador de PDF V4 (Landscape)
Diseño basado en slides horizontales (16:9):
- Páginas 1-4: imágenes institucionales a pantalla completa (cover)
- Páginas de servicio: imagen del servicio (cover, columna derecha) +
  panel con datos del servicio (columna izquierda, fondo claro)
- Página final: imagen de fondo (portada) + tarjetas con datos del
  cliente, resumen de servicios y coordenadas de instalación
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
import io
import os


class CMCProposalGeneratorV3:
    """Generador de propuestas en formato horizontal (landscape)"""

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
        self.panel_bg = HexColor('#F0F4F8')
        self.PAGE_W, self.PAGE_H = landscape(letter)

        self.style_title = ParagraphStyle(
            'title', fontName='Helvetica-Bold', fontSize=15,
            leading=18, textColor=self.dark_blue
        )
        self.style_label = ParagraphStyle(
            'label', fontName='Helvetica-Bold', fontSize=10,
            leading=13, textColor=self.dark_blue
        )
        self.style_body = ParagraphStyle(
            'body', fontName='Helvetica', fontSize=9,
            leading=12, textColor=self.dark_blue
        )

    # ========== ENTRY POINT ==========

    def generate(self, proposal_data):
        """Genera el PDF completo en una sola pasada (landscape)"""

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(self.PAGE_W, self.PAGE_H))

        is_first_page = [True]

        def new_page():
            if not is_first_page[0]:
                c.showPage()
            is_first_page[0] = False

        # Páginas 1-4: imágenes institucionales (contain sobre fondo de marca,
        # para no recortar texto que está cerca de los bordes)
        for img_file in ['1.jpeg', '2.jpeg', '3.jpeg', '4.jpeg']:
            new_page()
            img_path = os.path.join(self.images_dir, img_file)
            self._draw_institutional_page(c, img_path)

        # Páginas de servicios
        for service in proposal_data.get('services', []):
            new_page()
            self._draw_service_page(c, service)

        # Página final: resumen
        new_page()
        self._draw_summary_page(c, proposal_data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    # ========== IMÁGENES ==========

    def _draw_institutional_page(self, c, img_path):
        """Dibuja una imagen institucional 'contenida' dentro de la página
        (sin recortar) sobre un fondo del color de marca, para que las barras
        resultantes (si las hay) se mezclen con el diseño en vez de verse
        como espacio en blanco."""

        PW, PH = self.PAGE_W, self.PAGE_H

        c.setFillColor(self.dark_blue)
        c.rect(0, 0, PW, PH, stroke=0, fill=1)

        if not os.path.exists(img_path):
            return

        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
        except Exception:
            return

        img_ratio = iw / float(ih)
        page_ratio = PW / float(PH)

        if img_ratio > page_ratio:
            draw_w = PW
            draw_h = PW / img_ratio
            ox = 0
            oy = (PH - draw_h) / 2.0
        else:
            draw_h = PH
            draw_w = PH * img_ratio
            ox = (PW - draw_w) / 2.0
            oy = 0

        c.drawImage(img, ox, oy, width=draw_w, height=draw_h, mask='auto')

    def _draw_contain_image(self, c, img_path, x, y, w, h):
        """Dibuja una imagen 'contenida' dentro del rectángulo (x,y,w,h),
        sin recortar, centrada, sobre un fondo del color de marca
        (para que las barras resultantes se mezclen con el fondo oscuro
        de las propias slides en lugar de verse como espacio en blanco)."""

        c.setFillColor(self.dark_blue)
        c.rect(x, y, w, h, stroke=0, fill=1)

        if not os.path.exists(img_path):
            return

        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
        except Exception:
            return

        img_ratio = iw / float(ih)
        rect_ratio = w / float(h)

        if img_ratio > rect_ratio:
            draw_w = w
            draw_h = w / img_ratio
            ox = x
            oy = y + (h - draw_h) / 2.0
        else:
            draw_h = h
            draw_w = h * img_ratio
            ox = x + (w - draw_w) / 2.0
            oy = y

        c.drawImage(img, ox, oy, width=draw_w, height=draw_h, mask='auto')

    def _draw_cover_image(self, c, img_path, x, y, w, h):
        """Dibuja una imagen cubriendo completamente el rectángulo (x,y,w,h),
        recortando el exceso (estilo CSS 'background-size: cover')."""

        if not os.path.exists(img_path):
            c.setFillColor(self.dark_blue)
            c.rect(x, y, w, h, stroke=0, fill=1)
            return

        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
        except Exception:
            c.setFillColor(self.dark_blue)
            c.rect(x, y, w, h, stroke=0, fill=1)
            return

        img_ratio = iw / float(ih)
        rect_ratio = w / float(h)

        if img_ratio > rect_ratio:
            draw_h = h
            draw_w = h * img_ratio
            ox = x - (draw_w - w) / 2.0
            oy = y
        else:
            draw_w = w
            draw_h = w / img_ratio
            ox = x
            oy = y - (draw_h - h) / 2.0

        c.saveState()
        path = c.beginPath()
        path.rect(x, y, w, h)
        c.clipPath(path, stroke=0)
        c.drawImage(img, ox, oy, width=draw_w, height=draw_h, mask='auto')
        c.restoreState()

    # ========== PÁGINA DE SERVICIO ==========

    def _draw_service_page(self, c, service):
        """Slide de características del servicio a pantalla completa (contain,
        16:9 dentro de la página horizontal) + datos del formulario colocados
        en las barras superior/inferior resultantes (zonas vacías del slide,
        nunca sobre los bullets ni la foto)."""

        PW, PH = self.PAGE_W, self.PAGE_H

        service_name = service.get('name', '')
        img_filename = self.SERVICE_IMAGES.get(service_name, '05-telefonia-ip.jpg')
        img_path = os.path.join(self.images_dir, img_filename)
        self._draw_contain_image(c, img_path, 0, 0, PW, PH)

        # Altura de las barras resultantes del 'contain' (16:9 dentro de 11x8.5")
        bar_h = (PH - PW * 9.0 / 16.0) / 2.0

        # Líneas de acento cyan separando las barras del slide
        c.setFillColor(self.cyan)
        c.rect(0, bar_h - 1.5, PW, 1.5, stroke=0, fill=1)
        c.rect(0, PH - bar_h - 1.5, PW, 1.5, stroke=0, fill=1)

        pad = 8

        # ===== Barra inferior: Servicio + Plazo/Renta/Instalación/Coordenadas =====
        c.setFillColor(self.panel_bg)
        c.rect(0, 0, PW, bar_h, stroke=0, fill=1)

        name_w = PW * 0.18
        p_name = Paragraph(service_name or 'Servicio', ParagraphStyle(
            'svc_name', fontName='Helvetica-Bold', fontSize=11,
            leading=13, textColor=self.dark_blue
        ))
        nw, nh = p_name.wrap(name_w - pad, bar_h - 2 * pad)
        p_name.drawOn(c, pad, (bar_h - nh) / 2.0)

        conditions = service.get('conditions', {})
        coordinates = (service.get('coordinates') or '').strip()

        field_labels = ['Plazo', 'Renta mensual', 'Instalación']
        field_values = [
            conditions.get('term', '') or '—',
            conditions.get('monthly_rent', '') or '—',
            conditions.get('installation', '') or '—',
        ]
        if coordinates:
            field_labels.append('Coordenadas')
            field_values.append(coordinates)

        fields_x = name_w
        fields_w = PW - name_w - pad
        col_w = fields_w / len(field_labels)

        for i, (label, value) in enumerate(zip(field_labels, field_values)):
            cx = fields_x + i * col_w
            p_field = Paragraph(
                f'<font size="7" color="#5A6B7D"><b>{label.upper()}</b></font><br/>'
                f'<font size="8.5">{value}</font>',
                ParagraphStyle('field', fontName='Helvetica', leading=10, textColor=self.dark_blue)
            )
            fw, fh = p_field.wrap(col_w - 6, bar_h - 2 * pad)
            p_field.drawOn(c, cx + 3, (bar_h - fh) / 2.0)

        # ===== Barra superior: Descripción + Condiciones especiales =====
        description = (service.get('description') or '').strip()
        special_conditions = (conditions.get('special_conditions') or '').strip()

        if description or special_conditions:
            c.setFillColor(self.panel_bg)
            c.rect(0, PH - bar_h, PW, bar_h, stroke=0, fill=1)

            avail_h = bar_h - 2 * pad
            half_w = PW / 2.0 - pad - pad / 2.0

            style_label_sm = ParagraphStyle('label_sm', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=self.dark_blue)
            style_body_sm = ParagraphStyle('body_sm', fontName='Helvetica', fontSize=8, leading=10, textColor=self.dark_blue)

            if description and special_conditions:
                self._draw_top_bar_block(c, 'Descripción:', description, pad, PH - bar_h + pad, half_w, avail_h, style_label_sm, style_body_sm)
                self._draw_top_bar_block(c, 'Condiciones especiales:', special_conditions, pad + half_w + pad, PH - bar_h + pad, half_w, avail_h, style_label_sm, style_body_sm)
            elif description:
                self._draw_top_bar_block(c, 'Descripción:', description, pad, PH - bar_h + pad, PW - 2 * pad, avail_h, style_label_sm, style_body_sm)
            else:
                self._draw_top_bar_block(c, 'Condiciones especiales:', special_conditions, pad, PH - bar_h + pad, PW - 2 * pad, avail_h, style_label_sm, style_body_sm)

    def _draw_top_bar_block(self, c, label, text, x, y, width, height, style_label, style_body):
        """Dibuja 'Etiqueta:' + texto envuelto dentro de un bloque de ancho/alto
        fijos (recorta verticalmente si el texto excede el alto disponible)."""

        c.saveState()
        p = c.beginPath()
        p.rect(x, y, width, height)
        c.clipPath(p, stroke=0)

        p_label = Paragraph(label, style_label)
        lw, lh = p_label.wrap(width, height)
        p_label.drawOn(c, x, y + height - lh)

        p_body = Paragraph(text, style_body)
        bw, bh = p_body.wrap(width, height - lh - 2)
        p_body.drawOn(c, x, y + height - lh - 2 - bh)

        c.restoreState()

    # ========== PÁGINA DE RESUMEN ==========

    def _draw_summary_page(self, c, proposal_data):
        """Página final: fondo institucional + tarjetas con datos del cliente,
        resumen de servicios y coordenadas de instalación."""

        PW, PH = self.PAGE_W, self.PAGE_H

        # Fondo
        bg_path = os.path.join(self.images_dir, 'portada.jpg')
        self._draw_cover_image(c, bg_path, 0, 0, PW, PH)

        # Overlay oscuro detrás del título para legibilidad
        c.saveState()
        c.setFillColor(self.dark_blue)
        c.setFillAlpha(0.45)
        c.rect(0, PH - 50, PW, 50, stroke=0, fill=1)
        c.restoreState()

        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 18)
        c.drawString(30, PH - 34, 'Resumen de la Propuesta')

        client = proposal_data.get('client', {})
        services = proposal_data.get('services', [])

        margin = 30
        gutter = 20
        top_y = PH - 70
        col_w = (PW - 2 * margin - gutter) / 2.0
        left_x = margin
        right_x = margin + col_w + gutter

        # ----- Columna izquierda: Datos del Cliente -----
        client_table = self._build_client_table(client, col_w - 24)
        self._draw_card(c, left_x, top_y, col_w, 'Datos del Cliente', client_table)

        # ----- Columna derecha: Resumen de Servicios -----
        services_table = self._build_services_table(services, col_w - 24)
        next_top = self._draw_card(c, right_x, top_y, col_w, 'Resumen de Servicios', services_table)

        # ----- Columna derecha: Coordenadas de Instalación (si aplica) -----
        services_with_coords = [
            (s.get('name', ''), s.get('coordinates', ''))
            for s in services if (s.get('coordinates') or '').strip()
        ]
        if services_with_coords:
            coords_table = self._build_coords_table(services_with_coords, col_w - 24)
            self._draw_card(c, right_x, next_top - 16, col_w, 'Coordenadas de Instalación', coords_table)

    def _draw_card(self, c, x, top_y, width, title, table):
        """Dibuja una tarjeta (fondo blanco semi-opaco) con título y tabla.
        Retorna la coordenada Y del borde inferior de la tarjeta."""

        pad = 12
        content_w = width - 2 * pad

        tw, th = table.wrapOn(c, content_w, top_y)
        title_h = 22
        card_h = pad + title_h + th + pad

        # Fondo de la tarjeta
        c.saveState()
        c.setFillColor(white)
        c.setFillAlpha(0.92)
        c.roundRect(x, top_y - card_h, width, card_h, 6, stroke=0, fill=1)
        c.restoreState()

        # Título
        c.setFillColor(self.dark_blue)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x + pad, top_y - pad - 10, title)

        # Tabla
        table.drawOn(c, x + pad, top_y - card_h + pad)

        return top_y - card_h

    # ========== TABLAS DE LA PÁGINA DE RESUMEN ==========

    def _table_style(self, label_col=True):
        style = [
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_blue),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        return style

    def _build_client_table(self, client, content_width):
        """Tabla de 2 columnas (etiqueta / valor) con los datos del cliente"""

        fields = [
            ('Empresa', client.get('company', '')),
            ('Contacto', client.get('contact', '')),
            ('Giro de Negocio', client.get('business', '')),
            ('Teléfono', client.get('phone', '')),
            ('Celular / WhatsApp', client.get('whatsapp', '')),
            ('Correo', client.get('email', '')),
            ('Dirección Fiscal', client.get('fiscal_address', '')),
            ('Dirección del Sitio', client.get('site_address', '') or client.get('fiscal_address', '')),
        ]

        data = [
            [label, Paragraph(value or '—', self.style_body)]
            for label, value in fields
        ]

        table = Table(data, colWidths=[content_width * 0.34, content_width * 0.66])
        style = self._table_style() + [
            ('BACKGROUND', (0, 0), (0, -1), self.panel_bg),
            ('BACKGROUND', (1, 0), (1, -1), white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]
        table.setStyle(TableStyle(style))
        return table

    def _build_services_table(self, services, content_width):
        """Tabla de servicios cotizados con totales"""

        data = [['SERVICIO', 'PLAZO', 'RENTA MENSUAL', 'INSTALACIÓN']]

        total_monthly = 0
        total_installation = 0

        for service in services:
            conditions = service.get('conditions', {})
            term = conditions.get('term', '')
            rent_str = conditions.get('monthly_rent', '0')
            install_str = conditions.get('installation', '0')

            try:
                rent_num = float(str(rent_str).replace('$', '').replace(',', ''))
                total_monthly += rent_num
            except (ValueError, TypeError):
                rent_num = 0

            try:
                install_num = float(str(install_str).replace('$', '').replace(',', ''))
                total_installation += install_num
            except (ValueError, TypeError):
                install_num = 0

            data.append([
                Paragraph(service.get('name', ''), self.style_body),
                term,
                f'${rent_num:,.0f}',
                f'${install_num:,.0f}',
            ])

        data.append([
            'TOTAL MENSUAL',
            '',
            f'${total_monthly:,.0f} + IVA',
            f'${total_installation:,.0f}',
        ])

        col_widths = [
            content_width * 0.36,
            content_width * 0.18,
            content_width * 0.26,
            content_width * 0.20,
        ]

        table = Table(data, colWidths=col_widths)
        style = self._table_style() + [
            ('BACKGROUND', (0, 0), (-1, 0), self.dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [white, HexColor('#F5F5F5')]),
            ('BACKGROUND', (0, -1), (-1, -1), self.dark_blue),
            ('TEXTCOLOR', (0, -1), (-1, -1), white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
        table.setStyle(TableStyle(style))
        return table

    def _build_coords_table(self, services_with_coords, content_width):
        """Tabla de 2 columnas (servicio / coordenadas)"""

        data = [['SERVICIO', 'COORDENADAS']]
        for name, coords in services_with_coords:
            data.append([
                Paragraph(name, self.style_body),
                Paragraph(coords, self.style_body),
            ])

        table = Table(data, colWidths=[content_width * 0.45, content_width * 0.55])
        style = self._table_style() + [
            ('BACKGROUND', (0, 0), (-1, 0), self.dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F5F5F5')]),
        ]
        table.setStyle(TableStyle(style))
        return table
