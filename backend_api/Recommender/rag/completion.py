"""Pure helpers for assessing Recommender RAG completion."""

import os
from typing import Dict, Optional


def assess_rag_completion(file_name: str, results_dir: str = "results", minimum_graphs: int = 2) -> Dict[str, Optional[str]]:
    """Return the next recommender step and optional error message after RAG."""
    prefix = f"{file_name}_controller_graph_"
    count = sum(
        1
        for filename in os.listdir(results_dir)
        if filename.startswith(prefix)
    )

    if count >= minimum_graphs:
        return {"next_step": "comparison", "error_message": ""}

    return {
        "next_step": "review",
        "error_message": (
            "The Block Diagram Search Failed to find proper result please try another method"
        ),
    }
