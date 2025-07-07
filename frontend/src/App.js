// src/App.js

import React, { useState } from "react";
import { askAgent } from "./api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

function App() {
  const [storeUrl, setStoreUrl] = useState("");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setChat([...chat, { role: "user", text: input }]);
    setLoading(true);
    try {
      const response = await askAgent(input, storeUrl, chat.map(m => m.text));
      setChat(c => [...c, { role: "agent", text: response }]);
    } catch (e) {
      setChat(c => [...c, { role: "agent", text: "Error: " + e.message }]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <h2 className="title">🛍️ Shopify AI Agent</h2>

      <input
        value={storeUrl}
        onChange={e => setStoreUrl(e.target.value)}
        placeholder="Enter Shopify store URL"
        className="store-input"
      />

      <div className="chat-box">
        {chat.map((msg, i) => (
          <div
            key={i}
            className={`chat-message ${msg.role === "user" ? "user" : "agent"}`}
          >
            <div className="message-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.text}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && <div className="loading">🤖 Agent is thinking...</div>}
      </div>

      <form
        className="input-area"
        onSubmit={e => {
          e.preventDefault();
          sendMessage();
        }}
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          ➤
        </button>
      </form>
    </div>
  );
}

export default App;
