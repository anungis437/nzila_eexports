"""
PHASE 2 - Feature 5: CBSA Form 1 Generator

Generates official Canada Border Services Agency Form 1 - Vehicle Export Declaration.

This form is required when exporting vehicles from Canada. It must be presented
at the Canadian border at the time of export.

Reference: CBSA Form BSF407 (Vehicle Export Declaration)
Valid for: 30 days from date of issue
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime, timedelta
from django.utils import timezone


class CBSAForm1Generator:
    """
    Generate CBSA Form 1 (BSF407) - Vehicle Export Declaration
    
    This form is required for all vehicle exports from Canada.
    """
    
    def __init__(self, vehicle, buyer, export_date=None):
        """
        Initialize CBSA Form generator
        
        Args:
            vehicle: Vehicle instance
            buyer: User instance (buyer)
            export_date: Expected export date (defaults to today)
        """
        self.vehicle = vehicle
        self.buyer = buyer
        self.export_date = export_date or timezone.now()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        self.field_label_style = ParagraphStyle(
            'FieldLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        )
        
        self.field_value_style = ParagraphStyle(
            'FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica'
        )
    
    def generate_pdf(self):
        """
        Generate CBSA Form 1 PDF and return as BytesIO
        
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Header
        story.append(Paragraph("CANADA BORDER SERVICES AGENCY", self.title_style))
        story.append(Paragraph("VEHICLE EXPORT DECLARATION", self.title_style))
        story.append(Paragraph("Form BSF407", self.field_label_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Form metadata
        form_number = f"EXP{self.vehicle.id:06d}{timezone.now().strftime('%Y%m%d')}"
        issue_date = self.export_date.strftime('%Y-%m-%d')
        expiry_date = (self.export_date + timedelta(days=30)).strftime('%Y-%m-%d')
        
        metadata_data = [
            ['Form Number:', form_number, 'Issue Date:', issue_date],
            ['Valid Until:', expiry_date, 'Export Port:', '_________________'],
        ]
        
        metadata_table = Table(metadata_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Section 1: Exporter Information
        story.append(Paragraph("1. EXPORTER INFORMATION", self.section_style))
        exporter_data = [
            ['Full Name:', self.buyer.get_full_name() or self.buyer.username],
            ['Address:', self._get_buyer_address()],
            ['Phone:', self.buyer.phone or 'N/A'],
            ['Email:', self.buyer.email],
        ]
        story.append(self._create_field_table(exporter_data))
        story.append(Spacer(1, 0.15*inch))
        
        # Section 2: Vehicle Information
        story.append(Paragraph("2. VEHICLE INFORMATION", self.section_style))
        vehicle_data = [
            ['Year:', str(self.vehicle.year)],
            ['Make:', self.vehicle.make],
            ['Model:', self.vehicle.model],
            ['VIN:', self.vehicle.vin],
            ['Color:', self.vehicle.color or 'N/A'],
            ['Odometer:', f"{self.vehicle.mileage:,} km"],
            ['Transmission:', self.vehicle.transmission or 'N/A'],
            ['Fuel Type:', self.vehicle.get_fuel_type_display() if self.vehicle.fuel_type else 'N/A'],
        ]
        story.append(self._create_field_table(vehicle_data))
        story.append(Spacer(1, 0.15*inch))
        
        # Section 3: Export Details
        story.append(Paragraph("3. EXPORT DETAILS", self.section_style))
        export_data = [
            ['Purpose of Export:', 'Personal Use / Resale'],
            ['Destination Country:', '_________________'],
            ['Expected Export Date:', self.export_date.strftime('%Y-%m-%d')],
            ['Current Location:', self.vehicle.location or 'N/A'],
        ]
        story.append(self._create_field_table(export_data))
        story.append(Spacer(1, 0.15*inch))
        
        # Section 4: Declaration
        story.append(Paragraph("4. DECLARATION", self.section_style))
        declaration_text = """
        I hereby declare that:<br/>
        • I am the registered owner or authorized representative of the vehicle described above<br/>
        • The information provided in this declaration is true and complete to the best of my knowledge<br/>
        • I understand that this vehicle must be presented at a Canadian border for export verification<br/>
        • I will comply with all export requirements under the Customs Act and related regulations<br/>
        • There are no outstanding liens, loans, or encumbrances on this vehicle (or they have been disclosed)<br/>
        • This form is valid for 30 days from the issue date<br/>
        """
        story.append(Paragraph(declaration_text, self.field_value_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Signature section
        signature_data = [
            ['Signature:', '_' * 40, 'Date:', '_' * 20],
            ['', '', '', ''],
            ['Printed Name:', self.buyer.get_full_name() or self.buyer.username, '', ''],
        ]
        signature_table = Table(signature_data, colWidths=[1.2*inch, 3*inch, 0.8*inch, 2*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer / Important notes
        story.append(Paragraph("IMPORTANT NOTES:", self.section_style))
        notes_text = """
        • This form must be presented at a Canadian port of exit at the time of vehicle export<br/>
        • Keep a copy for your records<br/>
        • Failure to properly export a vehicle may result in penalties<br/>
        • For questions, contact CBSA at 1-800-461-9999 or visit www.cbsa-asfc.gc.ca<br/>
        • Vehicle must be paid in full with no outstanding liens<br/>
        • Provincial registration cancellation may be required - contact your provincial registry<br/>
        """
        story.append(Paragraph(notes_text, ParagraphStyle(
            'Notes',
            parent=self.field_value_style,
            fontSize=8,
            textColor=colors.HexColor('#666666')
        )))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_field_table(self, data):
        """Create a formatted table for form fields"""
        table = Table(data, colWidths=[2*inch, 5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table
    
    def _get_buyer_address(self):
        """Get formatted buyer address"""
        parts = []
        if hasattr(self.buyer, 'city') and self.buyer.city:
            parts.append(self.buyer.city)
        if hasattr(self.buyer, 'province') and self.buyer.province:
            parts.append(self.buyer.province)
        if hasattr(self.buyer, 'postal_code') and self.buyer.postal_code:
            parts.append(self.buyer.postal_code)
        
        return ', '.join(parts) if parts else 'N/A'
    
    def _get_vehicle_province(self):
        """Extract province from vehicle location"""
        if self.vehicle.location:
            # Location format is typically "City, Province"
            parts = self.vehicle.location.split(',')
            if len(parts) >= 2:
                return parts[-1].strip()
        return 'N/A'
