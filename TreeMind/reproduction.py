import sys
from handler import *
from model import ModelRequestError


def reproduce_bug(app_name, report_file_path, device_port='emulator-5554'):
    configs = load_config()
    expand_agent, simulate_agent = create_multiple_agents(configs)
    empty_candidate_retries = max(1, int(configs.get("EMPTY_CANDIDATE_RETRIES", 2)))
    work_dir, ss_dir = make_dir('./', app_name)

    device = u2.connect(device_port)
    device.set_orientation("natural")
    clear_logcat(device_port)
    bug_report = read_bug_report(report_file_path)
    print(f"Bug Report:{bug_report}")
    restart_command = get_restart_command(device)

    root = TreeNode(None, 1)
    root.conversation = [{"role": "user", "content": f"app name: {app_name}\nBug Report:{bug_report}\n"}]
    node = root
    step = 1
    step_record = {}
    crash = False
    search_exhausted = False

    while not crash and not search_exhausted:
        explore_conversation = node.conversation.copy()
        ui_info = {}
        while len(node.children) != 0:
            best_node = select_node(node)
            if best_node is None:
                mark_dead_end(node)
                break
            explore_conversation.extend(best_node.conversation)
            node = best_node

        if node.dead_end:
            if node is root:
                search_exhausted = True
                break
            restart_app(restart_command)
            node = root
            step += 1
            continue

        if not propagation(device, node.command):
            print(f"Failed to replay path for node at depth {node.depth}; pruning it.")
            mark_dead_end(node)
            restart_app(restart_command)
            node = root
            step += 1
            continue

        ui_info["widget_info"], ui_info["sequential_info"], ui_info["element"] = get_widget_info(device)
        print("===============================")
        print(ui_info["sequential_info"])
        print("===============================")
        node.conversation.append({"role": "user", "content": ui_info["sequential_info"]})
        explore_conversation.append({"role": "user", "content": ui_info["sequential_info"]})
        timestamp = int(time.time())
        node.image_path = ss_dir + f"//step{step}_{timestamp}.png"
        get_screenshot(device, node.image_path)

        possible_command = []
        for attempt in range(1, empty_candidate_retries + 1):
            try:
                possible_command = get_possible_action(expand_agent, node, device, ui_info, explore_conversation)
            except ModelRequestError as exc:
                print(f"Action model request failed ({attempt}/{empty_candidate_retries}): {exc}")
                continue
            if possible_command:
                break
            print(f"Action agent returned no candidates({attempt}/{empty_candidate_retries}).")

        if not possible_command:
            print(f"No candidates after bounded retries; pruning depth {node.depth}.")
            mark_dead_end(node)
            restart_app(restart_command)
            node = root
            step += 1
            continue

        expand(node, possible_command)
        expansion_complete = True
        simulation_items = []
        for candidate_id, child in enumerate(node.children):
            execution_success = execute_commands(device, child.command[-1])
            child.execution_status = "success" if execution_success else "failed"
            if execution_success:
                child.conversation = [{
                    "role": "user",
                    "content": f"\n\nSuccessfully executed command {child.command[-1]}.",
                }]
            else:
                child.immediate_value = 0.0
                child.record_value(child.immediate_value)
                mark_dead_end(child)
                child.conversation = [{
                    "role": "user",
                    "content": f"\n\nFailed to execute command {child.command[-1]}.",
                }]

            crash = execution_success and detect_crashes(device_port, device)
            if crash:
                step_record = child.command
                print(f"****Bug Found Successfully!****\n\nWith steps {step}")
                break
            if execution_success:
                _, current_ui, _ = get_widget_info(device)
                current_image_path = os.path.join(
                    ss_dir,
                    f"step{step}_{timestamp}_candidate{candidate_id}_post.png",
                )
                if not get_screenshot(device, current_image_path):
                    current_image_path = None
                simulation_items.append({
                    "candidate_id": candidate_id,
                    "child": child,
                    "action": child.command[-1],
                    "previous_ui": ui_info["sequential_info"],
                    "current_ui": current_ui,
                    "previous_image_path": node.image_path,
                    "current_image_path": current_image_path,
                })
            restart_app(restart_command)
            if not propagation(device, child.command[0:-1]):
                print("Failed to restore the parent state; stopping sibling evaluation.")
                mark_dead_end(node)
                expansion_complete = False
                break

        if simulation_items:
            try:
                if not crash:
                    scores = batch_simulation(simulate_agent, simulation_items, explore_conversation)
                    for item in simulation_items:
                        candidate_id = item["candidate_id"]
                        if candidate_id not in scores:
                            fallback_scores = batch_simulation(simulate_agent, [item], explore_conversation)
                            scores[candidate_id] = fallback_scores.get(candidate_id, 0.5)

                        child = item["child"]
                        child.immediate_value = scores[candidate_id]
                        child.record_value(child.immediate_value)
            finally:
                for item in simulation_items:
                    current_image_path = item.get("current_image_path")
                    if current_image_path and os.path.exists(current_image_path):
                        try:
                            os.remove(current_image_path)
                        except OSError as exc:
                            print(f"Failed to remove temporary screenshot: {exc}")
        if search_exhausted:
            break
        if not crash and expansion_complete:
            child_values = [child.immediate_value for child in node.children if child.immediate_value is not None]
            if child_values:
                backtrack(node, sum(child_values) / len(child_values))
            else:
                mark_dead_end(node)
            restart_app(restart_command)
            node = root
            step += 1
        elif not crash:
            restart_app(restart_command)
            node = root
            step += 1

    record_path = os.path.join(work_dir, 'record.txt')
    with open(record_path, 'w', encoding='utf-8') as f:
        f.write(str(step_record))
    if crash:
        print(f"Successfully reproduced the bug with following steps:\n {step_record}")
    else:
        print("Search exhausted without reproducing the bug.")

def make_dir(root_path, app_name):
    work_dir = create_dir(create_dir(root_path, "apps"), app_name)
    ss_dir = create_dir(work_dir, "screenshots")
    return work_dir, ss_dir

def mark_dead_end(target_node):
    target_node.dead_end = True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python reproduction.py <app_name> <report_file_path> [device_port]")
        print("  <app_name>          Name of the app to reproduce the bug")
        print("  <report_file_path>  Path to the bug report file")
        print("  [device_port]       Optional: device port, default is 'emulator-5554'")
    elif len(sys.argv) == 3:
        app_name = sys.argv[1]
        report_file_path = sys.argv[2]
        reproduce_bug(app_name, report_file_path)
    elif len(sys.argv) == 4:
        app_name = sys.argv[1]
        report_file_path = sys.argv[2]
        device_port = sys.argv[3]
        reproduce_bug(app_name, report_file_path, device_port)
    else:
        print("Usage: python3 reproduction.py <app_name> <report_file_path> [device_port]")
