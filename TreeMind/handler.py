from model import *
from utils import *
from mcts import *
from controller import *
import ast
import json
import os
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


def _simulation_image_content(image_path):
    if not image_path or not os.path.exists(image_path):
        return None
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{encode_image(image_path)}",
            "detail": "high",
        },
    }


def _build_batch_simulation_content(simulation_items):
    candidate_descriptions = []
    for item in simulation_items:
        candidate_descriptions.append(
            f"Candidate {item['candidate_id']}:\n"
            f"- Target step: {item['action']}\n"
            f"- Previous page: {item['previous_ui']}\n"
            f"- Current page: {item['current_ui']}"
        )

    prompt = (
        "### Batch Step Evaluation\n"
        "Evaluate every candidate independently against the bug report and "
        "reproduction path. Candidate ordering does not imply quality.\n\n"
        + "\n\n".join(candidate_descriptions)
        + "\n\n### Visual References\n"
        "The first image is the common previous page. Each following image is "
        "the post-action page for the candidate identified by the preceding label.\n"
        "Return only the JSON object required by the system prompt."
    )
    content = [{"type": "text", "text": prompt}]

    pre_image = _simulation_image_content(simulation_items[0].get("previous_image_path"))
    if pre_image:
        content.append({"type": "text", "text": "Common previous-page image:"})
        content.append(pre_image)

    for item in simulation_items:
        post_image = _simulation_image_content(item.get("current_image_path"))
        if post_image:
            content.append({
                "type": "text",
                "text": f"Post-action image for candidate {item['candidate_id']}:",
            })
            content.append(post_image)
    return content


def _parse_batch_scores(response, expected_ids):
    cleaned = response.strip().replace("```json", "").replace("```", "").strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return {}
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}

    evaluations = payload.get("evaluations", []) if isinstance(payload, dict) else []
    scores = {}
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue
        try:
            candidate_id = int(evaluation["candidate_id"])
            raw_score = float(evaluation["score"])
        except (KeyError, TypeError, ValueError):
            continue
        if candidate_id in expected_ids and candidate_id not in scores:
            scores[candidate_id] = max(0.0, min(10.0, raw_score))
    return scores


def batch_simulation(mllm: BaseModel, simulation_items, conversation):
    if not simulation_items:
        return {}

    messages = conversation.copy()
    prompts = load_prompts("./prompts/simulation.json")
    messages.append({
        "role": "user",
        "content": _build_batch_simulation_content(simulation_items),
    })
    prompts.extend(messages)
    try:
        response = mllm.get_model_response(prompts)
    except ModelRequestError as exc:
        print(f"Batch simulation model request failed: {exc}")
        return {}

    print("=========================")
    print(f"Simulation Agent: {response}")
    print("=========================")
    expected_ids = {item["candidate_id"] for item in simulation_items}
    scores = _parse_batch_scores(response, expected_ids)
    missing_ids = expected_ids - scores.keys()
    if missing_ids:
        print(f"Batch simulation omitted or invalidated candidates: {sorted(missing_ids)}")
    return scores


def simulation(device, mllm: BaseModel, node: TreeNode, ui_info, conversation):
    _, current_ui, _ = get_widget_info(device)
    current_image_path = os.path.join(
        os.path.dirname(node.parent.image_path),
        f"simulation_{time.time_ns()}_post.png",
    )
    if not get_screenshot(device, current_image_path):
        current_image_path = None

    item = {
        "candidate_id": 0,
        "action": node.command[-1],
        "previous_ui": ui_info["sequential_info"],
        "current_ui": current_ui,
        "previous_image_path": node.parent.image_path,
        "current_image_path": current_image_path,
    }
    try:
        return batch_simulation(mllm, [item], conversation).get(0, 5)
    finally:
        if current_image_path and os.path.exists(current_image_path):
            try:
                os.remove(current_image_path)
            except OSError as exc:
                print(f"Failed to remove temporary screenshot: {exc}")

        last_action = node.command[-1]
        if isinstance(last_action, dict) and last_action.get("action") == "set_text":
            cleanup_command = {
                "action": "set_text",
                "feature": last_action.get("feature"),
                "input_text": "",
            }
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

