from backend_core.Recommender.build_graph import build_graph, draw_graph_diagram
from backend_core.Recommender.states import OverallState


# Initialize graphc
graph = build_graph("gpt-oss-120b")
draw_graph_diagram(graph)

# config = {"configurable": {"thread_id": "1"}}
#
# # --- STEP 1: Initial Run ---
# # The graph will run and then STOP before RAG
# initial_input = OverallState()
# initial_input["file_name"] = "matlab_input/aircraft_pitch.m"
# for event in graph.stream(initial_input, config):
#     print(event)
#
# # --- STEP 2: The Human Intervenes ---
# print("\n--- PAUSED FOR REVIEW ---")
# user_choice = input("Type 'continue' to run RAG or 'exit' to finish: ")
#
# # Update the state with the human's decision
# graph.update_state(config, {"messages": [{"role": "user", "content": user_choice}]})
#
# # --- STEP 3: Resume ---
# # Passing 'None' as input tells the graph to resume from where it paused
# for event in graph.stream(None, config):
#     print(event)
