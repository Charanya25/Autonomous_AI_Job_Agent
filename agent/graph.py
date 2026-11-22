
from langgraph.graph import StateGraph, START, END

from agent.state import JobAgentState

from agent.nodes.load_memory import load_memory
from agent.nodes.scrape import scrape
from agent.nodes.filter import filter_node
from agent.nodes.score import score_node
from agent.nodes.apply import apply_node
from agent.nodes.email import email_node
from agent.nodes.hr_drip import hr_drip_node
from agent.nodes.save_memory import save_memory
from agent.nodes.report import report_node


# --------------------------------------------------
# CONDITIONAL ROUTING
# --------------------------------------------------

def should_continue(state):

    if state.get("errors"):
        return "save_memory"

    if state.get("eligible_jobs", 0) == 0:
        return "save_memory"

    return "score"


# --------------------------------------------------
# BUILD LANGGRAPH WORKFLOW
# --------------------------------------------------

def build_graph():

    workflow = StateGraph(JobAgentState)

    # Register all nine nodes
    workflow.add_node("load_memory", load_memory)
    workflow.add_node("scrape", scrape)
    workflow.add_node("filter", filter_node)
    workflow.add_node("score", score_node)
    workflow.add_node("apply", apply_node)
    workflow.add_node("email", email_node)
    workflow.add_node("hr_drip", hr_drip_node)
    workflow.add_node("save_memory", save_memory)
    workflow.add_node("report", report_node)

    # Main workflow connections
    workflow.add_edge(START, "load_memory")
    workflow.add_edge("load_memory", "scrape")
    workflow.add_edge("scrape", "filter")

    # Conditional routing after filtering
    workflow.add_conditional_edges(
        "filter",
        should_continue,
        {
            "score": "score",
            "save_memory": "save_memory"
        }
    )

    workflow.add_edge("score", "apply")
    workflow.add_edge("apply", "email")
    workflow.add_edge("email", "hr_drip")
    workflow.add_edge("hr_drip", "save_memory")
    workflow.add_edge("save_memory", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# --------------------------------------------------
# COMPILE WORKFLOW AT MODULE LEVEL
# --------------------------------------------------

app = build_graph()


# --------------------------------------------------
# DIRECT EXECUTION TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\nBuilding LangGraph workflow...")

    print("All nine nodes registered successfully.")

    print("\nWorkflow compiled successfully!")

    print("\nWorkflow structure:")
    print(app.get_graph().draw_ascii())
