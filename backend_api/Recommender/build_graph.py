from backend_api.Recommender.agents.agents import Agents
from backend_api.Recommender.rag.search_engine import SearchEngine
from backend_api.Recommender.functionalNodes.create_controller_graph import create_controller_graph
from backend_api.Recommender.states import OverallState

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# Supervisor decides when the analysis is ready for graph generation
def supervisor_edge(state: OverallState):
    last_message = state.get("supervisor_comment", "")
    if "CONTINUE" in last_message:
        return "create_controller_graph"
    return "control_loop_analyser"


# Human-in-the-loop decision logic
def choose_rag_pipeline(state: OverallState):
    # This key will be populated by the UI during the interrupt (or automatically if bypassed)
    rag_decision = state.get("RAG_decision", {})
    if "Flag" in rag_decision:
        if "BLOCK_DIAGRAM_SEARCH" in rag_decision["Flag"]:
            rag_decision["Flag"].remove("BLOCK_DIAGRAM_SEARCH")
            state["RAG_decision"] = rag_decision
            return "block_diagram_search"
        elif "OPENAI_WEB_SEARCH" in rag_decision["Flag"]:
            rag_decision["Flag"].remove("OPENAI_WEB_SEARCH")
            state["RAG_decision"] = rag_decision
            return "openai_web_search"
    return "end"


def check_human_intervention_condition(state: OverallState):
    result = choose_rag_pipeline(state)
    if result == "end":
        return "human_review"
    else:
        return result


def fail_create_controller(state: OverallState):
    controller = state.get("control_loop_analysis", "")
    if "FAILED" in controller:
        return "block_diagram_search"
    return "control_loop_supervisor"


def fail_finding_block_diagram_search(state: OverallState):
    image_recognition = state.get("block_diagram_json", "")
    if "FAILED" in image_recognition:
        return "block_diagram_search"
    return "control_loop_analyser"


def fail_finding_block_diagram_url(state: OverallState):
    block_diagram_url = state.get("block_diagram_url", "")
    rag_decision = state.get("RAG_decision", {})
    if "FAILED" in block_diagram_url:
        if "OPENAI_WEB_SEARCH" in rag_decision:
            rag_decision["Flag"].remove("OPENAI_WEB_SEARCH")
            state["RAG_decision"] = rag_decision
            return "openai_web_search"
        return "end"
    return "openai_image_recognition"


def build_graph(model_name):
    load_dotenv()
    memory = MemorySaver()

    agnt = Agents(model_name)
    search_engine = SearchEngine()
    builder = StateGraph(OverallState)

    # Define nodes
    # builder.add_node("standardize_matlab_file", agnt.standardize_python_file)
    builder.add_node("system_analyser", agnt.system_analyser)
    builder.add_node("control_loop_analyser", agnt.control_loop_analyser)
    builder.add_node("control_loop_structure", agnt.control_loop_structure)
    builder.add_node("control_loop_supervisor", agnt.control_loop_supervisor)
    builder.add_node("create_controller_graph", create_controller_graph)
    builder.add_node("openai_web_search", agnt.openai_web_search)
    builder.add_node("block_diagram_search", search_engine.tavily_block_diagram_search)
    builder.add_node("openai_image_recognition", agnt.openai_image_recognition)

    # NEW: Add a dedicated placeholder node for human review
    builder.add_node("human_review", lambda state: {})

    # Core Flow
    # builder.add_edge(START, "standardize_matlab_file")
    # builder.add_edge("standardize_matlab_file", "system_analyser")
    builder.add_edge(START, "system_analyser")
    builder.add_edge("system_analyser", "control_loop_analyser")
    builder.add_edge("control_loop_analyser", "control_loop_structure")
    builder.add_conditional_edges(
        "control_loop_structure",
        fail_create_controller,
        {
            "block_diagram_search": "block_diagram_search",
            "control_loop_supervisor": "control_loop_supervisor"
        }
    )

    # Routing from Supervisor
    builder.add_conditional_edges(
        "control_loop_supervisor",
        supervisor_edge,
        {
            "control_loop_analyser": "control_loop_analyser",
            "create_controller_graph": "create_controller_graph",
            "block_diagram_search": "block_diagram_search"
        }
    )

    # NEW: Conditional edge after graph creation to check if human review is needed
    builder.add_conditional_edges(
        "create_controller_graph",
        check_human_intervention_condition,
        {
            "human_review": "human_review",
            "openai_web_search": "openai_web_search",
            "block_diagram_search": "block_diagram_search",
            "end": END
        }
    )

    # NEW: Routing out of the human review node once resumed
    builder.add_conditional_edges(
        "human_review",
        choose_rag_pipeline,
        {
            "openai_web_search": "openai_web_search",
            "block_diagram_search": "block_diagram_search",
            "end": END
        }
    )

    # Loop back to analysis after searching
    builder.add_edge("openai_web_search", "control_loop_analyser")

    builder.add_conditional_edges(
        "block_diagram_search",
        fail_finding_block_diagram_url,
        {
            "openai_image_recognition": "openai_image_recognition",
            "openai_web_search": "openai_web_search",
            "end": END
        }
    )
    builder.add_conditional_edges(
        "openai_image_recognition",
        fail_finding_block_diagram_search,
        {
            "block_diagram_search": "block_diagram_search",
            "control_loop_analyser": "control_loop_analyser"
        }
    )

    # NEW: Compile with interrupt BEFORE the human review node instead of after graph creation
    react_graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]
    )

    return react_graph


def draw_graph_diagram(app: StateGraph, output_path: str = "workflow_graph.png"):
    """
    Draw the workflow graph to a file for visualization.

    Args:
        app: Compiled StateGraph
        output_path: Path to save the diagram
    """
    try:
        app.get_graph().draw_mermaid_png(output_file_path=output_path)
        print(f"Workflow graph diagram saved to {output_path}")
    except Exception as e:
        print(f"Could not draw graph: {e}. You may need to install graphviz and mermaid-cli.")
