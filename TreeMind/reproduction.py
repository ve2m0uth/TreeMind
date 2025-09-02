import sys
from handler import *


def reproduce_bug(app_name, report_file_path, device_port='emulator-5554'):
    configs = load_config()
    agent1, agent2 = create_multiple_agents(configs)
    work_dir, ss_dir = make_dir('./', app_name)

    device = u2.connect(device_port)
    clear_logcat(device_port)
    bug_report = read_bug_report(report_file_path)
    print(bug_report)
    back_command = get_back_command(device)

    root = TreeNode(None, 1)
    root.conversation = [{"role": "user", "content": f"app name: {app_name}.\n{bug_report}\n"}]
    root.reward = 1
    node = root
    step = 1
    step_record = {}
    crash = False

    while not crash:
        explore_conversation = node.conversation.copy()
        device.set_orientation("natural")
        ui_info = {}

        while len(node.children) != 0:
            best_node = select_node(node, step)
            explore_conversation.extend(best_node.conversation)
            execute_command(device, best_node.command[-1])
            node = best_node
            node.visits += 1

        ui_info["widget_info"], ui_info["sequential_info"], ui_info["element"] = get_widget_info(device)
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
            execute_command(device, child.command[-1])
            simulation(device, agent2, child, ui_info, explore_conversation)
            crash = detect_crashes(device_port, device)
            if crash:
                step_record = child.command
                print("****Bug Found Successfully!****")
                break
            back_to_previous(device, node.command, back_command)
        backtrack(node)
        back_to_previous(device, root.command, back_command)
        node = root
        step += 1

    record_path = os.path.join(work_dir, 'record.txt')
    with open(record_path, 'w', encoding='utf-8') as f:
        f.write(str(step_record))


def make_dir(root_path, app_name):
    work_dir = create_dir(create_dir(root_path, "apps"), app_name)
    ss_dir = create_dir(work_dir, "screenshots")
    return work_dir, ss_dir


def detect_crashes(device_port, device):
    crash = False
    logcat = get_logcat(device_port)

    if logcat and 'FATAL' in logcat:
        print('Found fatal')
        crash = True
    if re.match(r".*?getText\(\) = Unfortunately, .*? has stopped.*", logcat):
        print('Found App Stop')
        crash = True
    if re.match(r".*?UiObject: getText\(\) = .*? isn't responding\..*?", logcat):
        print('Found App isn\'t Responding')
        crash = True

    if not crash:
        time.sleep(1)
        package_name = device.app_current()['package']
        crash = check_error_keywords(get_current_hierarchy(device), package_name) \
                or 'crashreport' in device.app_current()['activity'].lower()
    return crash


def get_logcat(device_port):
    adb_command = ['adb', '-s', f'{device_port}', 'logcat', '-d', '*:E']
    try:
        result = subprocess.run(adb_command, capture_output=True, text=True, encoding='utf-8',
                                errors='ignore', timeout=5)
    except subprocess.TimeoutExpired:
        print("Get logcat did not complete within the timeout period.")
        return ''
    if result.returncode != 0:
        raise Exception("adb logcat failed, make sure your device is connected and adb is installed")
    return result.stdout


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