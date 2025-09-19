import urllib.parse
from dotenv import load_dotenv
import os, json, asyncio, traceback
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
import httpx


def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )


# ---------- Async Mistral HTTP client (OpenAI-compatible style) ----------
class AsyncMistralClient:
    def __init__(self, api_key: str, base_url: str = "https://api.mistral.ai", model: str = "mistral-large"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = None

    async def _client_obj(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def chat(self, messages, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        client = await self._client_obj()
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise RuntimeError(f"Mistral API error {resp.status_code}: {resp.text}")
        data = resp.json()
        choices = data.get("choices") or []
        if choices:
            first = choices[0]
            if "message" in first and isinstance(first["message"], dict):
                return first["message"].get("content", "")
            if "text" in first:
                return first.get("text", "")
        return data.get("output") or data.get("result") or json.dumps(data)

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# ---------- Model Selection Tool ----------
async def model_selection_tool(task_description: str, dataset_summary: str) -> str:
    """ML model selection assistant tool"""
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_api_url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai")
    mistral_model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    
    if not mistral_api_key:
        return "Error: MISTRAL_API_KEY not configured"
    
    llm = AsyncMistralClient(api_key=mistral_api_key, base_url=mistral_api_url, model=mistral_model)
    
    system_prompt = (
        "You are an ML model selection assistant. Given a short task description and dataset summary, "
        "return JSON with two keys: 'candidates' (list of {name,reason}) and 'recommended' (string)."
        " Keep answers short and machine-parseable."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task: {task_description}\nDataset: {dataset_summary}"},
    ]
    
    try:
        result = await llm.chat(messages, temperature=0.0, max_tokens=512)
        await llm.close()
        return result
    except Exception as e:
        await llm.close()
        return f"Error in model selection: {str(e)}"


async def create_agent(coral_tools, agent_tools):
    coral_tools_description = get_tools_description(coral_tools)
    agent_tools_description = get_tools_description(agent_tools)
    combined_tools = coral_tools + agent_tools
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are a Model Selection Agent interacting with the tools from Coral Server and having your own tools. Your task is to perform model selection instructions coming from any agent. 
            Follow these steps in order:
            1. Call wait_for_mentions from coral tools (timeoutMs: 30000) to receive mentions from other agents.
            2. When you receive a mention, keep the thread ID and the sender ID.
            3. Take 2 seconds to think about the content (instruction) of the message and check if it's related to ML model selection.
            4. If the instruction is for model selection, use the model_selection_tool with the provided task description and dataset summary.
            5. Take 3 seconds and think about the content and see if you have executed the instruction to the best of your ability. Make this your response as "answer".
            6. Use `send_message` from coral tools to send a message in the same thread ID to the sender Id you received the mention from, with content: "answer".
            7. If any error occurs, use `send_message` to send a message in the same thread ID to the sender Id you received the mention from, with content: "error".
            8. Always respond back to the sender agent even if you have no answer or error.
            9. Wait for 2 seconds and repeat the process from step 1.

            These are the list of coral tools: {coral_tools_description}
            These are the list of your tools: {agent_tools_description}"""
        ),
        ("placeholder", "{agent_scratchpad}")
    ])

    model = init_chat_model(
        model=os.getenv("MODEL_NAME", "mistral-small-latest"),
        model_provider=os.getenv("MODEL_PROVIDER", "mistral"),
        api_key=os.getenv("MODEL_API_KEY", os.getenv("MISTRAL_API_KEY")),
        temperature=os.getenv("MODEL_TEMPERATURE", "0.2"),
        max_tokens=os.getenv("MODEL_MAX_TOKENS", "1024"),
        base_url=os.getenv("MODEL_BASE_URL", None)
    )
    agent = create_tool_calling_agent(model, combined_tools, prompt)
    return AgentExecutor(agent=agent, tools=combined_tools, verbose=True, handle_parsing_errors=True)


async def main():
    runtime = os.getenv("CORAL_ORCHESTRATION_RUNTIME", None)
    if runtime is None:
        load_dotenv()

    base_url = os.getenv("CORAL_SSE_URL")
    agentID = os.getenv("CORAL_AGENT_ID")

    coral_params = {
        "agentId": agentID,
        "agentDescription": "ML Model Selection Agent that recommends appropriate machine learning models based on task description and dataset characteristics"
    }

    query_string = urllib.parse.urlencode(coral_params)
    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    print(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    timeout = float(os.getenv("TIMEOUT_MS", "300"))
    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": timeout,
                "sse_read_timeout": timeout,
            }
        }
    )

    print("Model Selection Agent Connection Established")

    coral_tools = await client.get_tools(server_name="coral")
    
    # Create custom agent tools
    agent_tools = [
        Tool(
            name="model_selection_tool",
            func=None,
            coroutine=model_selection_tool,
            description="Select appropriate ML models based on task description and dataset summary. Args: task_description (str), dataset_summary (str)"
        )
    ]

    print(f"Coral tools count: {len(coral_tools)} and agent tools count: {len(agent_tools)}")

    agent_executor = await create_agent(coral_tools, agent_tools)

    while True:
        try:
            print("Starting new agent invocation")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            print("Completed agent invocation, restarting loop")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in agent loop: {str(e)}")
            print(traceback.format_exc())
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
