from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage

class ChatState(TypedDict):
    messages: List[BaseMessage]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

def chatbot_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

graph = StateGraph(ChatState)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")
app = graph.compile()

state = {"messages": []}
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye 👋")
        break
    state["messages"].append(HumanMessage(content=user_input))
    state = app.invoke(state)
    print("Bot:", state["messages"][-1].content)

