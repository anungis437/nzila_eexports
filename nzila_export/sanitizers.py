"""
Input Sanitization Utilities
Prevents XSS and injection attacks by sanitizing user-generated content
"""
import bleach
from django.utils.html import escape
from django.conf import settings

# Allowed HTML tags for rich text (very restrictive)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(text):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        text: Raw HTML string
        
    Returns:
        Clean HTML string with only allowed tags
    """
    if not text:
        return text
    
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )


def sanitize_plain_text(text):
    """
    Strip all HTML from text and escape special characters
    
    Args:
        text: Raw text string
        
    Returns:
        Plain text with HTML entities escaped
    """
    if not text:
        return text
    
    # Strip all HTML
    clean = bleach.clean(text, tags=[], strip=True)
    
    # Escape remaining special characters
    return escape(clean)


def sanitize_url(url):
    """
    Validate and sanitize URL
    
    Args:
        url: URL string
        
    Returns:
        Clean URL or empty string if invalid
    """
    if not url:
        return ''
    
    # Basic URL validation
    allowed_schemes = ['http', 'https']
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        if parsed.scheme not in allowed_schemes:
            return ''
        
        return url
    except:
        return ''


def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    if not filename:
        return 'unnamed'
    
    # Remove path components
    import os
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    return filename or 'unnamed'
