"""
PDF Generation Utilities
Uses ReportLab to generate branded PDF documents
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, Frame, PageTemplate
)
from reportlab.lib.utils import ImageReader
from django.conf import settings


class PDFGenerator:
    """Base PDF generator with company branding"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            alignment=TA_RIGHT
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=20,
            borderWidth=0,
            borderColor=colors.HexColor('#1976d2'),
            borderPadding=5,
            backColor=colors.HexColor('#e3f2fd')
        ))
    
    def _add_header(self, canvas, doc):
        """Add company header to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#1976d2'))
        canvas.drawString(inch, doc.height + doc.topMargin + 0.5 * inch, 
                         getattr(settings, 'COMPANY_NAME', 'Nzila Export'))
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(inch, doc.height + doc.topMargin + 0.3 * inch,
                         'Canadian Vehicle Export Specialists')
        canvas.restoreState()
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        
        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(doc.width + doc.leftMargin, 0.5 * inch, text)
        
        # Company info
        canvas.drawString(inch, 0.5 * inch, 
                         f"{getattr(settings, 'COMPANY_NAME', 'Nzila Export')} | "
                         f"{getattr(settings, 'SUPPORT_EMAIL', 'support@nzilaexport.com')} | "
                         f"{getattr(settings, 'SUPPORT_PHONE', '1-800-NZILA-EX')}")
        
        canvas.restoreState()


class InvoicePDFGenerator(PDFGenerator):
    """Generate professional invoice PDFs"""
    
    def generate(self, invoice):
        """Generate invoice PDF and return BytesIO buffer"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=1.5*inch, bottomMargin=inch)
        
        # Build document content
        story = []
        
        # Invoice title and number
        story.append(Paragraph("INVOICE", self.styles['InvoiceTitle']))
        story.append(Paragraph(f"Invoice #{invoice.invoice_number}", 
                              self.styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice dates
        dates_data = [
            ['Invoice Date:', invoice.created_at.strftime('%B %d, %Y')],
            ['Due Date:', invoice.due_date.strftime('%B %d, %Y')],
            ['Status:', invoice.get_status_display()],
        ]
        dates_table = Table(dates_data, colWidths=[2*inch, 3*inch])
        dates_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(dates_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Bill To section
        story.append(Paragraph("BILL TO", self.styles['SectionHeader']))
        if invoice.deal and invoice.deal.buyer:
            buyer = invoice.deal.buyer
            bill_to_text = f"""
            <b>{buyer.full_name}</b><br/>
            {buyer.email}<br/>
            {buyer.phone if hasattr(buyer, 'phone') and buyer.phone else ''}
            """
            story.append(Paragraph(bill_to_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Vehicle Details (if applicable)
        if invoice.deal and invoice.deal.vehicle:
            story.append(Paragraph("VEHICLE DETAILS", self.styles['SectionHeader']))
            vehicle = invoice.deal.vehicle
            vehicle_text = f"""
            <b>{vehicle.year} {vehicle.make} {vehicle.model}</b><br/>
            VIN: {vehicle.vin}<br/>
            Color: {vehicle.color}<br/>
            Mileage: {vehicle.mileage:,} km
            """
            story.append(Paragraph(vehicle_text, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Line Items
        story.append(Paragraph("INVOICE ITEMS", self.styles['SectionHeader']))
        items_data = [['Description', 'Quantity', 'Unit Price', 'Amount']]
        
        # Add invoice items (customize based on your InvoiceItem model)
        if hasattr(invoice, 'items'):
            for item in invoice.items.all():
                items_data.append([
                    item.description,
                    str(item.quantity),
                    f"${item.unit_price:,.2f}",
                    f"${item.total:,.2f}"
                ])
        else:
            # Default item if no line items
            items_data.append([
                'Vehicle Purchase & Export Services',
                '1',
                f"${invoice.total_amount:,.2f}",
                f"${invoice.total_amount:,.2f}"
            ])
        
        # Add subtotal, tax, total rows
        items_data.extend([
            ['', '', 'Subtotal:', f"${invoice.total_amount:,.2f}"],
            ['', '', 'Tax (0%):', '$0.00'],
            ['', '', 'TOTAL DUE:', f"${invoice.total_amount:,.2f}"],
        ])
        
        items_table = Table(items_data, colWidths=[3.5*inch, inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -4), [colors.white, colors.HexColor('#f5f5f5')]),
            
            # Totals rows
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
            
            # All borders
            ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Payment Instructions
        story.append(Paragraph("PAYMENT INSTRUCTIONS", self.styles['SectionHeader']))
        payment_text = """
        Please make payment by the due date to avoid late fees.<br/><br/>
        <b>Payment Methods:</b><br/>
        • Wire Transfer: Contact us for banking details<br/>
        • Credit Card: Pay online through your customer portal<br/>
        • Interac e-Transfer: Send to payments@nzilaexport.com<br/><br/>
        <b>Note:</b> Please include your invoice number in the payment reference.
        """
        story.append(Paragraph(payment_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Terms & Conditions
        story.append(Paragraph("TERMS & CONDITIONS", self.styles['SectionHeader']))
        terms_text = """
        Payment is due within 30 days of invoice date. A late fee of 2% per month 
        will be applied to overdue balances. All sales are final unless otherwise 
        specified in writing. Vehicle title transfer occurs upon full payment receipt.
        """
        story.append(Paragraph(terms_text, self.styles['Normal']))
        
        # Build PDF with header/footer
        doc.build(story, onFirstPage=self._add_header, onLaterPages=self._add_header)
        
        buffer.seek(0)
        return buffer


class ComplianceReportPDFGenerator(PDFGenerator):
    """Generate compliance audit reports"""
    
    def generate_data_breach_report(self, breach):
        """Generate data breach incident report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=1.5*inch, bottomMargin=inch)
        
        story = []
        
        # Report title
        story.append(Paragraph("DATA BREACH INCIDENT REPORT", self.styles['CompanyHeader']))
        story.append(Paragraph(f"Report ID: {breach.breach_id}", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Incident summary
        summary_data = [
            ['Severity:', breach.get_severity_display()],
            ['Status:', breach.get_status_display()],
            ['Discovery Date:', breach.breach_date.strftime('%B %d, %Y')],
            ['Reported By:', breach.reported_by.full_name if breach.reported_by else 'N/A'],
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        story.append(Paragraph("INCIDENT DESCRIPTION", self.styles['SectionHeader']))
        story.append(Paragraph(breach.description, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header, onLaterPages=self._add_header)
        
        buffer.seek(0)
        return buffer


# Convenience functions
def generate_invoice_pdf(invoice):
    """Generate invoice PDF - returns BytesIO buffer"""
    generator = InvoicePDFGenerator()
    return generator.generate(invoice)


def generate_breach_report_pdf(breach):
    """Generate data breach report PDF - returns BytesIO buffer"""
    generator = ComplianceReportPDFGenerator()
    return generator.generate_data_breach_report(breach)
