import time
import uiautomator2 as u2
import xml.etree.ElementTree as ET
import subprocess
import re
import random
import string
from ElementTree_hepler import *
from collections import defaultdict


def get_current_hierarchy(device):
    with open('tmp', 'w', encoding='utf-8') as file:
        file.write(device.dump_hierarchy())
    xmlp = ET.XMLParser(encoding="utf-8")
    tree = ET.parse('tmp', parser=xmlp)
    return tree


def get_container_type(current_type, className, ):
    if current_type != 'click':
        return current_type

    if '.Switch' in className:
        return 'switch_widget'
    elif 'Spinner' in className:
        return 'spinner'
    elif 'CheckBox' in className:
        return 'check_box'
    elif 'EditText' in className:
        return 'set_text'
    return 'click'


def process_group_general(root, parent_map, info, attr_to_elements):
    attr_to_group_elments = defaultdict(list)
    group, other_text, visited_elements = [], [], []
    type = 'click'
    # if 'toolbar' in root.attrib.get('resource-id', ''):
    #    type='toolbar'
    if root.attrib.get('scrollable', 'false') == 'true':
        type = 'scrollable'

    # Iterate over all nodes
    for element in root.iter():
        visited_elements.append(element)
        clickable = element.attrib.get('clickable', 'false') == 'true'
        enabled = element.attrib.get('enabled', 'false') == 'true'
        text = element.attrib.get('text', '')
        content_desc = element.attrib.get('content-desc', '')
        resource_id = element.attrib.get('resource-id', '')
        className = element.attrib.get('class', '')

        type = get_container_type(type, className)
        className = className[className.rfind('.') + 1:]

        if type == 'set_text':
            if resource_id and text:
                group.insert(0, {className: resource_id})
                # if 'EditText' in className:
                #    group.insert(0, {className : resource_id})
                # else:
                #    group.insert(0,  resource_id)
                group.insert(0, text)
                attr_to_group_elments[resource_id].append(element)
            elif resource_id:
                group.insert(0, {className: resource_id})
            # if 'EditTxt' in className:
            #    group.insert(0, {className : resource_id})
            # else:
            #    group.insert(0,  resource_id)
            elif text:
                group.insert(0, text)
                attr_to_group_elments[text].append(element)
            else:
                bounds = element.attrib.get('bounds', '')
                group.insert(0, bounds)
                attr_to_group_elments[bounds].append(element)
        elif 'CheckBox' in className:
            if group != [] or other_text != []:
                group.append('status:checked' if element.attrib.get('checked', '') == 'true' else 'status:unchecked')
            elif text != '':
                group.extend(
                    [text, 'status:checked' if element.attrib.get('checked', '') == 'true' else 'status:unchecked'])
                attr_to_group_elments[text].append(element)
            elif resource_id:
                group.extend([resource_id,
                              'status:checked' if element.attrib.get('checked', '') == 'true' else 'status:unchecked'])
                attr_to_group_elments[resource_id].append(element)
            else:
                bounds = element.attrib.get('bounds', '')
                group.extend(
                    [bounds, 'status:checked' if element.attrib.get('checked', '') == 'true' else 'status:unchecked'])
                attr_to_group_elments[bounds].append(element)
        elif clickable:
            if content_desc:
                if enabled:
                    group.insert(0, {className: content_desc})
                else:
                    group.insert(0, 'disabled')
                    group.insert(0, {className: content_desc})
                attr_to_group_elments[content_desc].append(element)

            elif text:
                group.insert(0, text)
                attr_to_group_elments[text].append(element)

            elif resource_id:
                group.insert(0, {className: resource_id})
                attr_to_group_elments[resource_id].append(element)

            elif element.attrib.get('NAF', '') == 'true':
                bounds = element.attrib.get('bounds', '')
                group.insert(0, {'NAF': bounds})
                attr_to_group_elments[bounds].append(element)
        elif text and len(text) < 50:

            other_text.append(text)
            attr_to_group_elments[text].append(element)

    if other_text:
        group.extend(other_text)

    info['visited'].extend(visited_elements)

    for key, value in attr_to_group_elments.items():
        if key in attr_to_elements:
            attr_to_elements[key].extend(value)
        else:
            attr_to_elements[key] = value
    root_id = root.attrib.get('resource-id', '')
    if group != []:
        if root_id and root_id not in group:
            info[type].append(f"{root_id[root_id.rfind('/') + 1:]}:{group}")

        else:
            info[type].append(f"{group}")


