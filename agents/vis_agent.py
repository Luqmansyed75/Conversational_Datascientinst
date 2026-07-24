import os
import plotly.graph_objects as go
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0,
)

# ── Schema ─────────────────────────────────────────────────────────────────
class ChartInput(BaseModel):
    """LLM fills these fields to describe the chart to render."""
    chart_type : Literal["bar", "pie", "line"] = Field(description="Best chart type for the data.")
    x_label    : str                           = Field(description="X-axis label, e.g. 'Month'.")
    y_label    : str                           = Field(description="Y-axis label, e.g. 'Sales'.")
    title      : str                           = Field(description="Short descriptive chart title.")
    x_values   : list[str]                     = Field(description="X-axis category labels.")
    y_values   : list[float]                   = Field(description="Numeric values for each category.")


# ── System prompt ───────────────────────────────────────────────────────────
VIZ_SYSTEM_PROMPT = """You are a data visualization assistant.
Given a user question and SQL query results, extract the chart parameters.

Rules:
1. Choose EXACTLY ONE chart type:
   - If the user specifies a chart type (bar/line/pie), use that.
   - Use 'line' for time-series or trend data (monthly, yearly, daily).
   - Use 'bar' for category comparisons (top products, cities, etc).
   - Use 'pie' for part-of-whole proportions (share, percentage, distribution).
2. Extract x_values and y_values from the SQL results.
3. Write a short, clear title for the chart."""


# ── Figure builder ─────────────────────────────────────────────────────────
def _build_figure(params: ChartInput) -> go.Figure:
    if params.chart_type == "bar":
        fig = go.Figure(
            go.Bar(x=params.x_values, y=params.y_values, marker_color="steelblue")
        )
        fig.update_layout(xaxis_title=params.x_label, yaxis_title=params.y_label)

    elif params.chart_type == "line":
        fig = go.Figure(
            go.Scatter(
                x=params.x_values, y=params.y_values,
                mode="lines+markers",
                line=dict(color="steelblue", width=3),
                marker=dict(size=8),
            )
        )
        fig.update_layout(xaxis_title=params.x_label, yaxis_title=params.y_label)

    elif params.chart_type == "pie":
        fig = go.Figure(
            go.Pie(labels=params.x_values, values=params.y_values, hole=0.3)
        )

    fig.update_layout(title=params.title, template="plotly_dark", height=450)
    return fig


# ── Main entry point ───────────────────────────────────────────────────────
def run_viz_agent(question: str, sql_data: dict) -> go.Figure:
    """
    Reads the user question + SQL results from state,
    extracts chart params via structured output,
    builds and returns the Plotly figure.

    Args:
        question : original user question
        sql_data : dict with keys 'sql' and 'results' (list of dicts)

    Returns:
        go.Figure — to be stored in state['chart_figure']
    """
    structured_llm = llm.with_structured_output(ChartInput)

    chart_params: ChartInput = structured_llm.invoke([
        SystemMessage(content=VIZ_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"User question: {question}\n"
            f"SQL results: {sql_data.get('results', [])}"
        )),
    ])

    return _build_figure(chart_params)
