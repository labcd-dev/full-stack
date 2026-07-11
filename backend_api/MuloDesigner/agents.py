import os
import yaml
import json

from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from openai import OpenAI
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend_api.Recommender.agents.file_management import clean_json, get_content, load_m_file


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
    def __init__(self, model_name="gpt-oss-120b", prompt_dir="templates"):
        self.llm_nvidia = ChatNVIDIA(model="nvidia/llama-3.3-nemotron-super-49b-v1", temperature=0,
                                     max_completion_tokens=16000)
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.llm_groq = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_completion_tokens=16000)

        if model_name == "gpt-oss-120b":
            self.llm_think = ChatNVIDIA(model="openai/gpt-oss-120b", temperature=0, max_completion_tokens=16000)
        elif model_name.startswith("gpt"):
            self.llm_think = ChatOpenAI(model=model_name, temperature=0)

        self.prompts = {}
        self._load_all_prompts(prompt_dir)


    def _load_all_prompts(self, directory):
        """Discovers and loads all .yaml files in the prompt directory."""
        for filename in os.listdir(directory):
            if filename.endswith(".yaml"):
                name = filename.replace(".yaml", "")
                with open(os.path.join(directory, filename), 'r') as f:
                    self.prompts[name] = yaml.safe_load(f)


    def _call_llm(self, llm, prompt_text, system=False, context_messages=None, is_json=False):
        # Initialize messages
        messages = [SystemMessage(content=prompt_text) if system else HumanMessage(content=prompt_text)]
        if context_messages:
            messages = messages + context_messages

        if is_json:
            llm_formatted = llm.bind(response_format={"type": "json_object"})
            response = llm_formatted.invoke(messages)
        else:
            response = llm.invoke(messages)

        return get_content(response)


    def constraint_estimator(self, controller_structure, trimming_result):
        # writer({"progress": 0.3, "text": "ðŸ” Analyzing system dynamics..."})
        prompt = (self.prompts['constraint_estimator']['constraint_estimator']
                  .format(CONTROLLER_STRUCTURE_JSON=controller_structure, TRIM_JSON=trimming_result))

        response = self._call_llm(self.llm_nvidia, prompt, system=True)
        # response_content = clean_json(response, False)

        # writer({"agent_tag": "ðŸ”.System Analysis", "log_history": response_content})
        return response


    def constraint_estimator_web(self, controller_structure, trimming_result, model):
        # writer({"progress": 0.3, "text": "ðŸŒ Searching Web ..."})

        prompt = (self.prompts['constraint_estimator_web']['constraint_estimator_web']
                  .format(CONTROLLER_STRUCTURE_JSON=controller_structure, TRIM_JSON=trimming_result))
        schema = self.prompts['constraint_estimator_web']['schema']

        response = self.openai.responses.create(
            model=model,
            max_output_tokens=16000,
            tools=[{"type": "web_search_preview"}],
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "rag_result",
                    "schema": dict(schema),
                    "strict": True
                }
            })

        if hasattr(response, "usage"):
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = response.usage.total_tokens

            print("Input Tokens :", input_tokens)
            print("Output Tokens:", output_tokens)
            print("Total Tokens :", total_tokens)

        response_content = ""
        for item in response.output:
            if item.type == "message":
                response_content += item.content[0].text

        # response_content = clean_json(response_content, False)

        # writer({"agent_tag": "ðŸŒ.Web Search Result", "log_history": response_content})
        return response_content


if __name__ == '__main__':
    load_dotenv()

    controller = load_m_file("inputs/aircraft.json")
    trimming = load_m_file("inputs/aircraft_trim.json")
    agents = Agents(model_name="gpt-oss-120b")

    import pprint
    # pprint.pprint(agents.constraint_estimator(controller, trimming))
    pprint.pprint(agents.constraint_estimator_web(controller, trimming, 'gpt-5.4'))
