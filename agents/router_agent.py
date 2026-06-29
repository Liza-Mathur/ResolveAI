from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

ROUTER_SYSTEM_PROMPT = """You are the front-door assistant for Stryde's order dispute resolution system.

Decide if the customer's message contains an actual, specific order issue or claim
(e.g., mentions an order ID, a problem with a product, a request for refund/replacement/warranty)
that is ready to be investigated.

If YES — respond with exactly: PROCEED

If NO (e.g., it's a greeting, vague message, or missing key details like what happened or
which order) — respond with a short, warm, helpful message asking for the specific information
needed (order ID and/or what went wrong). Do NOT prefix this with anything else, just write
the message directly.
"""

async def run_router(customer_message: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": customer_message},
    ]
    response = await llm.ainvoke(messages)
    return response.content.strip()


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_router("Hi, I have an issue"))
    print(result)