def get_operable_elements(element, package_name, parent_map, info, attr_to_elements):
    if element.tag == 'node':
        # Filter out elements with package "com.android.systemui"
        if element.attrib.get('package', '') == 'com.android.systemui':
            return
        if element in info['visited']:
            return
        clickable = element.attrib.get('clickable', 'false') == 'true'
        long_clickable = element.attrib.get('long-clickable', 'false') == 'true'
        text = element.attrib.get('text', '')
        content_desc = element.attrib.get('content-desc', '')
        resource_id = element.attrib.get('resource-id', '')
        class_name = element.attrib.get('class', '')
        # 'edittext' in resource_id
        info['visited'].append(element)
        if 'toolbar' in resource_id:
            process_group_general(element, parent_map, info, attr_to_elements)
        elif (clickable or long_clickable) and not (text or content_desc or resource_id):
            process_group_general(element, parent_map, info, attr_to_elements)
        elif all_children_are_leaves(element) and is_clickable_or_has_clickable_children(element):
            process_group_general(element, parent_map, info, attr_to_elements)
        elif (clickable or long_clickable):
            if content_desc:
                info['click'].append([content_desc])
                # attr_to_elements[content_desc].append(element)
                if content_desc in attr_to_elements:
                    attr_to_elements[content_desc].append(element)
                else:
                    attr_to_elements.setdefault(content_desc, []).append(element)
            elif text and len(text) < 100:
                info['click'].append([text])
                attr_to_elements[text].append(element)
            elif resource_id:
                info['click'].append([resource_id])
                # attr_to_elements.setdefault(resource_id, []).append(element)
                if resource_id in attr_to_elements:
                    attr_to_elements[resource_id].append(element)
                else:
                    attr_to_elements.setdefault(resource_id, []).append(element)


        elif text != '':
            info['local_text'].append(text)

    for child in element:
        get_operable_elements(child, package_name, parent_map, info, attr_to_elements)


def get_sequential_info(info, activity, orientation, toast):
    info['Other Widgets with Text in This Page'] = info["local_text"]
    del info["visited"]
    del info["local_text"]

    info = {k: v for k, v in info.items() if v != [] and v != [[]]}

    info_string = ''
    for key, values in info.items():
        info_string += f"{key} has the following group(s):"
        i = 1
        for v in values:
            info_string += f"{i}#.{v};"
            i += 1
        # info_string +="\n"
    if toast is not None:
        return f"\n*Current Screen Information:  #Current Activity: {activity}. # UI Information:{info_string}.Toast message on the page: {toast}"
    else:
        return f"\n*Current Screen Information:  #Current Activity: {activity}.  # UI Information:{info_string}."



def get_screen_information(device, attribute_to_element_map, package_name):
    try:
        toast = device.toast.get_message(2, 5, None)
    except:
        toast = None

    tree = get_current_hierarchy(device)
    root = tree.getroot()
    parent_map = build_parent_map(tree)
    info = {'toolbar': [], 'set_text': [], 'click': [], 'spinner': [], 'check_box': [], 'switch_widget': [],
            'scrollable': [], 'local_text': [], 'visited': []}

    activity = device.app_current()['activity']
    get_operable_elements(root, package_name, parent_map, info, attribute_to_element_map)

    return info, get_sequential_info(info, activity, device.orientation, toast), attribute_to_element_map


def get_screenshot(device, screenshot_path):
    try:
        device.screenshot(f'{screenshot_path}')
        return True
    except Exception as e:
        print("Failed to get current screenshot")
        return False


