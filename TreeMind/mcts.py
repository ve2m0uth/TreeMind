import random
import math
from typing import List, Any


class TreeNode:
    def __init__(self, parent, depth):
        self.parent = parent
        self.depth = depth
        self.children = []
        self.visits = 1
        self.reward = 0
        self.image_path = ""
        self.command = []
        self.conversation = []


def select_node(node, times):
    ucb_list = []
    tau = 1.8
    for child in node.children:
        v = child.reward
        explore = math.sqrt(2.0 * math.log(times) / float(child.visits))
        score = v + 1 * explore
        ucb_list.append(score)
    m = max(ucb_list)
    exp_vals = [math.exp((u - m) / tau) for u in ucb_list]
    total = sum(exp_vals)
    if total == 0:
        probs = [1.0 / len(ucb_list)] * len(ucb_list)
    else:
        probs = [v / total for v in exp_vals]

    choice = random.choices(node.children, weights=probs, k=1)[0]
    return choice


def expand(node, possible_command):
    for i in range(len(possible_command)):
        new_node = TreeNode(node, node.depth + 1)
        new_node.conversation = [{"role": "user", "content": f"Successfully execute command {possible_command[i]}."}]
        new_node.command = node.command.copy()
        new_node.command.append(possible_command[i])
        node.children.append(new_node)


def backtrack(node: TreeNode):
    n = len(node.children)
    reward = 0
    for c in node.children:
        if 5.6 <= c.reward <= 8:
            reward += 4
        elif 3.2 <= c.reward < 5.6:
            reward += 1.6
        else:
            reward += 0.8
    reward = reward / n
    travel = node

    while travel is not None:
        travel.reward += reward
        travel = travel.parent