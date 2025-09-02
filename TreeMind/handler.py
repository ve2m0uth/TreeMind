from model import *
from utils import *
from mcts import *
from controller import *
import ast
import re
import time
import random


def create_multiple_agents(config):
    agents = {}
    for i in range(1, 3):
        agents_name = f"agent{i}"
        agents[agents_name] = load_llm(config)
    return agents["agent1"], agents["agent2"]


def get_possible_action(mllm: BaseModel, node: TreeNode, device, ui_info, conversation):
    messages = conversation.copy()
    prompts = load_prompts("./prompts/action.json")
    base64_image = encode_image(node.image_path)
    combined_content = combine_info(ui_info["sequential_info"], base64_image)
    messages.append({"role": "user", "content": combined_content})
    prompts.extend(messages)
    response = mllm.get_model_response(prompts)
    print("=========================")
    print(f"Expand Agent: {response}")
    print("=========================")
    possible_command = convert_message_to_command(response)
    if not possible_command:
        return []
    possible_command = remove_same_command(possible_command)
    for i in range(len(possible_command)):
        if possible_command[i]["action"] in ['click', 'long_click']:
            process_coordinate(device, possible_command[i], ui_info)

    return possible_command


def remove_same_command(possible_command):
    seen = set()
    unique = []
    for d in possible_command:
        # 将 dict 转成有序的 (key, value) 元组，这样才可以哈希
        key = tuple(sorted(d.items()))
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def simulation(device, mllm: BaseModel, node: TreeNode, ui_info, conversation):
    messages = conversation.copy()
    prompts = load_prompts("./prompts/simulation.json")
    widget_info, sequential_info, element = get_widget_info(device)
    prompt = (f"Above is the current UI widget info. "
              f"After executing the command {node.command[-1]}(target step), the UI was updated to: {sequential_info}, "
              f"which is shown in the screenshot."
              f"Now please analyze the result and give the target step a score between 0 and 10.\n")
    base64_image = encode_image(node.parent.image_path)
    combined_content = combine_info(prompt, base64_image)
    messages.append({"role": "user", "content": combined_content})
    prompts.extend(messages)
    response = mllm.get_model_response(prompts)
    print("=========================")
    print(f"Simulation Agent: {response}")
    print("=========================")
    index = response.find("Score: ")
    if index != -1:
        match = re.search(r"\d+", response[index + len("Score: "):])
        if match:
            reward = int(match.group()) * 0.8
            node.reward = reward
        else:
            print("Invalid format of response!")
    if node.command[-1]['action'] == 'set_text':
        command = {'action': 'set_text', 'feature': node.command[-1]['feature'], 'input_text': ''}
        execute_command(device, command)


def read_bug_report(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.readlines()
    bug_report = ', '.join([line.strip() for line in content])
    return f"Bug Report: {bug_report}"


def convert_message_to_command(message):
    command_list = []
    try:
        index = message.find("Suggestions:")
        if index != -1:
            message = message[index:]
        if "[" in message and "]" in message:
            start_index = message.index("[")
            end_index = message.rindex("]")
            message = message[start_index:end_index + 1]
            # pattern = r"\[([^\]]*)\]"
            if message == "[]" or message == "[{}]":
                command_list = []
            else:
                command_list = ast.literal_eval(message)
        elif "{" in message and "}" in message:
            start_index = message.index("{")
            end_index = message.rindex("}")
            message = message[start_index:end_index + 1]
            if message == "{}":
                command_list = []
            else:
                command_list = [ast.literal_eval(message)]
        return command_list
    except (ValueError, SyntaxError) as e:
        print(f"Unable to convert message to command list: {str(e)}")
        return []


def get_path(node: TreeNode):
    conversation = []
    t = node
    while t.parent is not None:
        conversation = t.conversation + conversation
        t = t.parent
    return conversation


def combine_info(prompt, base64_image):
    content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]
    image = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        }
    ]
    combined_content = content + image
    return combined_content

