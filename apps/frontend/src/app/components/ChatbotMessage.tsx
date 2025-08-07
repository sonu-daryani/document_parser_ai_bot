import React, { useState, useEffect } from 'react';

type ChatMessageProps = {
  text: string;
  isUser: boolean;
  image?: string;
  isLoading?: boolean;
};

// Custom Typewriter Hook
const useTypewriter = (text: string, delay: number = 30) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!text) return;

    setDisplayedText('');
    setIsTyping(true);
    let index = 0;

    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, delay);

    return () => clearInterval(timer);
  }, [text, delay]);

  return { displayedText, isTyping };
};

// Loading dots component
const LoadingDots = () => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center gap-1 text-gray-500">
      <span>Thinking</span>
      <span className="w-6 text-left">{dots}</span>
    </div>
  );
};

const ChatMessage: React.FC<ChatMessageProps> = ({ text, isUser, image, isLoading = false }) => {
  const { displayedText, isTyping } = useTypewriter(text, 30);

  return (
    <div className="w-full px-4 py-2">
      <div className={`flex gap-3 items-end ${isUser ? 'justify-end' : 'justify-start'}`}> 
        {/* Bot Avatar - Left side */}
        {!isUser && (
          <div className="flex-shrink-0">
            {image ? (
              <img src={image} alt="Bot" className="w-8 h-8 rounded-full object-cover" />
            ) : (
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
        )}

        {/* Message Bubble */}
        <div className={`max-w-xs sm:max-w-md lg:max-w-lg px-4 py-3 rounded-2xl shadow-sm whitespace-pre-line break-words ${
          isUser 
            ? 'bg-blue-500 text-white rounded-br-sm' 
            : 'bg-gray-100 text-gray-800 rounded-bl-sm border border-gray-200'
        }`}>
          {isUser ? (
            <p className="text-sm leading-relaxed">{text}</p>
          ) : (
            <div className="text-sm leading-relaxed">
              {isLoading ? (
                <LoadingDots />
              ) : (
                <div>
                  <span>{displayedText}</span>
                  {isTyping && (
                    <span className="inline-block w-0.5 h-4 bg-gray-600 animate-pulse ml-1"></span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* User Avatar - Right side */}
        {isUser && (
          <div className="flex-shrink-0">
            {image ? (
              <img src={image} alt="User" className="w-8 h-8 rounded-full object-cover" />
            ) : (
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;