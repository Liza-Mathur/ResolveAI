import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are the Policy Reasoner Agent for Stryde's order dispute resolution system.

You receive: (1) the customer's original claim/message, and (2) structured facts about
their order (status, products, customer loyalty tier) gathered by the Investigator agent.

Your job:
1. Determine what type of claim this is (e.g., damaged item, return request, warranty issue, wrong item).
2. Use search_policy_tool to retrieve the relevant policy text. Use the source_filter parameter
   ('returns_policy.md' or 'warranty_policy.md') if you are confident which policy applies;
   otherwise search without a filter.
3. Reason carefully using ONLY the retrieved policy text and the order facts to decide:
   APPROVED, DENIED, or ESCALATE.

IMPORTANT: If the customer's claim describes a situation, symptom, or issue that is not
clearly and explicitly addressed by the retrieved policy text — even partially — you MUST
choose ESCALATE rather than guessing or matching to the closest-sounding rule. Do not deny
or approve a claim based on partial similarity to an exclusion or inclusion; only do so if
the policy text explicitly and fully covers the situation described. When in doubt, ESCALATE.

4. Justify your decision by citing the specific policy rule that applies, or explain clearly
   why escalation is needed if the policy does not address the situation.

Respond in this format:
DECISION: [APPROVED / DENIED / ESCALATE]
REASONING: [clear explanation citing the specific policy rule, or explaining the ambiguity]
"""

async def run_policy_reasoner(customer_message: str, investigator_facts: str) -> str:
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            llm_with_tools = llm.bind_tools(tools)

            user_content = f"""Customer claim: {customer_message}

Order facts from Investigator:
{investigator_facts}
"""

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ]

            response = await llm_with_tools.ainvoke(messages)

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
    fake_facts = """
    Order ORD1001 - Status: Delivered
    Customer: Aarav Mehta, Loyalty Tier: Gold
    Products: Stryde AirRun Pro (Running Shoes), Stryde ProSock 3-Pack (Accessories)
    """
    result = asyncio.run(run_policy_reasoner(
        "My order ORD1001 arrived damaged, I want a refund",
        fake_facts
    ))
    print(result)