def execute_single_command(device, command):
    if not isinstance(command, dict):
        print(f"Invalid command type: {type(command).__name__}")
        return False

    try:
        package_name = device.app_current()['package']
    except Exception as e:
        print(f"Unable to read current app before executing {command}: {e}")
        return False
    command_map = {
        'complete': lambda: None,
        'restart': lambda: restart(device, package_name),
        'scroll': lambda: scroll(device, command.get('index', 0),
                                command.get('to_direction', command.get('target_direction', None))),
        'orientation': lambda: orientation(command),
        'rotate': lambda: orientation(command),
        'back': lambda: back(device),
        'swipe': lambda: swipe(device, command.get('to_direction', None)),
        'multiple_selection': lambda: multiple_selection(device, command['features']),
        'navigate up': lambda: back(device),
    }
    try:
        action = command.get('action', '')
        action = action.strip().lower()
        if action in command_map:
            return command_map[action]() is not False
        elif command.get('feature', None) is None:
            print(f"The program cannot recognized this actions {command}")
            return False
        else:
            rep_attr = command.get('feature', None)
            index = command.get('index', 0)

            if action == 'set_text':
                return set_text(
                    device, rep_attr, command.get('input_text', "qwer1234@"), index
                ) is True
            elif action == 'click':
                if command.get('coordinate', None) is None:
                    ui_object = locate_ui_object(device, rep_attr, index)
                    if ui_object:
                        getattr(ui_object, action)()
                        return True
                else:
                    click(device, command["coordinate"])
                    return True
            elif action == 'long_click':
                if command.get('coordinate', None) is None:
                    ui_object = locate_ui_object(device, rep_attr, index)
                    if ui_object:
                        getattr(ui_object, action)()
                        return True
                else:
                    long_click(device, command["coordinate"])
                    return True
    except Exception as e:
        print(f"Command execution error for {command}: {e}")
        return False
    return False


def execute_commands(device, command_list):
    if not isinstance(command_list, list):
        print(f"Invalid command sequence type: {type(command_list).__name__}")
        return False
    for command in command_list:
        if execute_single_command(device, command):
            continue
        else:
            print(f"The program cannot recognized this actions {command}")
            return False
    return True


def locate_ui_object(device, rep_attr, type=None, index=0):
    ui_object = device(text=rep_attr)[index]
    if ui_object:
        return ui_object

    ui_object = device(description=rep_attr)[index]
    if ui_object:
        return ui_object

    ui_object = device(resourceId=rep_attr)[index]
    if ui_object:
        return ui_object

    bounds_dict = get_bounds_dict(rep_attr)
    if bounds_dict is not None:
        for ui_object in device():
            if ui_object.info['bounds'] == bounds_dict:
                if type == None:
                    return ui_object
                if type == 'set_text' and 'EditText' in ui_object.info['className']:
                    return ui_object


def get_bounds_dict(bounds):
    pattern = r'^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$'
    match = re.match(pattern, bounds)
    if not match:
        return None
    coordinates = [int(coord) for pair in bounds.split('][') for coord in pair.strip('[]').split(',')]
    if len(coordinates) != 4:
        raise ValueError(f"Expected 4 coordinates, but got {len(coordinates)}")
    bounds_dict = {'left': coordinates[0],
                   'top': coordinates[1],
                   'right': coordinates[2],
                   'bottom': coordinates[3]}
    return bounds_dict


def restart(device, package_name):
    device.app_stop(package_name)
    time.sleep(2)
    device.app_start(package_name)
    time.sleep(2)
    return True


def scroll(device, index=0, direction=None):
    scrollables = device(scrollable=True)
    if not scrollables.exists:
        return False
    if direction == 'up' or direction == 'top' or direction == None:
        device(scrollable=True)[index].fling.vert.toBeginning()
    elif direction == 'down' or direction == 'bottom':
        device(scrollable=True)[index].fling()
    elif direction == 'end':
        device(scrollable=True)[index].fling.toEnd()
    else:
        device.swipe_ext("down", scale=0.9)
    time.sleep(1)
    return True

def get_current_rotation():
    result = subprocess.check_output(
        "adb shell settings get system user_rotation",
        shell=True
    ).decode().strip()

    try:
        return int(result)
    except ValueError:
        return 0


