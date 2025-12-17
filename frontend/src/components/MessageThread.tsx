import { useEffect, useRef } from 'react';
import { useConversation, useMarkConversationAsRead } from '../api/chat';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, Download } from 'lucide-react';
import MessageInput from './MessageInput';

interface MessageThreadProps {
  conversationId: number;
}

export default function MessageThread({ conversationId }: MessageThreadProps) {
  const { user } = useAuth();
  const { data: conversation, isLoading } = useConversation(conversationId);
  const markAsRead = useMarkConversationAsRead();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasMarkedAsRead = useRef(false);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages]);
  
  // Mark conversation as read when opened
  useEffect(() => {
    if (conversation && conversation.unread_count > 0 && !hasMarkedAsRead.current) {
      markAsRead.mutate(conversationId);
      hasMarkedAsRead.current = true;
    }
  }, [conversation, conversationId, markAsRead]);
  
  // Reset hasMarkedAsRead when conversation changes
  useEffect(() => {
    hasMarkedAsRead.current = false;
  }, [conversationId]);
  
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }
  
  if (!conversation) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-500">Conversation not found</p>
      </div>
    );
  }
  
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = diffInMs / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
    }
  };
  
  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b bg-white p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {conversation.other_participant?.full_name || conversation.participant_1_info?.full_name || conversation.participant_2_info?.full_name}
            </h2>
            {conversation.vehicle_info && (
              <p className="text-sm text-gray-600">
                {conversation.vehicle_info.year} {conversation.vehicle_info.make} {conversation.vehicle_info.model}
              </p>
            )}
          </div>
          {conversation.other_participant?.role && (
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
              {conversation.other_participant.role}
            </span>
          )}
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 space-y-4 overflow-y-auto bg-gray-50 p-4">
        {conversation.messages && conversation.messages.length > 0 ? (
          conversation.messages.map((message) => {
            const isOwnMessage = message.sender === user?.id;
            
            return (
              <div
                key={message.id}
                className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[70%] ${isOwnMessage ? 'text-right' : 'text-left'}`}>
                  <div
                    className={`inline-block rounded-lg px-4 py-2 ${
                      isOwnMessage
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-900 shadow-sm'
                    }`}
                  >
                    {!isOwnMessage && (
                      <p className="mb-1 text-xs font-medium opacity-75">
                        {message.sender_name}
                      </p>
                    )}
                    
                    <p className="whitespace-pre-wrap break-words">{message.content}</p>
                    
                    {message.attachment_url && (
                      <div className="mt-2">
                        <a
                          href={message.attachment_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`flex items-center gap-1 text-sm underline ${
                            isOwnMessage ? 'text-blue-100' : 'text-blue-600'
                          }`}
                        >
                          <Download className="h-3 w-3" />
                          <span>Attachment</span>
                        </a>
                      </div>
                    )}
                  </div>
                  
                  <p
                    className={`mt-1 text-xs text-gray-500 ${
                      isOwnMessage ? 'text-right' : 'text-left'
                    }`}
                  >
                    {formatTime(message.created_at)}
                    {isOwnMessage && message.is_read && ' · Read'}
                  </p>
                </div>
              </div>
            );
          })
        ) : (
          <div className="flex h-full items-center justify-center">
            <p className="text-gray-500">No messages yet. Start the conversation!</p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <MessageInput conversationId={conversationId} />
    </div>
  );
}
