import os
import json
import re

from langchain_core.messages import AIMessage


def load_m_file(file_name):
    """
    Reads the .m file and returns the file content.
    """
    print("=== reading .m file ===")
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    else:
        raise FileNotFoundError(f"The file {file_name} does not exist in the current directory.")


def clean_quotes(data):
    """Recursively removes redundant leading/trailing quotes from keys and values."""
    if isinstance(data, dict):
        return {clean_quotes(k): clean_quotes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_quotes(i) for i in data]
    elif isinstance(data, str):
        return data.strip().strip('"').strip("'")
    return data


import ast  # add this import at the top of the file

def clean_json(raw_content: str, needDict: bool = True, needPrint: bool = False):
    # 1. Extract content from Markdown blocks or find Braces
    json_block_pattern = r"```(?:json)?\s*(.*?)\s*```"
    block_match = re.search(json_block_pattern, raw_content, re.DOTALL)

    if block_match:
        content = block_match.group(1).strip()
        if needPrint:
            print(20*"_" + "content" + 20*"_")
            print(content)
    else:
        brace_match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
        content = brace_match.group(1).strip() if brace_match else raw_content.strip()
        if needPrint:
            print(20 * "_" + "content brace_match" + 20 * "_")
            print(content)

    # 2. Remove // comments
    content = re.sub(r"//.*", "", content)

    # 3. Remove function object entries (e.g., 'system_f': <function ...>)
    # Include optional preceding comma
    function_pattern = r',?\s*(["|\'])(\w+)\1\s*:\s*<function\s+[^>]+>'
    content = re.sub(function_pattern, '', content)

    # 4. Clean up dangling commas after removal
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)
    content = re.sub(r'{\s*,', '{', content)
    content = re.sub(r'\[\s*,', '[', content)

    if needPrint:
        print(20 * "_" + "after removing functions" + 20 * "_")
        print(content)

    # 5. Convert Python dict literal (single quotes) to a real dict
    try:
        python_obj = ast.literal_eval(content)
        # 6. Convert to valid JSON string (double quotes, proper escaping)
        json_string = json.dumps(python_obj)
        if needPrint:
            print(20 * "_" + "json_string" + 20 * "_")
            print(json_string)
        # 7. Parse the JSON string into a dict/list
        data = json.loads(json_string)
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse content as Python literal:\n{content}")
        raise ValueError(f"Parsing error: {e}")

    # 8. Clean up extra quotes recursively (though json.dumps already did)
    cleaned_data = clean_quotes(data)
    if needPrint:
        print(20 * "_" + 'cleaned_data' + 20 * "_")
        print(cleaned_data)

    return cleaned_data if needDict else json.dumps(cleaned_data)

def get_content(message: AIMessage):
    content = message.content
    if len(content) > 0:
        return message.content
    return message.additional_kwargs["reasoning_content"]