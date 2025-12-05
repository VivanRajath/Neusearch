import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Maximize2, Minimize2 } from 'lucide-react';
import config from '../config';

const ChatInterface = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [messages, setMessages] = useState([
        { text: "Hi! I'm your AI shopping assistant. Looking for something specific?", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            // Call backend API
            const response = await fetch(`${config.API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMessage.text })
            });
            const data = await response.json();

            // Assuming the backend returns { answer: "...", recommendations: [...] }
            // Adjust based on actual RAG response structure
            const botMessage = {
                text: data.answer || "Here are some recommendations based on your query.",
                sender: 'bot',
                recommendations: data.recommendations || []
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { text: "Sorry, I encountered an error. Please try again.", sender: 'bot' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-interface">
            {!isOpen && (
                <button className="chat-toggle" onClick={() => setIsOpen(true)}>
                    <MessageCircle size={24} />
                </button>
            )}

            {isOpen && (
                <div className={`chat-window ${isFullscreen ? 'fullscreen' : ''}`}>
                    <div className="chat-header">
                        <h3>AI Assistant</h3>
                        <div className="chat-header-actions">
                            <button onClick={() => setIsFullscreen(!isFullscreen)} title={isFullscreen ? "Minimize" : "Fullscreen"}>
                                {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
                            </button>
                            <button onClick={() => setIsOpen(false)}><X size={20} /></button>
                        </div>
                    </div>

                    <div className="chat-messages">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`message ${msg.sender}`}>
                                <div className="message-content">
                                    <p dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br />') }}></p>

                                    {msg.recommendations && msg.recommendations.length > 0 && (
                                        <div className="recommendations">
                                            {msg.recommendations.map((rec, rIdx) => (
                                                <a
                                                    key={rIdx}
                                                    href={rec.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="mini-product-card"
                                                >
                                                    <img src={rec.image_url} alt={rec.title} />
                                                    <p>{rec.title}</p>
                                                </a>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && <div className="message bot"><p>Thinking...</p></div>}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chat-input">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder="Ask for recommendations..."
                            rows="1"
                        />
                        <button onClick={handleSend} disabled={loading}>
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;
