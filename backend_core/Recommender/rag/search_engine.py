import os
from tavily import TavilyClient
import json
import queue


class SearchEngine:

    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.images = queue.Queue()
        self.block_diagram_search_round = 0

    def tavily_block_diagram_search(self, state, writer):
        writer({"progress": 0.25, "text": "🌐 Searching Web ..."})

        sys_id_json = json.loads(state["system_identification"])
        system_name = str(sys_id_json.get("system_name", ""))

        # query = f"{system_name} control system architecture block diagram"
        query = f"{system_name} controller block-diagram"
        if self.images.empty():
            if self.block_diagram_search_round >= 1:
                self.block_diagram_search_round = 0
                error_message = "FAILED to find proper Block Diagram"
                return {"messages": [error_message], "block_diagram_url": error_message}

            response = self.tavily.search(
                query=query,
                search_depth="advanced",
                max_results=1,
                include_images=True,
                chunks_per_source=1
            )
            for img in response["images"]:
                self.images.put(img)
            self.block_diagram_search_round = (self.block_diagram_search_round + 1)

        image_url = self.images.get()
        writer({"agent_tag": "🖼️.Found Block Diagram", "log_history": image_url})
        return {"messages": [image_url], "block_diagram_url": image_url}



