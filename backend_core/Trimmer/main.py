"""
main.py - Execution entry point with Human-in-the-Loop logic

This module provides the main execution entry point for the agentic control system framework.
It supports Human-in-the-Loop breakpoints using LangGraph's interrupt_before functionality.
"""

import numpy as np
import json
import logging
from datetime import datetime
import os
import sys

from build_graph import build_workflow_graph
from states import WorkflowState
from backend_core.Trimmer.functionalNodes.create_controller_graph import Plotter
from pdf_generator import generate_pdf_report


def main():
    """Main execution function with Human-in-the-Loop support."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = os.path.join(base_dir, "../logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"session_langraph_{session_timestamp}.log")

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger.info("Session started with Langraph: %s", session_timestamp)

    # Build the workflow graph
    app = build_workflow_graph()

    # Initial state
    initial_state: WorkflowState = {
        "ui_mode": "terminal",
        "logger": logger,
        "trace": [],
        "restart_count": 0,
        "max_restarts": 3,
        "final_result": {},
        "config": {},
        "initial_guess": {},
        "strategy": "",
        "x_e": np.array([]),
        "u_e": np.array([]),
        "converged": False,
        "A": np.array([]),
        "B": np.array([])
    }

    # Run the workflow
    final_state = app.invoke(initial_state)
    result = final_state.get('final_result', {})
    config = final_state.get('config', {})

    # Save results
    if not config:
        for entry in reversed(final_state.get('trace', [])):
            if 'config' in entry:
                config = entry['config']
                break

    safe_system_name = config.get('system_name', 'unknown_system').replace(" ", "_")
    output_dir = os.path.join(base_dir, "../results")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{safe_system_name}_result_langraph.json")
    with open(output_file, 'w') as f:
        json.dump(make_serializable(result), f, indent=2)

    print("\n" + "="*60)
    print("RESULTS (Langraph)")
    print("="*60)

    if "error" in result:
        logger.error("Workflow error: %s", result['error'])
        print(f"\n✗ ERROR: {result['error']}")
        print(f"\nResult saved to: {output_file}")
        sys.exit(1)

    print(f"\nResult saved to: {output_file}")

    # Generate PDF Report and Visualization
    if result and 'equilibrium' in result and result['equilibrium'].get('x_e') is not None:
        pdf_file = os.path.join(output_dir, f"{safe_system_name}_report_langraph.pdf")
        generate_pdf_report(result, config, pdf_file)
        logger.info("PDF report generated: %s", pdf_file)

        # Visualization
        print("\n" + "-"*60)
        print("SIMULATION")
        print("-"*60)
        plot_choice = input("\nGenerate time response plot? (y/n) [default=y]: ").strip().lower()
        if plot_choice != 'n':
            x_e = np.array(result['equilibrium']['x_e'])
            u_e = np.array(result['equilibrium']['u_e'])
            plotter = Plotter(config['system_f'], config['params'], x_e, u_e)
            t_span = np.linspace(0, 50, 1000)
            x0 = x_e + 0.01 * np.random.randn(len(x_e))
            plot_file = os.path.join(output_dir, f"{safe_system_name}_response_langraph.png")
            plotter.plot_time_response(t_span, x0, config['state_vars'], save_path=plot_file)
            logger.info("Plot saved to: %s", plot_file)

    # Offer to display the workflow graph
    graph_path = "plots"
    if os.path.exists(graph_path):
        print("\n" + "-"*60)
        print("WORKFLOW GRAPH OPTION")
        print("-"*60)
        graph_choice = input("Display workflow graph? (y/n) [default=n]: ").strip().lower()
        if graph_choice == 'y':
            try:
                import webbrowser
                webbrowser.open(graph_path)
                print(f"Workflow graph opened in default viewer.")
            except Exception as e:
                print(f"Could not open graph: {e}")

    logger.info("Session ended.")
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE (Langraph)")
    print("="*60 + "\n")

def make_serializable(obj):
    """Convert objects to JSON-serializable format."""
    if callable(obj):
        return str(obj)
    elif hasattr(obj, 'tolist'):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)

if __name__ == "__main__":
    main()
