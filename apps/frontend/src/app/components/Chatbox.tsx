
type ChatboxProps = {
  isUploading: boolean;
  className?: string;
};

type Message = {
  text: string;
  isUser: boolean;
};

type ChatMessageProps = {
  text: string;
  isUser: boolean;
  image: string;
  isLoading?: boolean;
};

import axios from 'axios';
import { useEffect, useState } from 'react';

// Circular loader component with Tailwind
const CircularLoader = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-8 text-center py-12">
      <h2 className="text-xl font-semibold text-gray-700">
        Please wait while we are embedding your file
      </h2>
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );
};

// Send Icon Component
const SendIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.429a1 1 0 001.17-1.409l-7-14z" />
  </svg>
);

// User Avatar Component
const UserAvatar = () => (
  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
    </svg>
  </div>
);

// Bot Avatar Component
const BotAvatar = () => (
  <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center flex-shrink-0">
    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
    </svg>
  </div>
);

// Chat Message Component
const ChatMessage: React.FC<ChatMessageProps> = ({ text, isUser, image, isLoading = false }) => {
  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <BotAvatar />}
      
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-500 text-white rounded-br-none' 
          : 'bg-gray-200 text-gray-800 rounded-bl-none'
      }`}>
        {isLoading && !isUser ? (
          <div className="flex items-center gap-2">
            <div className="animate-pulse">Thinking...</div>
            <div className="flex gap-1">
              <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce"></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
            </div>
          </div>
        ) : (
          <p className="text-sm">{text}</p>
        )}
      </div>
      
      {isUser && <UserAvatar />}
    </div>
  );
};


const Chatbox = ({ isUploading, className }: ChatboxProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // You may want to get user_id from context or props in a real app
  const user_id = localStorage.getItem('user_id') || 'xyz123';

  // Load messages from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('chat_conversation');
    if (stored) {
      try {
        setMessages(JSON.parse(stored));
      } catch {
        setMessages([]);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chat_conversation', JSON.stringify(messages));
  }, [messages]);

  const handleUserInput = async () => {
    if (!userInput.trim()) return;
    const userMsg: Message = { text: userInput, isUser: true };
    setMessages((prev: Message[]) => [...prev, userMsg]);
    setIsLoading(true);
    setUserInput("");
    try {
      const response = await axios.post('/api/chat', {
        query: userInput,
        user_id: user_id
      });
      const botMsg: Message = { text: response.data.answer, isUser: false };
      setMessages((prev: Message[]) => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
      setMessages((prev: Message[]) => [...prev, { text: "Something went wrong!", isUser: false }]);
    }
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleUserInput();
    }
  };

  return (
    <div className={`w-full max-w-4xl mx-auto bg-white rounded-xl shadow-lg ${className || ''}`}>
      <div className="text-center py-8 border-b border-gray-200">
        <h1 className="text-3xl font-bold text-blue-800">Chat Box</h1>
      </div>
      
      {isUploading ? (
        <CircularLoader />
      ) : (
        <div className="flex flex-col overflow-y-auto h-screen max-h-[80vh]">
          {/* Chat Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && !isLoading && (
              <div className="text-center text-gray-500 py-8">
                <p>Ask a question about your uploaded PDF document</p>
              </div>
            )}
            {messages.map((msg: Message, idx: number) => (
              <ChatMessage key={idx} text={msg.text} isUser={msg.isUser} image="" />
            ))}
            {isLoading && (
              <ChatMessage text="" isUser={false} image="" isLoading={true} />
            )}
          </div>
          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex gap-3">
              <input
                onChange={(e) => setUserInput(e.target.value)}
                value={userInput}
                onKeyPress={handleKeyPress}
                type="text"
                placeholder="Enter your question"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                onClick={handleUserInput}
                disabled={isLoading || !userInput.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
              >
                Send
                <SendIcon />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbox;