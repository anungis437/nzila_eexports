import { useState, useEffect, useRef } from 'react';
import { Send, Paperclip, X } from 'lucide-react';
import { useSendMessage } from '../api/chat';

interface MessageInputProps {
  conversationId: number;
}

export default function MessageInput({ conversationId }: MessageInputProps) {
  const [content, setContent] = useState('');
  const [attachment, setAttachment] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const sendMessage = useSendMessage();
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [content]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim() && !attachment) return;
    
    await sendMessage.mutateAsync({
      conversation: conversationId,
      content: content.trim(),
      attachment: attachment || undefined,
    });
    
    setContent('');
    setAttachment(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachment(file);
    }
  };
  
  const removeAttachment = () => {
    setAttachment(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="border-t bg-white p-4">
      {attachment && (
        <div className="mb-2 flex items-center gap-2 rounded bg-gray-100 p-2">
          <Paperclip className="h-4 w-4 text-gray-500" />
          <span className="flex-1 truncate text-sm text-gray-700">{attachment.name}</span>
          <button
            type="button"
            onClick={removeAttachment}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Remove attachment"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
      
      <div className="flex items-end gap-2">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          aria-label="Attach file"
        >
          <Paperclip className="h-5 w-5" />
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          accept="image/*,.pdf,.doc,.docx"
          aria-label="Attach file"
        />
        
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Shift+Enter for new line)"
          className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 max-h-[120px]"
          rows={1}
        />
        
        <button
          type="submit"
          disabled={(!content.trim() && !attachment) || sendMessage.isPending}
          className="rounded-lg bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Send message"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
      
      <p className="mt-1 text-xs text-gray-500">Press Enter to send, Shift+Enter for new line</p>
    </form>
  );
}
