"""
Base models with soft delete and audit logging functionality
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """
    Abstract base model with soft delete functionality
    Implements GDPR/PIPEDA compliance requirement for data retention
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted At'),
        help_text=_('Timestamp when this record was soft-deleted')
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name=_('Deleted By')
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Include deleted objects
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """Soft delete this object"""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()
    
    def restore(self):
        """Restore a soft-deleted object"""
        self.deleted_at = None
        self.deleted_by = None
        self.save()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None


class AuditModel(models.Model):
    """
    Abstract base model with audit trail functionality
    Tracks who created/modified records and when
    Required for investor validation and compliance
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('Created By')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('Updated By')
    )
    
    class Meta:
        abstract = True


class AuditLog(models.Model):
    """
    Comprehensive audit log for all critical operations
    Supports Law 25, PIPEDA, and GDPR compliance requirements
    """
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('export', _('Export')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('approve', _('Approve')),
        ('reject', _('Reject')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('User')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('Action')
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name=_('Model Name')
    )
    object_id = models.CharField(
        max_length=100,
        verbose_name=_('Object ID')
    )
    object_repr = models.TextField(
        verbose_name=_('Object Representation')
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Changes'),
        help_text=_('JSON of field changes')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} #{self.object_id}"
