import sys
from handler import *


def reproduce_bug(app_name, report_file_path, device_port='emulator-5554'):
    configs = load_config()
    agent1, agent2 = create_multiple_agents(configs)
    work_dir, ss_dir = make_dir('./', app_name)

    device = u2.connect(device_port)
    device.set_orientation("natural")
    clear_logcat(device_port)
    bug_report = read_bug_report(report_file_path)
    print(f"Bug Report:{bug_report}")
    restart_command = get_restart_command(device)

    root = TreeNode(None, 1)
    root.conversation = [{"role": "user", "content": f"app name: {app_name}\nBug Report:{bug_report}\n"}]
    root.reward = 1
    node = root
    step = 1
    step_record = {}
    crash = False

    while not crash:
        explore_conversation = node.conversation.copy()
        ui_info = {}

        while len(node.children) != 0:
            best_node = select_node(node, step)
            explore_conversation.extend(best_node.conversation)
            node = best_node
            node.visits += 1
        propagation(device, node.command)

        ui_info["widget_info"], ui_info["sequential_info"], ui_info["element"] = get_widget_info(device)
        print("===============================")
        print(ui_info["sequential_info"])
        print("===============================")
        node.conversation.append({"role": "user", "content": ui_info["sequential_info"]})
        explore_conversation.append({"role": "user", "content": ui_info["sequential_info"]})
        timestamp = int(time.time())
        node.image_path = ss_dir + f"//step{step}_{timestamp}.png"
        get_screenshot(device, node.image_path)

        possible_command = get_possible_action(agent1, node, device, ui_info, explore_conversation)
        if not possible_command:
            continue
        expand(node, possible_command)
        for child in node.children:
            execute_commands(device, child.command[-1])
            simulation(device, agent2, child, ui_info, explore_conversation)
            crash = detect_crashes(device_port, device)
            if crash:
                step_record = child.command
                print(f"****Bug Found Successfully!****\n\nWith steps {step}")
                break
            restart_device(restart_command)
            propagation(device, child.command[0:-1])
        if not crash:
            backtrack(node)
            restart_device(restart_command)
            propagation(device, root.command)
            node = root
            step += 1

    record_path = os.path.join(work_dir, 'record.txt')
    with open(record_path, 'w', encoding='utf-8') as f:
        f.write(str(step_record))
        print(f"Successfully reproduced the bug with following steps:\n {step_record}")


def make_dir(root_path, app_name):
    work_dir = create_dir(create_dir(root_path, "apps"), app_name)
    ss_dir = create_dir(work_dir, "screenshots")
    return work_dir, ss_dir


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python3 reproduction.py <app_name> <report_file_path> [device_port]")
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