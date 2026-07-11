from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import json

from backend_core.Recommender.agents.file_management import clean_json
from backend_core.Trimmer.states import WorkflowState
from backend_core.Trimmer.agenticNodes.parsing_graph import ParsingGraph
from backend_core.Trimmer.agenticNodes.input_handlers import InputHandlers
from backend_core.Trimmer.agenticNodes.create_agent import create_agent, _load_template


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Dynamically key instances by class and model name to support multi-model caching
        model_name = kwargs.get('model_name') or (args[0] if args else "gpt_os-120b")
        key = (cls, model_name)
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]



class Agents(metaclass=SingletonMeta):
    
    def __init__(self, model_name="gpt-oss-120b"):
        # self.llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1, api_key=os.getenv(
        # "GEMINI_API_KEY"))
        self.llm_nvidia = ChatNVIDIA(model="nvidia/llama-3.3-nemotron-super-49b-v1", temperature=0,
                                     max_completion_tokens= 8000)
        if model_name == "gpt-oss-120b":
            # self.llm_think = ChatNVIDIA(model="openai/gpt-oss-120b", temperature=0)
            self.llm_think = ChatGroq(model="openai/gpt-oss-120b", temperature=0.1)
        elif model_name.startswith("gpt-"):
            self.llm_think = ChatOpenAI(model=model_name, temperature=0.1)


    def parse_system(self, state: WorkflowState, writer) -> WorkflowState:
        writer({"progress": 0.1, "text": "⚙️ Parsing System..."})

        logger = state['logger']
        logger.info("--- Entering Node: parse_system ---")

        parsing_graph = ParsingGraph(self.llm_think, logger=logger)

        if state["ui_mode"] == "terminal":
            file_path = InputHandlers.get_file_path()
            result = parsing_graph.invoke({"input_text": file_path, "ui_mode": "terminal"})


        elif state["ui_mode"] == "streamlit":
            inputContent = state['input_content']
            operating_conditions = state["trimming_params"]
            initial_state = parsing_graph.build_initial_state(
                {"equation": inputContent, "ui_mode": "streamlit", "ui_inputs": state["ui_inputs"],
                 "operating_conditions": operating_conditions})
            result = parsing_graph.invoke(initial_state)


        config = result.get("final_config", {})

        logger.info("Parsed config: %s", json.dumps(self.make_serializable(config), indent=2))
        state['config'] = config

        writer({"agent_tag": "⚙️. Parsing System", "log_history": clean_json(str(config), False)})
        return state

    def generate_prompt(self):
        return create_agent(self.llm_think, "generate_prompt")

    def validate_only(self, state: WorkflowState):
        logger = state['logger']
        parsing_graph = ParsingGraph(self.llm_think, logger=logger)
        config = state['config']

        return parsing_graph.validate_only(config)

    def plan_strategy(self):
        return create_agent(self.llm_think, "plan_strategy")

    def equilibrium_check(self):
        return create_agent(self.llm_think, "equilibrium_check")

    def human_intervention(self):
        return create_agent(self.llm_think, "human_intervention")

    def generate_narratives(self, result: dict, config: dict, system_identification: dict = None,
                            controller_json: dict = None) -> dict:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser

        # We use a JSON output parser to ensure the LLM returns exactly the dictionary structure
        # required by pdf_generator.py
        parser = JsonOutputParser()

        prompt = _load_template("generate_narratives")

        system_prompt = prompt["system_prompt"]
        human_prompt = prompt["human_prompt"]

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        # Build the LangChain runnable
        chain = prompt_template | self.llm_think | parser

        try:
            # Safely invoke the chain with serialized inputs to prevent serialization errors
            narratives = chain.invoke({
                "config": self.make_serializable(config),
                "result": self.make_serializable(result),
                "sys_id": self.make_serializable(system_identification) if system_identification else "Not provided",
                "ctrl_json": self.make_serializable(controller_json) if controller_json else "Not provided"
            })
            return narratives

        except Exception as e:
            # Fallback empty dictionary to prevent crashing the PDF generator if LLM fails
            print(f"Error generating LLM narratives: {e}")
            return {}

    def make_serializable(self, obj):
        if callable(obj):
            return str(obj)
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        else:
            try:
                json.dumps(obj)
                return obj
            except TypeError:
                return str(obj)




