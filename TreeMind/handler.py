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
    prompt = (
        f"### Action Selection\n"
        f"Current UI state: {ui_info['sequential_info']}\n"
        f"Please select the next action to perform based on the conversation history, current UI state and the bug report.\n"
    )
    base64_image = encode_image(node.image_path)
    combined_content = combine_info(prompt, base64_image)
    messages.append({"role": "user", "content": combined_content})
    prompts.extend(messages)
    response = mllm.get_model_response(prompts)
    response = response.replace("\n", "").replace("\r", "").replace("*", "").replace("`", "")
    print("=========================")
    print(f"Expand Agent: {response}")
    print("=========================")
    raw_strategies = convert_message_to_command(response)
    if not raw_strategies:
        return []
    raw_strategies = remove_same_command(raw_strategies)
    for strategy in raw_strategies:
        if not isinstance(strategy, list):
            continue
        for action in strategy:
            if action.get("action") in ['click', 'long_click']:
                process_coordinate(device, action, ui_info)
    return raw_strategies


def remove_same_command(possible_command):
    seen = set()
    unique = []
    for command_seq in possible_command:
        try:
            hashable_seq = tuple(
                tuple(sorted(cmd.items())) for cmd in command_seq
            )
        except AttributeError:
            continue
        if hashable_seq not in seen:
            seen.add(hashable_seq)
            unique.append(command_seq)
    return unique


def simulation(device, mllm: BaseModel, node: TreeNode, ui_info, conversation):
    messages = conversation.copy()
    prompts = load_prompts("./prompts/simulation.json")
    widget_info, sequential_info, element = get_widget_info(device)
    last_action = node.command[-1]
    pre_step_info = ui_info["sequential_info"] 
    prompt = (
        f"### Step Execution Data\n"
        f"Please evaluate the transition based on the workflow defined in the System Prompt:\n\n"
        f"1. **Previous Page**: {pre_step_info}\n"
        f"2. **Target Step Executed**: {last_action}\n"
        f"3. **Current Page (After Execution Target Step)**: {sequential_info}\n"
        f"4. **Visual References**: \n"
        f"   I have uploaded TWO images to assist your evaluation:\n"
        f"   - **First Image**: The **Previous Page** UI (Before the action was taken).\n"
        f"   - **Second Image**: The **Current Page** UI (The result after the action).\n"
        f"   Compare them to check for visual changes (e.g., dialogs appearing, screen transitions, error toasts).\n"
        f"### Evaluation Instructions\n"
        f"Compare the **Previous Page** and **Current Page** contexts (both text and visual) to assess the action's impact.\n"
        f"- **CRITICAL REMINDER**: Refer to the 'Core Rule' in your instructions. If **Pre-Step == Post-Step** (no visible change), do NOT automatically give a low score. If the action is logically valid according to the Bug Report (e.g., entering text, clicking a button reported as unresponsive), it implies a **High Score**.\n\n"
        f"### Output Format\n"
        f"Provide a brief reasoning, followed strictly by:\n"
        f"Score: <integer>"
    )
    
    pre_image_base64 = encode_image(node.parent.image_path)
    post_image_path = os.path.join(os.path.dirname(node.parent.image_path), f"temp.png")
    get_screenshot(device, post_image_path)
    post_image_base64 = encode_image(post_image_path)
    combined_content = combine_info(prompt, pre_image_base64, post_image_base64)
    messages.append({"role": "user", "content": combined_content})
    prompts.extend(messages)
    response = mllm.get_model_response(prompts)
    response = response.replace("\n", "").replace("\r", "").replace("*", "").replace("`", "")
    print("=========================")
    print(f"Simulation Agent: {response}")
    print("=========================")
    os.remove(post_image_path)
    match = re.search(r"Score:\s*(\d+)", response)
    if match:
        reward = int(match.group(1))
        node.reward = max(0, min(10, reward))
    else:
        print("Invalid format of response! Defaulting to 5.")
        node.reward = 5
    if isinstance(last_action, dict) and last_action.get('action') == 'set_text':
        cleanup_command = {'action': 'set_text', 'feature': last_action.get('feature'), 'input_text': ''}
        execute_single_command(device, cleanup_command)


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
            message = message[start_index:end_index + 1].strip()
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


def combine_info(prompt, *base64_images):
    content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]
    for img_base64 in base64_images:
        if img_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}",
                    "detail": "high"
                }
            })

    return content

