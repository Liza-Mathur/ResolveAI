import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.sessions import StdioConnection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_PROMPT = """You are the Investigator Agent for Stryde's order dispute resolution system.

Your job: given a customer's message, identify their order and gather all relevant facts
(order status, customer loyalty tier, product details) needed to evaluate their claim.

- If the customer provides an order ID, use get_order_details_tool directly.
- If no order ID is given, use find_orders_by_customer_tool with their name or customer_id
  to find candidate orders, and pick the most likely match based on context clues
  (product mentioned, approximate date, etc.) If multiple equally likely matches exist,
  state clearly that clarification is needed.

Always respond with a clear, structured summary of the facts you found. If you cannot
find the order at all, say so explicitly.
Do NOT discuss policy, refunds, or eligibility. Your ONLY job is to look up and report order facts
"""

async def run_investigator(customer_message: str) -> str:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            llm_with_tools = llm.bind_tools(tools)

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": customer_message},
            ]

            response = await llm_with_tools.ainvoke(messages)

            # if the model wants to call a tool, execute it and feed result back
            while response.tool_calls:
                messages.append(response)
                for call in response.tool_calls:
                    tool = next(t for t in tools if t.name == call["name"])
                    result = await tool.ainvoke(call["args"])
                    messages.append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": call["id"],
                    })
                response = await llm_with_tools.ainvoke(messages)

            return response.content


if __name__ == "__main__":
    result = asyncio.run(run_investigator("My order ORD1001 arrived damaged, I want a refund"))
    print(result)