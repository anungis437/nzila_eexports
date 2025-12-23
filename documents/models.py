"""
PHASE 2 - Feature 5: Canadian Export Documentation Models

Models for managing export documents, CBSA forms, and export readiness checklists.
Supports Canadian diaspora buyers exporting vehicles internationally.
"""

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ExportDocument(models.Model):
    """
    Export documents for vehicles (CBSA forms, title guides, etc.)
    
    Tracks document generation, expiration, and delivery status.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('CBSA_FORM_1', 'CBSA Form 1 - Vehicle Export Declaration'),
        ('TITLE_GUIDE_ON', 'Ontario Title Transfer Guide'),
        ('TITLE_GUIDE_QC', 'Quebec Title Transfer Guide'),
        ('TITLE_GUIDE_BC', 'British Columbia Title Transfer Guide'),
        ('TITLE_GUIDE_AB', 'Alberta Title Transfer Guide'),
        ('TITLE_GUIDE_MB', 'Manitoba Title Transfer Guide'),
        ('TITLE_GUIDE_SK', 'Saskatchewan Title Transfer Guide'),
        ('TITLE_GUIDE_NS', 'Nova Scotia Title Transfer Guide'),
        ('TITLE_GUIDE_NB', 'New Brunswick Title Transfer Guide'),
        ('TITLE_GUIDE_NL', 'Newfoundland & Labrador Title Transfer Guide'),
        ('TITLE_GUIDE_PE', 'Prince Edward Island Title Transfer Guide'),
        ('TITLE_GUIDE_NT', 'Northwest Territories Title Transfer Guide'),
        ('TITLE_GUIDE_YT', 'Yukon Title Transfer Guide'),
        ('TITLE_GUIDE_NU', 'Nunavut Title Transfer Guide'),
        ('LIEN_CERTIFICATE', 'PPSA Lien Search Certificate'),
        ('EXPORT_CHECKLIST', 'Export Readiness Checklist'),
        ('BILL_OF_SALE', 'Bill of Sale'),
        ('OTHER', 'Other Document'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Generation'),
        ('GENERATED', 'Generated'),
        ('DELIVERED', 'Delivered to Buyer'),
        ('EXPIRED', 'Expired'),
        ('FAILED', 'Generation Failed'),
    ]
    
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='export_documents',
        verbose_name=_('Vehicle')
    )
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='export_documents',
        verbose_name=_('Buyer')
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_('Document Type')
    )
    
    file = models.FileField(
        upload_to='export_documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png'])],
        null=True,
        blank=True,
        verbose_name=_('Document File')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_('Status')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expires At'),
        help_text=_('Date when document becomes invalid (e.g., CBSA forms valid 30 days)')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Additional information or generation errors')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Export Document')
        verbose_name_plural = _('Export Documents')
        indexes = [
            models.Index(fields=['vehicle', 'document_type']),
            models.Index(fields=['buyer', 'created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.vehicle}"
    
    def is_expired(self):
        """Check if document has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_expired(self):
        """Mark document as expired if past expiration date"""
        if self.is_expired() and self.status != 'EXPIRED':
            self.status = 'EXPIRED'
            self.save(update_fields=['status', 'updated_at'])


class ExportChecklist(models.Model):
    """
    Export readiness checklist for vehicles
    
    Tracks completion of pre-export requirements to ensure smooth transactions.
    """
    
    vehicle = models.OneToOneField(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='export_checklist',
        verbose_name=_('Vehicle')
    )
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='export_checklists',
        verbose_name=_('Buyer')
    )
    
    # Pre-export checklist items
    title_verified = models.BooleanField(
        default=False,
        verbose_name=_('Title Verified'),
        help_text=_('Vehicle title is clear and verified')
    )
    
    lien_checked = models.BooleanField(
        default=False,
        verbose_name=_('Lien Search Completed'),
        help_text=_('PPSA lien search completed with no active liens')
    )
    
    insurance_confirmed = models.BooleanField(
        default=False,
        verbose_name=_('Insurance Confirmed'),
        help_text=_('Export insurance coverage confirmed')
    )
    
    payment_cleared = models.BooleanField(
        default=False,
        verbose_name=_('Payment Cleared'),
        help_text=_('Payment received and cleared')
    )
    
    inspection_completed = models.BooleanField(
        default=False,
        verbose_name=_('Inspection Completed'),
        help_text=_('Third-party inspection completed (if required)')
    )
    
    cbsa_form_generated = models.BooleanField(
        default=False,
        verbose_name=_('CBSA Form 1 Generated'),
        help_text=_('CBSA Form 1 vehicle export declaration generated')
    )
    
    title_guide_provided = models.BooleanField(
        default=False,
        verbose_name=_('Title Guide Provided'),
        help_text=_('Provincial title transfer guide provided to buyer')
    )
    
    export_ready = models.BooleanField(
        default=False,
        verbose_name=_('Export Ready'),
        help_text=_('All checklist items completed, vehicle ready for export')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At'),
        help_text=_('When all checklist items were completed')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Additional notes or issues')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Export Checklist')
        verbose_name_plural = _('Export Checklists')
        indexes = [
            models.Index(fields=['vehicle']),
            models.Index(fields=['buyer', 'export_ready']),
        ]
    
    def __str__(self):
        status = "Ready" if self.export_ready else "Incomplete"
        return f"Export Checklist - {self.vehicle} ({status})"
    
    def check_completion(self):
        """
        Check if all required items are complete and update export_ready status
        """
        required_items = [
            self.title_verified,
            self.lien_checked,
            self.payment_cleared,
            self.cbsa_form_generated,
            self.title_guide_provided,
        ]
        
        all_complete = all(required_items)
        
        if all_complete and not self.export_ready:
            self.export_ready = True
            self.completed_at = timezone.now()
            self.save(update_fields=['export_ready', 'completed_at', 'updated_at'])
        elif not all_complete and self.export_ready:
            self.export_ready = False
            self.completed_at = None
            self.save(update_fields=['export_ready', 'completed_at', 'updated_at'])
        
        return self.export_ready
    
    def get_completion_percentage(self):
        """Calculate percentage of checklist items completed"""
        total_items = 7  # Total number of checklist items
        completed_items = sum([
            self.title_verified,
            self.lien_checked,
            self.insurance_confirmed,
            self.payment_cleared,
            self.inspection_completed,
            self.cbsa_form_generated,
            self.title_guide_provided,
        ])
        
        return int((completed_items / total_items) * 100)
