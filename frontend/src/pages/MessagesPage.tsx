import { useState } from 'react';
import { MessageSquare } from 'lucide-react';
import ConversationList from '../components/ConversationList';
import MessageThread from '../components/MessageThread';

export default function MessagesPage() {
  const [selectedConversationId, setSelectedConversationId] = useState<number | undefined>();
  
  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Sidebar - Conversation List */}
      <div className="w-80 border-r">
        <div className="border-b bg-white p-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-gray-600" />
            <h1 className="text-xl font-bold text-gray-900">Messages</h1>
          </div>
        </div>
        
        <ConversationList
          selectedConversationId={selectedConversationId}
          onSelectConversation={setSelectedConversationId}
        />
      </div>
      
      {/* Main Content - Message Thread */}
      <div className="flex-1">
        {selectedConversationId ? (
          <MessageThread conversationId={selectedConversationId} />
        ) : (
          <div className="flex h-full items-center justify-center bg-gray-50">
            <div className="text-center">
              <MessageSquare className="mx-auto mb-4 h-16 w-16 text-gray-400" />
              <h2 className="mb-2 text-xl font-medium text-gray-900">Select a conversation</h2>
              <p className="text-sm text-gray-500">
                Choose a conversation from the left to view messages
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
