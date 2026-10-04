import random
import math
from typing import List, Any


class TreeNode:
    def __init__(self, parent, depth):
        self.parent = parent
        self.depth = depth
        self.children = []
        self.visit_count = 0
        self.value_sum = 0.0
        self.immediate_value = None
        self.image_path = ""
        self.command = []
        self.conversation = []
        self.dead_end = False
        self.execution_status = "pending"

    @property
    def mean_value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / float(self.visit_count)

    def record_value(self, value):
        self.visit_count += 1
        self.value_sum += value


def select_node(node: TreeNode):
    selectable_children = [child for child in node.children if not child.dead_end]
    if not selectable_children:
        return None

    unvisited_children = [child for child in selectable_children if child.visit_count == 0]
    if unvisited_children:
        return random.choice(unvisited_children)

    parent_visits = max(1, node.visit_count)
    ucb_list = []
    for child in selectable_children:
        explore = math.sqrt(2.0 * math.log(parent_visits) / float(child.visit_count))
        score = child.mean_value + explore
        ucb_list.append(score)
    m = max(ucb_list)
    branch_scale = math.sqrt(len(selectable_children))
    exp_vals = [math.exp((u - m) / branch_scale) for u in ucb_list]
    total = sum(exp_vals)
    if total == 0:
        probs = [1.0 / len(ucb_list)] * len(ucb_list)
    else:
        probs = [v / total for v in exp_vals]

    choice = random.choices(selectable_children, weights=probs, k=1)[0]
    return choice


def expand(node: TreeNode, possible_command):
    for i in range(len(possible_command)):
        new_node = TreeNode(node, node.depth + 1)
        new_node.conversation = []
        new_node.command = node.command.copy()
        new_node.command.append(possible_command[i])
        node.children.append(new_node)
    # node.command = []

def backtrack(node: TreeNode, value):
    temp = node
    while temp is not None:
        temp.record_value(value)
        temp = temp.parent

