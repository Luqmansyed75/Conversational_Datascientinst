from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from db.checkpoint import checkpointer

from graph.state import AgentState
from agents  import route, check_sufficiency, run_rag_agent, run_sql_agent, generate_response, run_viz_agent

MAX_ITERATIONS = 3


def router_node(state: AgentState) -> dict:
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

    # Return only fields this node modifies
    return {
        "intent":        curr_intent,
        "iteration":     iteration + 1,
        "intent_history": list(state.get("intent_history") or []) + [curr_intent],
    }



def rag_node(state: AgentState) -> dict:
    return {"rag_context": run_rag_agent(state["question"])}


def sql_node(state: AgentState) -> dict:
    return {"sql_data": run_sql_agent(
        question     = state["question"],
        chat_history = state.get("chat_history", []),
    )}


def response_node(state: AgentState) -> dict:
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
    # Pass chat_history so LLM sees previous conversation turns
    output = generate_response(
        state["question"],
        source,
        data,
        chat_history=state.get("chat_history", []),
    )

    # Return new messages — add_messages reducer appends them to existing history
    return {
        "final_answer": output.answer,
        "needs_chart":  output.needs_chart,
        "chat_history": [
            HumanMessage(content=state["question"]),
            AIMessage(content=output.answer),
        ],
    }


def viz_node(state: AgentState) -> dict:
    """Runs only when response_node sets needs_chart=True and sql_data exists."""
    fig = run_viz_agent(
        question = state["question"],
        sql_data = state["sql_data"],
    )
    # Serialize to JSON string — go.Figure is not msgpack serializable
    return {"chart_figure": fig.to_json() if fig else None}


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

    return graph.compile(checkpointer=checkpointer)


app = build_graph()


def run(question: str, thread_id: str, chat_history: list = []) -> dict:
    config = {"configurable": {"thread_id": thread_id}}

    # chat_history uses add_messages reducer — passing [] appends nothing,
    # checkpointer automatically restores existing history for this thread_id
    state = app.invoke({
        "question":       question,
        "intent":         None,
        "intent_history": [],
        "rag_context":    None,
        "sql_data":       None,
        "final_answer":   None,
        "needs_chart":    None,
        "chart_figure":   None,
        "chat_history":   [],
        "iteration":      0,
    }, config=config)
    return {
        "answer":         state["final_answer"],
        "needs_chart":    state["needs_chart"],
        "has_chart":      state["chart_figure"] is not None,
        "chart_figure":   state["chart_figure"],
        "intent_history": state["intent_history"],
        "sql_res":        state["sql_data"],
        "chat_history":   state["chat_history"],
    }


if __name__ == "__main__":
    # Use the same thread_id across questions to test multi-turn memory
    thread_id = "test-thread-6"
    tests = [
        "What are the top 3 selling products?",
        "And add the total cost of these products?",
        # "What was the total revenue for last quarter?",
        # "Can you compare that to the previous quarter?",
        # "What are the top 5 customers by revenue?",
        # "Can you show me a chart of their purchase history?",
        # "What is the average order value for these customers?",
        # "Can you provide a summary of the sales performance for this year?",
    ]

    for q in tests:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print(f"{'='*60}")
        result = run(q, thread_id=thread_id)
        print(f"Answer       : {result['answer']}")
        # print(f"Needs chart  : {result['needs_chart']}")
        # print(f"Has chart    : {result['has_chart']}")
        # print(f"Intent path  : {result['intent_history']}")
        #print(f"SQL results  : {result['sql_res']}")
        print(f"Chat history : {result['chat_history']}")
        # print(f"Chart JSON   : {'<present>' if result['chart_figure'] else None}")