from controller import execute_command
import subprocess
import yaml
import os
import json
import re
import time


def clear_logcat(device_ip):
    adb_command = ['adb', '-s', device_ip, 'logcat', '-c']
    subprocess.run(adb_command)


def create_dir(prefix, latter):
    dir_path = os.path.join(prefix, latter)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def load_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        s = f.read()
        return json.loads(s)


def get_back_command(device):
    # get package name
    backCommand = {}
    package_name = device.app_current()['package']
    if len(package_name) == 0:
        print('****Failed to find package name****')
        exit(0)
    adb_command = f"adb shell dumpsys package {package_name}"
    res = os.popen(adb_command).read()
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
        exit(0)
    adb_command = 'adb shell am force-stop ' + package_name
    execute_adb(adb_command)
    backCommand['stop_command'] = adb_command
    adb_command = "adb shell am start " + latter
    execute_adb(adb_command)
    backCommand['start_command'] = adb_command
    return backCommand


def back_to_previous(device, command_list, backCommand):
    execute_adb(backCommand['stop_command'])
    execute_adb(backCommand['start_command'])
    time.sleep(3)
    for i in range(len(command_list)):
        ret = execute_command(device, command_list[i])
        if ret is False:
            print("****Failed to back parent****")
            return True
    return False


def execute_adb(adb_command):
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Command execution failed: {adb_command}")
        print(result.stderr)
        exit(0)


def load_config(config_path = "./config.yaml"):
    configs = dict(os.environ)
    with open(config_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    configs.update(yaml_data)
    return configs
