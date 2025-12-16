from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from io import BytesIO
import os


class PDFGenerator:
    """Comprehensive PDF generation service for invoices, receipts, and reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom PDF styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        # Header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#334155'),
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Right-aligned style
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))

    def _add_header(self, canvas, doc):
        """Add header to PDF pages"""
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#1e40af'))
        canvas.drawString(inch, 10.5 * inch, "Nzila Exports")
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawString(inch, 10.3 * inch, "Premium Vehicle Export Services")
        canvas.restoreState()

    def _add_footer(self, canvas, doc):
        """Add footer to PDF pages"""
        canvas.saveState()
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        canvas.drawString(
            inch, 0.5 * inch,
            f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}"
        )
        canvas.drawRightString(
            7.5 * inch, 0.5 * inch,
            f"Page {page_num}"
        )
        canvas.restoreState()

    def generate_invoice(self, payment_data, deal_data=None, buyer_data=None):
        """
        Generate a professional invoice PDF
        
        Args:
            payment_data: Dict with payment information (amount, currency, date, etc.)
            deal_data: Optional dict with deal details
            buyer_data: Optional dict with buyer information
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=1.5*inch,
            bottomMargin=inch
        )

        # Container for PDF elements
        elements = []

        # Title
        elements.append(Paragraph("INVOICE", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2 * inch))

        # Invoice metadata
        invoice_data = [
            ['Invoice Number:', payment_data.get('invoice_number', 'N/A')],
            ['Date:', payment_data.get('date', timezone.now().strftime('%B %d, %Y'))],
            ['Due Date:', payment_data.get('due_date', 'Upon Receipt')],
            ['Status:', payment_data.get('status', 'Pending').upper()],
        ]

        invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Billing information
        if buyer_data:
            elements.append(Paragraph("Bill To:", self.styles['SectionHeader']))
            billing_info = f"""
            <b>{buyer_data.get('name', 'N/A')}</b><br/>
            {buyer_data.get('email', '')}<br/>
            {buyer_data.get('phone', '')}<br/>
            {buyer_data.get('address', '')}
            """
            elements.append(Paragraph(billing_info, self.styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

        # Deal/Service details
        if deal_data:
            elements.append(Paragraph("Service Details:", self.styles['SectionHeader']))
            service_data = [
                ['Description', 'Quantity', 'Unit Price', 'Amount'],
                [
                    deal_data.get('description', 'Vehicle Export Service'),
                    '1',
                    f"{payment_data.get('currency', 'USD')} {payment_data.get('amount', 0):,.2f}",
                    f"{payment_data.get('currency', 'USD')} {payment_data.get('amount', 0):,.2f}"
                ]
            ]

            service_table = Table(service_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
            service_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(service_table)
            elements.append(Spacer(1, 0.3 * inch))

        # Total summary
        elements.append(Paragraph("Payment Summary:", self.styles['SectionHeader']))
        
        subtotal = payment_data.get('amount', 0)
        tax = payment_data.get('tax', 0)
        total = subtotal + tax

        summary_data = [
            ['Subtotal:', f"{payment_data.get('currency', 'USD')} {subtotal:,.2f}"],
            ['Tax:', f"{payment_data.get('currency', 'USD')} {tax:,.2f}"],
            ['', ''],  # Spacer row
            ['Total:', f"{payment_data.get('currency', 'USD')} {total:,.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[4.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 2), 'Helvetica'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('TEXTCOLOR', (0, 0), (-1, 2), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#1e40af')),
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#1e40af')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Payment information
        elements.append(Paragraph("Payment Information:", self.styles['SectionHeader']))
        payment_info = f"""
        <b>Payment Method:</b> {payment_data.get('payment_method', 'Bank Transfer')}<br/>
        <b>Transaction ID:</b> {payment_data.get('transaction_id', 'N/A')}<br/>
        <b>Payment Date:</b> {payment_data.get('payment_date', 'Pending')}
        """
        elements.append(Paragraph(payment_info, self.styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # Terms and notes
        if payment_data.get('notes'):
            elements.append(Paragraph("Notes:", self.styles['SectionHeader']))
            elements.append(Paragraph(payment_data['notes'], self.styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

        # Footer text
        footer_text = """
        <b>Thank you for your business!</b><br/>
        For questions about this invoice, please contact us at support@nzilaexports.com
        """
        elements.append(Paragraph(footer_text, self.styles['CustomSubtitle']))

        # Build PDF
        doc.build(
            elements,
            onFirstPage=lambda c, d: (self._add_header(c, d), self._add_footer(c, d)),
            onLaterPages=lambda c, d: (self._add_header(c, d), self._add_footer(c, d))
        )

        buffer.seek(0)
        return buffer

    def generate_receipt(self, payment_data, deal_data=None):
        """
        Generate a payment receipt PDF
        
        Args:
            payment_data: Dict with payment information
            deal_data: Optional dict with deal details
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=1.5*inch,
            bottomMargin=inch
        )

        elements = []

        # Title
        elements.append(Paragraph("PAYMENT RECEIPT", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3 * inch))

        # Receipt number and date
        receipt_header = f"""
        <b>Receipt #:</b> {payment_data.get('receipt_number', 'N/A')}<br/>
        <b>Date:</b> {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        elements.append(Paragraph(receipt_header, self.styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # Payment details
        elements.append(Paragraph("Payment Details:", self.styles['SectionHeader']))
        
        payment_details = [
            ['Amount Paid:', f"{payment_data.get('currency', 'USD')} {payment_data.get('amount', 0):,.2f}"],
            ['Payment Method:', payment_data.get('payment_method', 'N/A')],
            ['Transaction ID:', payment_data.get('transaction_id', 'N/A')],
            ['Status:', payment_data.get('status', 'Completed').upper()],
        ]

        details_table = Table(payment_details, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Confirmation message
        confirmation = f"""
        <b>Payment Confirmed</b><br/><br/>
        This receipt confirms that we have received your payment of 
        <b>{payment_data.get('currency', 'USD')} {payment_data.get('amount', 0):,.2f}</b>.<br/><br/>
        Thank you for your payment!
        """
        elements.append(Paragraph(confirmation, self.styles['CustomSubtitle']))

        # Build PDF
        doc.build(
            elements,
            onFirstPage=lambda c, d: (self._add_header(c, d), self._add_footer(c, d)),
            onLaterPages=lambda c, d: (self._add_header(c, d), self._add_footer(c, d))
        )

        buffer.seek(0)
        return buffer

    def generate_deal_report(self, deal_data, include_financials=True):
        """
        Generate a comprehensive deal report PDF
        
        Args:
            deal_data: Dict with deal information
            include_financials: Boolean to include financial details
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=1.5*inch,
            bottomMargin=inch
        )

        elements = []

        # Title
        elements.append(Paragraph("DEAL REPORT", self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Deal #{deal_data.get('deal_number', 'N/A')}",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 0.3 * inch))

        # Deal overview
        elements.append(Paragraph("Deal Overview:", self.styles['SectionHeader']))
        overview_data = [
            ['Status:', deal_data.get('status', 'N/A')],
            ['Created:', deal_data.get('created_date', 'N/A')],
            ['Last Updated:', deal_data.get('updated_date', 'N/A')],
            ['Stage:', deal_data.get('stage', 'N/A')],
        ]

        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Vehicle information
        if deal_data.get('vehicle'):
            elements.append(Paragraph("Vehicle Information:", self.styles['SectionHeader']))
            vehicle = deal_data['vehicle']
            vehicle_info = f"""
            <b>{vehicle.get('make', '')} {vehicle.get('model', '')}</b><br/>
            Year: {vehicle.get('year', 'N/A')}<br/>
            VIN: {vehicle.get('vin', 'N/A')}<br/>
            Color: {vehicle.get('color', 'N/A')}
            """
            elements.append(Paragraph(vehicle_info, self.styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))

        # Financial details
        if include_financials and deal_data.get('financials'):
            elements.append(Paragraph("Financial Details:", self.styles['SectionHeader']))
            financials = deal_data['financials']
            
            financial_data = [
                ['Item', 'Amount'],
                ['Purchase Price', f"${financials.get('purchase_price', 0):,.2f}"],
                ['Commission', f"${financials.get('commission', 0):,.2f}"],
                ['Shipping', f"${financials.get('shipping', 0):,.2f}"],
                ['Total', f"${financials.get('total', 0):,.2f}"],
            ]

            financial_table = Table(financial_data, colWidths=[3*inch, 2*inch])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(financial_table)

        # Build PDF
        doc.build(
            elements,
            onFirstPage=lambda c, d: (self._add_header(c, d), self._add_footer(c, d)),
            onLaterPages=lambda c, d: (self._add_header(c, d), self._add_footer(c, d))
        )

        buffer.seek(0)
        return buffer


# Singleton instance
pdf_generator = PDFGenerator()
