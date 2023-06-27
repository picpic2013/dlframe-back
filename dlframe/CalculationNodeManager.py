import queue
from dlframe.CalculationNode import CalculationNode
from dlframe.ExecutionNode import ExecutionNode

class CalculationNodeManager:
    def __init__(self, parallel=False) -> None:
        self.nodes = {}
        self.element_nodes = {}

        self.latest_node = None
        self.parallel = parallel

    def register_node(self, node: CalculationNode):
        self.nodes.setdefault(id(node), node)
        if not self.parallel:
            if self.latest_node is not None:
                self.latest_node > node
            self.latest_node = node
        return self

    def register_element(self, name: str, element_dict: dict=None, *args, **kwargs):
        if element_dict is None:
            element_dict = {}
        node = CalculationNode('__Element__' + str(element_dict), self, None, element_dict, is_root_node=True, *args, **kwargs)
        self.element_nodes.setdefault(id(node), name)
        return node

    def inspect(self):
        name_dict = {node_name: list(self.nodes[node_id].element_dict.keys()) for node_id, node_name in self.element_nodes.items()}
        return name_dict

    def execute(self, config: dict, max_size=0):
        node_dict = {name: ExecutionNode(node) for name, node in self.nodes.items()}
        node_queue = queue.Queue(maxsize=max_size)
        for name, node in node_dict.items():
            if node.in_degree == 0:
                node_queue.put(name)

        while not node_queue.empty():
            current_node_name = node_queue.get()
            current_node = node_dict[current_node_name]

            current_node.execute(config, node_dict)
            
            for next_node in current_node.node.next_nodes:
                next_node_name = id(next_node)
                node_dict[next_node_name].in_degree -= 1
                if node_dict[next_node_name].in_degree == 0:
                    node_queue.put(next_node_name)
        return self