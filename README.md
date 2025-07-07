# 🛍️ Shopify AI Agent — Fullstack LangChain Project

This project is a fullstack AI-powered assistant built using **LangChain**, **Flask**, and **React**, designed to intelligently analyze a Shopify store's data using the **Shopify Admin REST API** (GET-only). It can answer natural language questions about orders, products, and customers using real-time data.

---

## 🚀 Features

- 🔗 Connects to real Shopify Admin REST API (GET-only)
- 🧠 LangChain ReAct Agent with memory and reasoning
- 📊 Provides summaries, tables, and (optional) charts
- 🧰 Uses custom tools: Shopify API + Python REPL for logic
- 🖥️ Full frontend chat interface using React
- 🧾 Returns Markdown-formatted responses

---

## 🧠 Agent Prompt Used

You are an intelligent assistant helping analyze a Shopify store. Follow strict ReAct format and never skip any step.

**TOOLS:**  
{tools}

**TOOL NAMES:**  
{tool_names}

**ALWAYS follow this format:**
```
Question: the input question you must answer
Thought: Think carefully before choosing a tool
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/... as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question, use markdown (no code blocks)
```
Begin!

Question: {input}  
{agent_scratchpad}

---

## 🧱 Project Architecture

```
.
├── backend/
│   ├── app.py              # Flask app (API endpoint)
│   ├── agent.py            # LangChain agent setup and executor
│   ├── shopify_tool.py     # Custom GET-only tool with retry, pagination
│   └── .env                # (ignored) Shopify and Azure credentials
│
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React frontend with chat UI
│   │   ├── api.js          # Function to send chat requests to backend
│   │   └── App.css         # Basic styling
│
├── requirements.txt        # Python dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 🔧 Backend (Flask + LangChain)

1. **Create a virtual environment:**
   - Mac/Linux:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file inside `backend/`:**
   ```ini
   SHOPIFY_SHOP_NAME=clevrr-test.myshopify.com
   SHOPIFY_ACCESS_TOKEN=your_token_here
   SHOPIFY_API_VERSION=2025-07

   AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_azure_api_key
   AZURE_OPENAI_API_VERSION=2023-07-01-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-35
   ```

4. **Run the backend:**
   ```bash
   cd backend
   python app.py
   ```

---

### 🌐 Frontend (React)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the React development server:**
   ```bash
   npm start
   ```

3. **Open your browser at:**  
   [http://localhost:3000](http://localhost:3000)

---

## 💬 Sample Questions Supported

- How many orders were placed in the last 7 days?
- Which products sold the most last month?
- Show a table of revenue by city.
- Who are my repeat customers?
- What is the AOV (Average Order Value) trend this month?
- (Bonus) Plot a graph of order volume over the past 4 weeks.

---

## 🧪 Tools Used

| Tool Name           | Purpose                                         |
|---------------------|-------------------------------------------------|
| get_shopify_data    | Custom tool for GET-only Shopify API access     |
| PythonAstREPLTool   | Used for reasoning, aggregation, and charts     |

---

## 📝 Notes

- The frontend is bootstrapped with [Create React App](https://github.com/facebook/create-react-app).
- If deploying, update the API URL in `frontend/src/api.js` as needed.
- The backend and frontend must both be running for the chat to function.
- All environment variables are required for the backend to function properly.

---

## 📄 License

MIT