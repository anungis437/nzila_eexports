"""
HTML Sanitization Utilities
Prevents XSS attacks by cleaning user-generated HTML content.
"""
import bleach
from typing import Optional


# Allowed HTML tags for rich text content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
]

# Allowed attributes for specific tags
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'span': ['class'],
    'code': ['class'],
}

# Allowed protocols for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(text: Optional[str], strip: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        text: HTML content to sanitize
        strip: If True, removes all HTML tags. If False, keeps allowed tags.
        
    Returns:
        Sanitized HTML string
        
    Example:
        >>> sanitize_html('<script>alert("XSS")</script><p>Hello</p>')
        '&lt;script&gt;alert("XSS")&lt;/script&gt;<p>Hello</p>'
        
        >>> sanitize_html('<p>Hello</p>', strip=True)
        'Hello'
    """
    if not text:
        return ''
    
    if strip:
        # Strip all HTML tags
        return bleach.clean(text, tags=[], strip=True)
    
    # Clean HTML, keeping only allowed tags and attributes
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Strip disallowed tags instead of escaping
    )
    
    return cleaned


def sanitize_text(text: Optional[str]) -> str:
    """
    Sanitize plain text by stripping all HTML tags.
    
    Args:
        text: Text content that may contain HTML
        
    Returns:
        Plain text with all HTML removed
        
    Example:
        >>> sanitize_text('<b>Hello</b> <script>alert(1)</script>')
        'Hello alert(1)'
    """
    return sanitize_html(text, strip=True)


def validate_url(url: Optional[str]) -> bool:
    """
    Validate that a URL uses an allowed protocol.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is safe, False otherwise
        
    Example:
        >>> validate_url('https://example.com')
        True
        
        >>> validate_url('javascript:alert(1)')
        False
    """
    if not url:
        return False
    
    url_lower = url.lower().strip()
    
    # Check for allowed protocols
    for protocol in ALLOWED_PROTOCOLS:
        if url_lower.startswith(f'{protocol}:'):
            return True
    
    # Check for protocol-relative URLs (//example.com)
    if url_lower.startswith('//'):
        return True
    
    # Check for relative URLs (/path or path)
    if not ':' in url_lower.split('/')[0]:
        return True
    
    return False
