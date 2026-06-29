import asyncio
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are the Response Drafter Agent for Stryde's order dispute resolution system.

You receive a decision (APPROVED / DENIED / ESCALATE) and the reasoning behind it from the
Policy Reasoner agent. Your job is to write a clear, warm, professional customer-facing
message communicating this outcome.

Guidelines:
- If APPROVED: confirm next steps clearly (refund/replacement process, expected timeline).
- If DENIED: explain why politely and clearly, citing the relevant policy in plain language
  (not legal/robotic tone), and offer any alternative if one exists.
- If ESCALATE: let the customer know their case needs further review by the support team,
  with an expected timeframe, without overpromising an outcome.
- Never sound robotic or overly formal. Be empathetic, clear, and concise.
- Do not invent details (tracking numbers, exact dates) that weren't provided.
"""

async def run_response_drafter(decision_and_reasoning: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": decision_and_reasoning},
    ]

    response = await llm.ainvoke(messages)
    return response.content


if __name__ == "__main__":
    fake_decision = """
DECISION: APPROVED
REASONING: According to the returns policy, if a customer receives a damaged item, they must
email support within 48 hours of delivery, including the order number and photos. Stryde will
then arrange an immediate replacement or full refund at no cost to the customer.
"""
    result = asyncio.run(run_response_drafter(fake_decision))
    print(result)