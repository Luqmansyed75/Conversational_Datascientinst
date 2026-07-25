from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from agents  import route, check_sufficiency, run_rag_agent, run_sql_agent, generate_response, run_viz_agent

MAX_ITERATIONS = 3


def router_node(state: AgentState) -> AgentState:
    sql_data    = state.get("sql_data")
    rag_context = state.get("rag_context")
    iteration   = state.get("iteration", 0)

    # Distinguish between "node ran" and "node returned data"
    sql_was_run  = sql_data is not None
    has_sql      = bool(sql_data and sql_data.get("results"))
    has_rag      = bool(rag_context)

    if iteration >= MAX_ITERATIONS:
        curr_intent = "ready"

    elif sql_was_run and not has_sql:
        # SQL ran but returned empty rows — no point retrying
        curr_intent = "ready"

    elif has_rag and has_sql:
        curr_intent = "ready"

    elif has_rag or has_sql:
        # Some data collected — check if it's enough
        curr_intent = check_sufficiency(
            state["question"],
            sql_data,
            rag_context,
        )

    else:
        # First visit — classify intent
        curr_intent = route(state["question"])

    state["intent"]        = curr_intent
    state["iteration"]     = iteration + 1
    state["intent_history"] = list(state.get("intent_history") or []) + [curr_intent]
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

    # One LLM call → returns both answer text + needs_chart decision
    output = generate_response(state["question"], source, data)

    state["final_answer"] = output.answer
    state["needs_chart"]  = output.needs_chart

    state["chat_history"].append({"role": "user",      "content": state["question"]})
    state["chat_history"].append({"role": "assistant",  "content": output.answer})
    return state


def viz_node(state: AgentState) -> AgentState:
    """Runs only when response_node sets needs_chart=True and sql_data exists."""
    fig = run_viz_agent(
        question = state["question"],
        sql_data = state["sql_data"],
    )
    state["chart_figure"] = fig
    return state


def route_edge(state: AgentState) -> str:
    intent = state.get("intent")
    if intent in ("rag", "needs_rag"):
        return "rag"
    elif intent in ("sql", "needs_sql"):
        return "sql"
    else:
        return "response"


def viz_edge(state: AgentState) -> str:
    """Routes to viz_node if chart is needed, otherwise ends."""
    if state.get("needs_chart") :
        return "viz"
    return END


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router",   router_node)
    graph.add_node("rag",      rag_node)
    graph.add_node("sql",      sql_node)
    graph.add_node("response", response_node)
    graph.add_node("viz",      viz_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_edge,
        {"rag": "rag", "sql": "sql", "response": "response"},
    )

    graph.add_edge("rag", "router")
    graph.add_edge("sql", "router")

    # After response: go to viz or end
    graph.add_conditional_edges(
        "response",
        viz_edge,
        {"viz": "viz", END: END},
    )

    graph.add_edge("viz", END)

    return graph.compile()


app = build_graph()


def run(question: str, chat_history: list = []) -> dict:
    state = app.invoke({
        "question":       question,
        "intent":         None,
        "intent_history": [],
        "rag_context":    None,
        "sql_data":       None,
        "final_answer":   None,
        "needs_chart":    None,
        "chart_figure":   None,
        "chat_history":   chat_history,
        "iteration":      0,
    })
    return {
        "answer":        state["final_answer"],
        "needs_chart":   state["needs_chart"],
        "chart_figure":  state["chart_figure"],
        "intent_history": state["intent_history"],
        "sql_res":state["sql_data"]
    }


if __name__ == "__main__":
    tests = [
        "Show me the last 5 months sales of electronics products",
    ]

    for q in tests:
        print(f"\nQ: {q}")
        result = run(q)
        print(f"Answer      : {result['answer']}")
        print(f"Needs chart : {result['needs_chart']}")
        print(f"Has figure  : {result['chart_figure'] is not None}")
        print(f"Intent path : {result['intent_history']}")
        print(f"sql_res : {result['sql_res']}")
        print("-" * 50)