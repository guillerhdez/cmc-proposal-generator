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

    # Mapeo de servicios a imágenes de características (página 1 por servicio)
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

    # Mapeo de servicios a imágenes de condiciones (página 2 por servicio)
    SERVICE_COND_IMAGES = {
        'Internet Dedicado': '01-internet-dedicado-cond.jpg',
        'Internet para Eventos': '02-internet-eventos-cond.jpg',
        'Internet Satelital': '03-internet-satelital-cond.jpg',
        'Conectividad LTE': '04-conectividad-lte-cond.jpg',
        'Telefonía IP': '05-telefonia-ip-cond.jpg',
        'Telefonía IP / Cloud PBX': '05-telefonia-ip-cond.jpg',
        'Ciberseguridad Integral': '06-ciberseguridad-cond.jpg',
        # IoT/CCTV no tiene slide de condiciones en el VIP, usar características
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

        # Páginas de servicios: 2 páginas por servicio
        for service in proposal_data.get('services', []):
            # Página 1: slide de características a pantalla completa
            new_page()
            self._draw_service_features_page(c, service)
            # Página 2: slide de condiciones como fondo + tabla encima
            new_page()
            self._draw_service_conditions_page(c, service)

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

    def _draw_service_features_page(self, c, service):
        """Página 1 por servicio: slide de características a pantalla completa (cover)."""
        PW, PH = self.PAGE_W, self.PAGE_H
        service_name = service.get('name', '')
        img_filename = self.SERVICE_IMAGES.get(service_name, '05-telefonia-ip.jpg')
        img_path = os.path.join(self.images_dir, img_filename)
        self._draw_cover_image(c, img_path, 0, 0, PW, PH)

    # Bounds de la tabla nativa en cada slide de condiciones del VIP
    # (left%, right%, top%, bottom%) — medidos y confirmados visualmente
    SERVICE_COND_TABLE_BOUNDS = {
        'Internet Dedicado':        (0.01,  0.526, 0.21,  0.88),
        'Internet Satelital':       (0.027, 0.53,  0.20,  0.888),
        'Telefonía IP':             (0.04,  0.535, 0.20,  0.878),
        'Telefonía IP / Cloud PBX': (0.04,  0.535, 0.20,  0.878),
    }

    # Servicios que usan slide de condiciones del VIP como fondo
    SERVICES_WITH_COND_SLIDE = {
        'Internet Dedicado',
        'Internet Satelital',
        'Telefonía IP',
        'Telefonía IP / Cloud PBX',
    }

    def _draw_service_conditions_page(self, c, service):
        """Página 2 por servicio:
        - Si el servicio tiene slide de condiciones VIP: lo usa como fondo,
          tapa la tabla nativa y pone la tabla del formulario encima.
        - Si no: fondo azul marino institucional + tabla del formulario.
        El panel se ajusta al tamaño de la tabla, no a toda la página."""
        PW, PH = self.PAGE_W, self.PAGE_H

        service_name = service.get('name', '')
        conditions = service.get('conditions', {})
        coordinates = (service.get('coordinates') or '').strip()
        description = (service.get('description') or '').strip()
        special_conditions = (conditions.get('special_conditions') or '').strip()

        has_cond_slide = service_name in self.SERVICES_WITH_COND_SLIDE
        pad = 14

        # ── FILAS DE LA TABLA ──────────────────────────────────────────────
        rows = [
            ('CONDICIÓN', 'DETALLE'),
            ('PLAZO', conditions.get('term', '') or '—'),
            ('RENTA MENSUAL', conditions.get('monthly_rent', '') or '—'),
            ('INSTALACIÓN', conditions.get('installation', '') or '—'),
        ]
        if coordinates:
            rows.append(('COORDENADAS', coordinates))
        if description:
            rows.append(('DESCRIPCIÓN', description))
        if special_conditions:
            rows.append(('CONDICIONES ESP.', special_conditions))

        row_h = 26
        title_h = 28
        sep_h = 10
        table_h = row_h * len(rows)
        panel_h = pad + title_h + sep_h + table_h + pad

        # ── 1. FONDO ───────────────────────────────────────────────────────
        if has_cond_slide:
            # Fondo = slide de condiciones del VIP
            cond_filename = self.SERVICE_COND_IMAGES.get(service_name, '01-internet-dedicado-cond.jpg')
            cond_path = os.path.join(self.images_dir, cond_filename)
            self._draw_cover_image(c, cond_path, 0, 0, PW, PH)

            # Tapar tabla nativa con rectángulo del color del fondo oscuro del slide
            bounds = self.SERVICE_COND_TABLE_BOUNDS.get(service_name, (0, 0.53, 0.21, 0.88))
            bl, br, bt, bb = bounds
            # En ReportLab y=0 es abajo; convertir %: top del PDF = PH*(1-bt), bottom = PH*(1-bb)
            cover_x = PW * bl
            cover_w = PW * br - cover_x
            cover_y = PH * (1.0 - bb)
            cover_h = PH * (bb - bt)
            c.setFillColor(self.dark_blue)
            c.rect(cover_x, cover_y, cover_w, cover_h, stroke=0, fill=1)
        else:
            # Fondo azul marino institucional con patrón geométrico
            c.setFillColor(self.dark_blue)
            c.rect(0, 0, PW, PH, stroke=0, fill=1)
            # Líneas decorativas diagonales tipo CMC
            c.saveState()
            c.setStrokeColor(HexColor('#002B5C'))
            c.setLineWidth(40)
            for i in range(-2, 6):
                x = PW * 0.6 + i * 120
                c.line(x, 0, x + PH, PH)
            c.restoreState()

        # ── 2. PANEL con tabla — tamaño ajustado al contenido ──────────────
        # Posición: centrado verticalmente, alineado a la izquierda
        panel_w = PW * 0.42
        panel_x = 0
        panel_y = (PH - panel_h) / 2.0  # centrado vertical

        # Fondo del panel
        c.setFillColor(self.dark_blue)
        c.rect(panel_x, panel_y, panel_w, panel_h, stroke=0, fill=1)

        # Borde cyan derecho e inferior
        c.setFillColor(self.cyan)
        c.rect(panel_x + panel_w - 2, panel_y, 2, panel_h, stroke=0, fill=1)
        c.rect(panel_x, panel_y, panel_w, 2, stroke=0, fill=1)
        c.rect(panel_x, panel_y + panel_h - 2, panel_w, 2, stroke=0, fill=1)

        # ── 3. TÍTULO ──────────────────────────────────────────────────────
        y_cursor = panel_y + panel_h - pad

        p_title = Paragraph(service_name, ParagraphStyle(
            'cond_title', fontName='Helvetica-Bold', fontSize=12,
            leading=15, textColor=white
        ))
        tw, th = p_title.wrap(panel_w - 2 * pad, title_h)
        p_title.drawOn(c, panel_x + pad, y_cursor - th)
        y_cursor -= title_h

        # Separador cyan
        c.setFillColor(self.cyan)
        c.rect(panel_x + pad, y_cursor - 2, panel_w - 2 * pad, 1.5, stroke=0, fill=1)
        y_cursor -= sep_h

        # ── 4. FILAS DE LA TABLA ───────────────────────────────────────────
        col_w_label = (panel_w - 2 * pad) * 0.42
        col_w_value = (panel_w - 2 * pad) * 0.58

        style_header = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8,
                                      leading=10, textColor=white)
        style_cell_label = ParagraphStyle('td_label', fontName='Helvetica-Bold', fontSize=7.5,
                                          leading=9, textColor=self.cyan)
        style_cell_value = ParagraphStyle('td_val', fontName='Helvetica', fontSize=7.5,
                                          leading=9, textColor=white)

        for i, (label, value) in enumerate(rows):
            row_y = y_cursor - row_h
            if i == 0:
                c.setFillColor(self.cyan)
            elif i % 2 == 1:
                c.setFillColor(HexColor('#002244'))
            else:
                c.setFillColor(HexColor('#001A33'))
            c.rect(panel_x + pad, row_y, panel_w - 2 * pad, row_h, stroke=0, fill=1)

            st_l = style_header if i == 0 else style_cell_label
            st_v = style_header if i == 0 else style_cell_value

            p_l = Paragraph(label, st_l)
            p_l.wrap(col_w_label - 4, row_h - 4)
            p_l.drawOn(c, panel_x + pad + 4, row_y + 6)

            p_v = Paragraph(value, st_v)
            p_v.wrap(col_w_value - 4, row_h - 4)
            p_v.drawOn(c, panel_x + pad + col_w_label + 4, row_y + 6)

            y_cursor -= row_h

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
