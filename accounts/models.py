from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('dealer', _('Dealer')),
        ('broker', _('Broker')),
        ('buyer', _('Buyer')),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='buyer',
        verbose_name=_('Role')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Company Name')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Address')
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Country')
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=[('en', 'English'), ('fr', 'Français')],
        default='en',
        verbose_name=_('Preferred Language')
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_dealer(self):
        return self.role == 'dealer'
    
    def is_broker(self):
        return self.role == 'broker'
    
    def is_buyer(self):
        return self.role == 'buyer'
