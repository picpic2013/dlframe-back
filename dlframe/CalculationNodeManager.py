import queue
from dlframe.CalculationNode import CalculationNode
from dlframe.ExecutionNode import ExecutionNode

class CalculationNodeManager:
    def __init__(self, parallel=False) -> None:
        self.nodes = {}
        self.element_nodes = {}
        self.class_type_name2node = {}

        self.latest_node = None
        self.parallel = parallel

    def _register_node(self, node: CalculationNode):
        self.nodes.setdefault(id(node), node)
        if not self.parallel:
            if self.latest_node is not None:
                self.latest_node > node
            self.latest_node = node
        return self

    def register_element(self, name: str, element_dict: dict=None, display: bool=True):
        if element_dict is None:
            element_dict = {}
        node = CalculationNode('__Element__' + str(element_dict), self, None, element_dict, is_root_node=True)
        self.class_type_name2node.setdefault(name, node)
        if not display:
            assert len(element_dict) == 1, 'you can only register one element if not display'
        else:
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
    
    def register(self, class_type_name, option_name=None, element=None, display=None):
        if type(option_name) == dict:
            if display is None:
                display = True
            return self.register_element(class_type_name, option_name, display)
        if element is not None:
            if option_name is None:
                option_name = element.__name__
            node = None
            if class_type_name not in self.class_type_name2node.keys():
                element_dict = {option_name: element}
                if class_type_name is None:
                    class_type_name = '__Element__' + str(element_dict)
                elif display is None:
                    display = True
                node = CalculationNode(class_type_name, self, None, element_dict, is_root_node=True)
                self.class_type_name2node.setdefault(class_type_name, node)
                if display:
                    self.element_nodes.setdefault(id(node), class_type_name)
            else:
                node = self.class_type_name2node[class_type_name]
                node.element_dict.setdefault(option_name, element)
                if display is not None:
                    assert False, f'The display option is only supported when registering for the first time. Please set the display option when registering element "{next(iter(node.element_dict.keys()))}".'
            return node
        def _warp_function_(raw_element, class_type_name=class_type_name, option_name=option_name, display=display, self=self):
            self.register(class_type_name, option_name, raw_element, display)
            return raw_element
        return _warp_function_
    
    def __getitem__(self, key):
        if key in self.class_type_name2node.keys():
            return self.class_type_name2node[key]
        return self.register(key, {}, display=True)