import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.Investigator import run_investigator
from agents.policy_reasoner import run_policy_reasoner
from agents.Response_drafter import run_response_drafter
from agents.router_agent import run_router


class DisputeState(TypedDict):
    customer_message: str       # the latest message
    conversation_history: list 
    router_decision: str
    investigator_facts: str
    policy_decision: str
    final_response: str

async def router_node(state: DisputeState) -> dict:
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in state["conversation_history"]
    )
    full_context = f"{history_text}\nuser: {state['customer_message']}"
    result = await run_router(full_context)
    if result == "PROCEED":
        return {"router_decision": "proceed"}
    else:
        return {"router_decision": "clarify", "final_response": result}


async def end_early_node(state: DisputeState) -> dict:
    return {}


def route_after_router(state: DisputeState) -> str:
    if state["router_decision"] == "proceed":
        return "investigator"
    return "end_early"


async def investigator_node(state: DisputeState) -> dict:
    facts = await run_investigator(state["customer_message"])
    return {"investigator_facts": facts}


async def policy_reasoner_node(state: DisputeState) -> dict:
    decision = await run_policy_reasoner(
        state["customer_message"],
        state["investigator_facts"]
    )
    return {"policy_decision": decision}


async def response_drafter_node(state: DisputeState) -> dict:
    response = await run_response_drafter(state["policy_decision"])
    return {"final_response": response}


async def human_handoff_node(state: DisputeState) -> dict:
    message = (
        "Thank you for reaching out. Your case requires a closer review by our support team "
        "to ensure we handle it correctly. We'll get back to you within 1-2 business days "
        "with an update. We appreciate your patience.\n\n"
        "Stryde Customer Support Team"
    )
    return {"final_response": message}


def route_after_policy(state: DisputeState) -> str:
    if "ESCALATE" in state["policy_decision"]:
        return "human_handoff"
    return "response_drafter"


graph = StateGraph(DisputeState)

graph.add_node("router", router_node)
graph.add_node("investigator", investigator_node)
graph.add_node("policy_reasoner", policy_reasoner_node)
graph.add_node("response_drafter", response_drafter_node)
graph.add_node("human_handoff", human_handoff_node)
graph.add_node("end_early", end_early_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    route_after_router,
    {
        "investigator": "investigator",
        "end_early": "end_early",
    }
)

graph.add_edge("investigator", "policy_reasoner")

graph.add_conditional_edges(
    "policy_reasoner",
    route_after_policy,
    {
        "response_drafter": "response_drafter",
        "human_handoff": "human_handoff",
    }
)

graph.add_edge("response_drafter", END)
graph.add_edge("human_handoff", END)
graph.add_edge("end_early", END)

app = graph.compile()

async def main():
    result = await app.ainvoke({
        # "customer_message": "My Stryde AirRun Pro shoes (ORD1001) have a strange chemical smell and slight discoloration on the upper after 3 months. Not sure if this counts as a defect or normal wear."
        # "customer_message": "My Stryde AirRun Pro shoes (ORD1001) started separating at the sole after 5 months of regular running use. I want a refund or replacement."
        "customer_message": "I want to return my Stryde AirRun Pro shoes (ORD1001), I've worn them outdoors for 2 weeks and the soles are dirty, I just don't like the fit."
    })
    print("=== FINAL RESPONSE ===")
    print(result["final_response"])
    print()
    print("=== FULL STATE (for debugging) ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

