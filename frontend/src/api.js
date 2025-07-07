// src/api.js

export async function askAgent(question, storeUrl, chatHistory) {
  const res = await fetch("http://localhost:5000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, store_url: storeUrl, chat_history: chatHistory }),
  });
  if (!res.ok) throw new Error("API error");
  return (await res.json()).response;
}