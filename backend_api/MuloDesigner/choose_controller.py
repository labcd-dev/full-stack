import json
import os
import re


def batch_controllers(controller, trimmingResult):
    controller_batches = [[]]
    controller_counter = 0
    layer = 0

    if type(controller) == str:
        controller = json.loads(controller)  # Fixed: Removed to_zero_based here
    signal_mapping, number_of_controllers = get_signal_mapping(controller)

    if type(trimmingResult) == str:
        trimmingResult = json.loads(trimmingResult)
    equilibrium = trimmingResult["equilibrium"]
    # print(equilibrium)

    for signal in signal_mapping.values():
        if "from" not in signal:
            ctrl = _get_controller_from_signal(signal, controller)
            controller_batches[0].append({
                # "address": signal["to"],
                "input": to_zero_based(ctrl["controlled_variable_in_equation"]),
                "input_index": get_index(ctrl["controlled_variable_in_equation"]),
                "output": to_zero_based(_get_state_name(ctrl["output_variable_in_equation"])),
                "output_index": get_index(ctrl["output_variable_in_equation"]),
                "target": get_equilibrium(equilibrium, ctrl["output_variable_in_equation"])
            })
            controller_counter += 1

    while controller_counter < number_of_controllers:
        for ctrl in controller_batches[layer]:
            output = ctrl["output"]
            signal = signal_mapping.get(output)
            if not signal:
                continue
            nextCtrl = _get_controller_from_signal(signal, controller)
            if nextCtrl is not None:
                if len(controller_batches) < layer + 2:
                    controller_batches.append([])
                controller_batches[layer + 1].append({
                    # "address": signal["to"],
                    "input": to_zero_based(nextCtrl["controlled_variable_in_equation"]),
                    "input_index": get_index(nextCtrl["controlled_variable_in_equation"]),
                    "output": to_zero_based(_get_state_name(nextCtrl["output_variable_in_equation"])),
                    "output_index": get_index(nextCtrl["output_variable_in_equation"]),
                    "target": get_equilibrium(equilibrium, nextCtrl["output_variable_in_equation"])
                })
                controller_counter += 1

        layer += 1

    return controller_batches


def get_index(signal_str):
    match = re.search(r'([A-Za-z_]+)[\(\[](\d+)[\)\]]', signal_str)
    zero_based_idx = int(match.group(2)) - 1
    return zero_based_idx


def get_equilibrium(equilibrium, signal_str):
    match = re.search(r'([A-Za-z_]+)[\(\[](\d+)[\)\]]', signal_str)
    zero_based_idx = int(match.group(2)) - 1
    # print(signal_str)
    # print(zero_based_idx)
    return equilibrium["x_e"][zero_based_idx]


def _get_controller_from_signal(signal, controller):
    try:
        plIndex = signal["to"]["pid_loop"]
        cIndex = signal["to"]["controller"]
        return controller["pid_loops"][plIndex]["controllers"][cIndex]
    except:
        return None


def get_signal_mapping(controller):
    signal_mapping = {}
    i = 0

    if type(controller) == str:
        controller = json.loads(controller)  # Fixed: Removed to_zero_based here
    pid_loops = controller["pid_loops"]

    pdLoop = 0
    for loop in pid_loops:
        ctrl = 0
        for controller_item in loop["controllers"]:
            controllerAddress = {"pid_loop": pdLoop, "controller": ctrl}

            # Apply the 0-based conversion utility safely
            inputSignal = to_zero_based(controller_item["controlled_variable_in_equation"])
            outputSignal = to_zero_based(_get_state_name(controller_item["output_variable_in_equation"]))

            signals = {inputSignal: "to", outputSignal: "from"}
            names = {
                inputSignal: to_zero_based(controller_item["controlled_variable_in_equation"]),
                outputSignal: to_zero_based(controller_item["output_signal"])
            }

            for signal, ky in signals.items():
                if signal not in signal_mapping:
                    arrow = {"name": names[signal], ky: controllerAddress}
                    signal_mapping[signal] = arrow
                else:
                    arrow = signal_mapping[signal]
                    arrow[ky] = controllerAddress
                    signal_mapping[signal] = arrow

            i += 1
            ctrl += 1

        pdLoop += 1

    return signal_mapping, i


def _get_state_name(outputSignal):
    # Robustly check for X_sp and convert safely using regex
    if outputSignal.startswith("X_sp"):
        match = re.search(r'\d+', outputSignal)
        if match:
            n = int(match.group())
            return f'X({n})'  # Keep original convention format; to_zero_based down the line handles it cleanly
    return outputSignal


def to_zero_based(signal_str):
    if not isinstance(signal_str, str):
        return signal_str

    # Matches text followed by numbers inside parentheses or brackets
    match = re.search(r'([A-Za-z_]+)[\(\[](\d+)[\)\]]', signal_str)
    if match:
        prefix = match.group(1)
        zero_based_idx = int(match.group(2)) - 1

        # If it's a setpoint string, match your expected output mapping keys
        if prefix == "X_sp":
            return f"X[{zero_based_idx}]"
        return f"{prefix}[{zero_based_idx}]"

    return signal_str.replace("(", "[").replace(")", "]")


def load_file(file_name):
    """Reads the file and returns the file content."""
    print("=== reading file ===")
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    else:
        raise FileNotFoundError(f"The file {file_name} does not exist in the current directory.")


if __name__ == "__main__":
    test = load_file("inputs/aircraft.json")
    trimming = load_file("inputs/aircraft_trim.json")

    import pprint
    # pprint.pprint(get_signal_mapping(test))
    # pprint.pprint(json.loads(test))
    pprint.pprint(batch_controllers(test, trimming))