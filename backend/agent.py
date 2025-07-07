# ✅ FILE: agent.py
import os
import json
import re
import ast
import dateparser
from datetime import datetime
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_openai import AzureChatOpenAI
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from shopify_tool import get_shopify_data

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.1
)

python_tool = PythonAstREPLTool()

def get_shopify_data_tool(input_data):
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except Exception:
            return {"error": "Invalid input format for get_shopify_data"}
    if not isinstance(input_data, dict):
        return {"error": "Input must be a dict"}
    if input_data.get("method", "GET").upper() != "GET":
        return {"error": "This operation is not permitted. Only GET requests are allowed."}
    try:
        resource = input_data.get('resource', 'orders')
        params = input_data.get('params', {})

        # Limit results to avoid exceeding token limits
        if "limit" not in params:
            params["limit"] = 10  # or 30 — reduce if needed

        store_url = input_data.get('store_url')
        result = get_shopify_data(resource, params, store_url)

        if isinstance(result, list):
            if all(isinstance(item, dict) for item in result):
                return {resource: result}
            else:
                print(f"❌ Unexpected data format in result: {[type(item) for item in result[:2]]}")
                return {"error": "Expected a list of dictionaries but got incorrect data structure."}
        return result

    except Exception as e:
        return {"error": f"Shopify API error: {str(e)}"}

shopify_tool = Tool(
    name="get_shopify_data",
    func=lambda x: get_shopify_data_tool(x),
    description="""
Use this tool to fetch data from a Shopify store. Input must be a JSON object:
{
    "resource": "<orders|products|customers|collections>",
    "params": {...optional query parameters...},
    "store_url": "<your-shop.myshopify.com>"
}
Returns: JSON with the requested data.
"""
)

def extract_date_range(text):
    now = datetime.now()
    parsed_start = dateparser.parse(text, settings={'RELATIVE_BASE': now})
    if parsed_start:
        return {
            "created_at_min": parsed_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "created_at_max": now.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    return {}

def format_orders_brief(orders):
    return "\n".join([
        f"- Order #{o.get('order_number')} - ₹{o.get('total_price')} - {o.get('customer', {}).get('first_name', '')} {o.get('customer', {}).get('last_name', '')}"
        for o in orders[:5]
    ])

# --- MEMORY (Chat History) ---
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- PROMPT TEMPLATE ---
react_prompt = PromptTemplate.from_template("""
You are an intelligent assistant helping analyze a Shopify store. Follow strict ReAct format and never skip any step.

TOOLS:
{tools}

TOOL NAMES: {tool_names}

ALWAYS follow this format:

Question: the input question you must answer
Thought: Think carefully before choosing a tool
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/... as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question, use markdown (no code blocks)

Begin!

Question: {input}
{agent_scratchpad}
""")

# --- AGENT SETUP ---
agent = create_react_agent(
    llm=llm,
    tools=[shopify_tool, python_tool],
    prompt=react_prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[shopify_tool, python_tool],
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    early_stopping_method="force"
)

# --- OUTPUT SANITIZATION ---
def sanitize_output(output):
    # Block code blocks
    if "```" in output:
        return "Sorry, I cannot return code. Here is a summary instead:\n" + re.sub(r"```.*?```", "", output, flags=re.DOTALL)
    # Block unsafe ops
    if re.search(r"\\b(POST|PUT|DELETE)\\b", output, re.IGNORECASE):
        return "This operation is not permitted. Only GET requests are allowed."
    return output

# --- MAIN RUN FUNCTION ---
# --- MAIN RUN FUNCTION ---
def run_agent(question, store_url=None, chat_history=None):
    if not store_url:
        store_url = os.getenv("SHOPIFY_SHOP_NAME", "clevrr-test.myshopify.com")

    # ✅ LIMIT chat history length to avoid token overflow
    MAX_CHAT_HISTORY_LENGTH = 10
    if chat_history and len(chat_history) > MAX_CHAT_HISTORY_LENGTH:
        chat_history = chat_history[-MAX_CHAT_HISTORY_LENGTH:]

    # Add store_url context to the question
    enhanced_question = f"{question}\nStore: {store_url}\nCurrent date: {datetime.now().strftime('%Y-%m-%d')}"
    
    try:
        result = agent_executor.invoke({"input": enhanced_question, "chat_history": chat_history or []})
        output = result['output'] if isinstance(result, dict) and 'output' in result else str(result)
        return sanitize_output(output)
    except Exception as e:
        return f"Error processing request: {str(e)}"



 