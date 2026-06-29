import asyncio
import streamlit as st
from graph import app as resolve_graph

st.set_page_config(page_title="ResolveAI - Stryde Dispute Resolution", page_icon="🛠️")

st.title("🛠️ ResolveAI")
st.caption("Stryde's AI-powered order dispute resolution assistant")

if "history" not in st.session_state:
    st.session_state.history = []

for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

user_input = st.chat_input("Describe your order issue...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Investigating your case..."):
            result = asyncio.run(resolve_graph.ainvoke({
                "customer_message": user_input,
                "conversation_history": st.session_state.history,
            }))
            
            final_response = result["final_response"]

            with st.expander("See reasoning (debug)"):
                st.markdown(f"**Facts gathered:**\n{result.get('investigator_facts', '')}")
                st.markdown(f"**Policy decision:**\n{result.get('policy_decision', '')}")

            st.markdown(final_response)

    st.session_state.history.append({"role": "assistant", "content": final_response})