from controller import get_current_hierarchy
from ElementTree_hepler import check_error_keywords
from controller import execute_commands
import subprocess
import yaml
import os
import json
import re
import time

flag = 0

def clear_logcat(device_ip):
    adb_command = ['adb', '-s', device_ip, 'logcat', '-c']
    subprocess.run(adb_command)

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


def create_dir(prefix, latter):
    dir_path = os.path.join(prefix, latter)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def load_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        s = f.read()
        return json.loads(s)


def get_restart_command(device):
    package_name = device.app_current()['package']
    if len(package_name) == 0:
        raise RuntimeError("Failed to find package name")
    adb_command = f"adb shell dumpsys package {package_name}"
    result = subprocess.run(
        adb_command,
        shell=True,
        capture_output=True,
        text=True
    )
    res = result.stdout
    if result.returncode != 0:
        raise RuntimeError(f"Failed to execute dumpsys: {result.stderr}")
    pattern = re.compile(r'android.intent.action.MAIN:\s*(\S+\s+\S+/\S+.+?filter\s+\S+)')
    match = pattern.search(res)
    if match:
        latter = match.group(1)
        for i in range(len(latter)):
            if latter[i] == ' ':
                latter = latter[i + 1:]
                break
    else:
        print("****Failed to Find activity Name****")
        raise RuntimeError("Failed to find activity name")

    return {
        'stop_command':
            f'adb shell am force-stop {package_name}',
        'start_command':
            f'adb shell am start {latter}'
    }


def restart_app(restartCommand):
    execute_adb(restartCommand['stop_command'])
    time.sleep(2)
    execute_adb(restartCommand['start_command'])
    time.sleep(2)

def propagation(device, command_list):
    device.set_orientation("natural")
    for command in command_list:
        if not execute_commands(device, command):
            return False
    return True


def execute_adb(adb_command):
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Command execution failed: {adb_command}")
        print(result.stderr)
        raise RuntimeError(f"Command execution failed: {adb_command}\n{result.stderr}")


def load_config(config_path = "./config.yaml"):
    configs = dict(os.environ)
    with open(config_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    configs.update(yaml_data)
    return configs
