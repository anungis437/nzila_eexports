import { useConversations } from '../api/chat';
import { Loader2, MessageSquare } from 'lucide-react';
import type { Conversation } from '../api/chat';

interface ConversationListProps {
  selectedConversationId?: number;
  onSelectConversation: (conversationId: number) => void;
}

export default function ConversationList({
  selectedConversationId,
  onSelectConversation,
}: ConversationListProps) {
  const { data: conversations, isLoading } = useConversations();
  
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }
  
  if (!conversations || conversations.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center">
        <MessageSquare className="mb-4 h-12 w-12 text-gray-400" />
        <h3 className="mb-2 text-lg font-medium text-gray-900">No messages yet</h3>
        <p className="text-sm text-gray-500">
          Start a conversation by contacting a dealer about a vehicle
        </p>
      </div>
    );
  }
  
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = diffInMs / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const diffInMins = Math.floor(diffInMs / (1000 * 60));
      return `${diffInMins}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };
  
  return (
    <div className="h-full overflow-y-auto bg-white">
      {conversations.map((conversation: Conversation) => (
        <button
          key={conversation.id}
          onClick={() => onSelectConversation(conversation.id)}
          className={`w-full border-b p-4 text-left transition-colors hover:bg-gray-50 ${
            selectedConversationId === conversation.id ? 'bg-blue-50 hover:bg-blue-50' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 overflow-hidden">
              <div className="flex items-center gap-2">
                <h3 className="font-medium text-gray-900">
                  {conversation.other_participant?.full_name}
                </h3>
                {conversation.unread_count > 0 && (
                  <span className="rounded-full bg-blue-600 px-2 py-0.5 text-xs font-medium text-white">
                    {conversation.unread_count}
                  </span>
                )}
              </div>
              
              {conversation.vehicle_info && (
                <p className="text-xs text-gray-500">
                  {conversation.vehicle_info.year} {conversation.vehicle_info.make}{' '}
                  {conversation.vehicle_info.model}
                </p>
              )}
              
              {conversation.last_message && (
                <p className="mt-1 truncate text-sm text-gray-600">
                  {conversation.last_message.content}
                </p>
              )}
            </div>
            
            {conversation.last_message && (
              <p className="ml-2 text-xs text-gray-500">
                {formatTime(conversation.last_message.created_at)}
              </p>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}
