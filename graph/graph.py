from langgraph.graph import StateGraph, START, END

from graph.state           import AgentState
from agents.router         import route, check_sufficiency
from agents.rag_agent      import run_rag_agent
from agents.sql_agent      import run_sql_agent
from agents.response_agent import generate_response

MAX_ITERATIONS = 3


def router_node(state: AgentState) -> AgentState:
    has_rag   = bool(state.get("rag_context")) 
    has_sql   = bool(state.get("sql_data"))   
    iteration = state.get("iteration", 0)

    if iteration >= MAX_ITERATIONS:
        curr_intent = "ready"
    elif has_rag and has_sql:
        curr_intent = "ready"
    elif has_rag or has_sql:
        # Some data already collected — check if it's sufficient
        curr_intent = check_sufficiency(
            state["question"],
            state.get("sql_data"),
            state.get("rag_context"),
        )
    else:
        # First visit — classify intent
        curr_intent = route(state["question"])

    state["intent"] = curr_intent
    
    # Safely retrieve/append history
    history = list(state.get("intent_history") or [])
    history.append(curr_intent)
    state["intent_history"] = history

    state["iteration"] = iteration + 1
    return state


def rag_node(state: AgentState) -> AgentState:
    state["rag_context"] = run_rag_agent(state["question"])
    return state


def sql_node(state: AgentState) -> AgentState:
    state["sql_data"] = run_sql_agent(state["question"])
    return state


def response_node(state: AgentState) -> AgentState:
    has_rag = bool(state.get("rag_context"))
    has_sql = bool(state.get("sql_data"))

    if has_rag and has_sql:
        source = "both"
        data   = {"rag_context": state["rag_context"], "sql_data": state["sql_data"]}
    elif has_rag:
        source = "rag"
        data   = state["rag_context"]
    elif has_sql:
        source = "sql"
        data   = state["sql_data"]
    else:
        source = "general"
        data   = None

    state["final_answer"] = generate_response(state["question"], source, data)
    state["chat_history"].append({"role": "user",      "content": state["question"]})
    state["chat_history"].append({"role": "assistant",  "content": state["final_answer"]})
    return state


def route_edge(state: AgentState) -> str:
    intent = state.get("intent")  # intent is a single string now ("sql", "needs_rag", etc.)
    if intent in ("rag", "needs_rag"):
        return "rag"
    elif intent in ("sql", "needs_sql"):
        return "sql"
    else:
        return "response"   # "ready" / "general"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router",   router_node)
    graph.add_node("rag",      rag_node)
    graph.add_node("sql",      sql_node)
    graph.add_node("response", response_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_edge,
        {"rag": "rag", "sql": "sql", "response": "response"},
    )

    # Feedback loop — return to router to check sufficiency
    graph.add_edge("rag", "router")
    graph.add_edge("sql", "router")
    graph.add_edge("response", END)

    return graph.compile()


app = build_graph()

def run(question: str, chat_history: list = []) -> list:
    state = app.invoke({
        "question":       question,
        "intent":         None,
        "intent_history": [],       # Initialized intent_history
        "rag_context":    None,
        "sql_data":       None,
        "final_answer":   None,
        "chat_history":   chat_history,
        "iteration":      0,
    })
    return [state["iteration"], state["rag_context"], state["sql_data"], state["final_answer"], state["intent_history"]]


if __name__ == "__main__":
    tests = [
        "What is the return policy for the category with the highest sales?"
    ]

    for q in tests:
        print(f"\nQ: {q}")
        a = run(q)
        for item in a:
            print(item)
            print("-" * 50)
        print("-" * 50)