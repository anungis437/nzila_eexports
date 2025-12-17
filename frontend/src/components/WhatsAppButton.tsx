import React from 'react';
import { MessageCircle } from 'lucide-react';

interface WhatsAppButtonProps {
  phoneNumber: string;
  message?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'icon' | 'button';
}

const WhatsAppButton: React.FC<WhatsAppButtonProps> = ({
  phoneNumber,
  message = '',
  className = '',
  size = 'md',
  variant = 'button',
}) => {
  const handleClick = () => {
    // Clean phone number (remove spaces, dashes, etc.)
    const cleanPhone = phoneNumber.replace(/[^\d+]/g, '');
    
    // Encode message for URL
    const encodedMessage = encodeURIComponent(message);
    
    // Create WhatsApp URL
    const whatsappUrl = `https://wa.me/${cleanPhone}${encodedMessage ? `?text=${encodedMessage}` : ''}`;
    
    // Open in new window
    window.open(whatsappUrl, '_blank', 'noopener,noreferrer');
  };

  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  if (variant === 'icon') {
    return (
      <button
        onClick={handleClick}
        className={`inline-flex items-center justify-center bg-[#25D366] hover:bg-[#20BA5A] text-white rounded-full p-2 transition-colors ${className}`}
        title="Contact via WhatsApp"
      >
        <MessageCircle className={iconSizes[size]} />
      </button>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center gap-2 bg-[#25D366] hover:bg-[#20BA5A] text-white rounded-lg font-medium transition-colors ${sizeClasses[size]} ${className}`}
    >
      <MessageCircle className={iconSizes[size]} />
      WhatsApp
    </button>
  );
};

export default WhatsAppButton;