def orientation(command):
    direction = (
        command.get('to_direction')
        or command.get('direction')
        or command.get('orientation')
    )

    subprocess.run(
        "adb shell settings put system accelerometer_rotation 0",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    current_rotation = get_current_rotation()

    if direction == 'portrait':
        subprocess.run(
            "adb shell settings put system user_rotation 0",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    elif direction == 'landscape':
        subprocess.run(
            "adb shell settings put system user_rotation 1",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    elif direction == 'natural':
        subprocess.run(
            "adb shell settings put system user_rotation 0",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    elif direction == 'upsidedown':
        subprocess.run(
            "adb shell settings put system user_rotation 2",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    elif direction == 'rotate_right' or direction == 'right':
        new_rotation = (current_rotation + 1) % 4
        subprocess.run(
            f"adb shell settings put system user_rotation {new_rotation}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    elif direction == 'rotate_left' or direction == 'left':
        new_rotation = (current_rotation + 3) % 4
        subprocess.run(
            f"adb shell settings put system user_rotation {new_rotation}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    else:
        options = [0, 1, 2, 3]
        if current_rotation in options:
            options.remove(current_rotation)
        new_rotation = random.choice(options)

        subprocess.run(
            f"adb shell settings put system user_rotation {new_rotation}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    time.sleep(1)
    return True



def swipe(device, direction=None):
    if direction == 'up':
        device.swipe_ext("up", scale=0.9)
    elif direction == 'down':
        device.swipe_ext("down", scale=0.9)
    elif direction == 'right':
        device.swipe_ext("right", scale=0.9)
    else:

        device.swipe_ext("left", scale=0.9)
    time.sleep(1)
    return True


def multiple_selection(device, items):
    widget_info, sequential_info, map = get_widget_info(device)
    if len(items) == 0:
        print("No items to select.")
        return False
    if not execute_single_command(device, {'feature': items[0], 'action': 'long_click'}):
        return False
    if len(items) > 1:
        for item in items[1:]:
            command = {'feature': item, 'action': 'click'}
            if not execute_single_command(device, command):
                return False
    time.sleep(1)
    return True


def back(device):
    device.press('back')
    time.sleep(1)
    return True


def click(device, coor):
    device.click(coor[0], coor[1])
    time.sleep(1)
    return True


def long_click(device, coor):
    device.long_click(coor[0], coor[1], 1.5)
    time.sleep(1)
    return True


def set_text(device, rep_attr, input_text, index):
    ui_object = locate_ui_object(device, rep_attr, 'set_text', index)
    if ui_object is None:
        return False
    elif input_text == None:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choices(characters, k=10))
        input_text = random_string
    try:
        ui_object.set_text(input_text)
    except:
        return "fail locate the target"
    time.sleep(1)
    return True


def get_element(attribute_to_element_map, command):
    if isinstance(command['feature'], dict):
        return None

    element_list = attribute_to_element_map.get(command['feature'], [])
    if element_list != []:
        index = command.get('index', 0)
        if index >= len(element_list):
            return None
        else:
            element = element_list[index]
    else:
        element = None
    return element


def get_center_if_coordinate(s):
    pattern = r'^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$'
    match = re.match(pattern, s)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        centerX = (x1 + x2) // 2
        centerY = (y1 + y2) // 2
        return [centerX, centerY]
    else:
        return None


def get_widget_info(device):
    package_name = device.app_current()['package']
    attribute_to_element_map = {}
    widget_info, info, attribute_to_element_map = get_screen_information(device, attribute_to_element_map, package_name)
    return widget_info, info, attribute_to_element_map


def process_coordinate(device, command, ui_info):
    command['coordinate'] = None
    element = get_element(ui_info["element"], command)
    rep_attr = command.get('feature')
    action = command.get('action')
    index = command.get('index', 0)

    bounds_pattern = re.compile(r'^\[\d+,\d+\]\[\d+,\d+\]$')
    if bounds_pattern.match(rep_attr):
        x1, y1, x2, y2 = map(
        int,
        rep_attr.replace('[', '').replace(']', ',').split(',')[:-1])
        centerX = (x1 + x2) // 2
        centerY = (y1 + y2) // 2
        command['coordinate'] = [centerX, centerY]
        return True

    if element is None:
        if 'click' in action and index == 0:
            coor = get_center_if_coordinate(rep_attr)
            if coor:
                command['coordinate'] = coor
                return True
    else:
        coor = get_center_if_coordinate(element.attrib.get('bounds', ''))
        if coor:
            command['coordinate'] = coor
            return True
    if command['coordinate'] is None:
        try:
            ui_object = locate_ui_object(device, rep_attr, None, index)
            if ui_object and hasattr(ui_object, 'info') and 'bounds' in ui_object.info:
                bounds = ui_object.info['bounds']
                center_x = (bounds['left'] + bounds['right']) // 2
                center_y = (bounds['top'] + bounds['bottom']) // 2
                command["coordinate"] = [center_x, center_y]
        except Exception as e:
            pass
    return False if command['coordinate'] is None else True
