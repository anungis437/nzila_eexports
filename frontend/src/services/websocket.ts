/**
 * WebSocket Service for Real-Time Chat
 * 
 * This service handles WebSocket connections for real-time messaging.
 * It provides automatic reconnection, message queuing, and event handling.
 */

export interface ChatMessage {
  type: 'message' | 'typing' | 'read' | 'status' | 'connection_established' | 'error';
  message_id?: number;
  sender_id?: number;
  sender_name?: string;
  content?: string;
  timestamp?: string;
  is_read?: boolean;
  is_typing?: boolean;
  user_id?: number;
  user_name?: string;
  status?: 'online' | 'offline';
  message_ids?: number[];
  reader_id?: number;
  conversation_id?: string;
  message?: string;
}

type MessageHandler = (message: ChatMessage) => void;
type ConnectionHandler = () => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private conversationId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private messageQueue: any[] = [];
  private messageHandlers: MessageHandler[] = [];
  private connectionHandlers: ConnectionHandler[] = [];
  private disconnectionHandlers: ConnectionHandler[] = [];
  private isIntentionallyClosed = false;
  
  /**
   * Connect to WebSocket for a conversation
   */
  connect(conversationId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Already connected');
      return;
    }
    
    this.conversationId = conversationId;
    this.isIntentionallyClosed = false;
    
    // Determine WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/chat/${conversationId}/`;
    
    console.log('[WebSocket] Connecting to:', wsUrl);
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => this.handleOpen();
      this.ws.onmessage = (event) => this.handleMessage(event);
      this.ws.onerror = (error) => this.handleError(error);
      this.ws.onclose = (event) => this.handleClose(event);
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.scheduleReconnect();
    }
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    console.log('[WebSocket] Disconnecting');
    this.isIntentionallyClosed = true;
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.reconnectAttempts = 0;
  }
  
  /**
   * Send a chat message
   */
  sendMessage(content: string) {
    if (!content.trim()) {
      return;
    }
    
    const message = {
      type: 'message',
      message: content.trim(),
    };
    
    this.send(message);
  }
  
  /**
   * Send typing indicator
   */
  sendTyping(isTyping: boolean) {
    const message = {
      type: 'typing',
      is_typing: isTyping,
    };
    
    this.send(message);
  }
  
  /**
   * Send read receipt
   */
  sendReadReceipt(messageIds: number[]) {
    if (messageIds.length === 0) {
      return;
    }
    
    const message = {
      type: 'read',
      message_ids: messageIds,
    };
    
    this.send(message);
  }
  
  /**
   * Add message handler
   */
  onMessage(handler: MessageHandler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }
  
  /**
   * Add connection handler
   */
  onConnect(handler: ConnectionHandler) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }
  
  /**
   * Add disconnection handler
   */
  onDisconnect(handler: ConnectionHandler) {
    this.disconnectionHandlers.push(handler);
    return () => {
      this.disconnectionHandlers = this.disconnectionHandlers.filter(h => h !== handler);
    };
  }
  
  /**
   * Check if connected
   */
  isConnected() {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
  
  // Private methods
  
  private send(message: any) {
    if (this.isConnected()) {
      this.ws!.send(JSON.stringify(message));
    } else {
      console.log('[WebSocket] Queueing message (not connected)');
      this.messageQueue.push(message);
    }
  }
  
  private handleOpen() {
    console.log('[WebSocket] Connected');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    
    // Send queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
    
    // Notify connection handlers
    this.connectionHandlers.forEach(handler => handler());
  }
  
  private handleMessage(event: MessageEvent) {
    try {
      const data: ChatMessage = JSON.parse(event.data);
      console.log('[WebSocket] Message received:', data.type);
      
      // Notify all message handlers
      this.messageHandlers.forEach(handler => handler(data));
    } catch (error) {
      console.error('[WebSocket] Failed to parse message:', error);
    }
  }
  
  private handleError(error: Event) {
    console.error('[WebSocket] Error:', error);
  }
  
  private handleClose(event: CloseEvent) {
    console.log('[WebSocket] Closed:', event.code, event.reason);
    this.ws = null;
    
    // Notify disconnection handlers
    this.disconnectionHandlers.forEach(handler => handler());
    
    // Attempt to reconnect if not intentionally closed
    if (!this.isIntentionallyClosed) {
      this.scheduleReconnect();
    }
  }
  
  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    
    // Exponential backoff
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.conversationId && !this.isIntentionallyClosed) {
        this.connect(this.conversationId);
      }
    }, delay);
  }
}

// Singleton instance
export const websocketService = new WebSocketService();
