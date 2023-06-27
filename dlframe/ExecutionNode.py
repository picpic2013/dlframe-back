from dlframe.CalculationNode import CalculationNode

class ExecutionNode:
    def __init__(self, node: CalculationNode) -> None:
        self.node = node
        self.in_degree = len(node.last_nodes)

        self.end_execution = False
        self.result = None

    def execute(self, config, node_dict):
        assert not self.end_execution, 'I do not know why this can happen'
        
        if self.node.is_root_node: # root nodes
            try:
                sub_config = config[self.node.node_manager.element_nodes[id(self.node)]]
                self.result = self.node.element_dict[sub_config]
            except:
                assert len(self.node.element_dict) == 1, f'no config for {self.node.node_manager.element_nodes[id(self.node)]}'
                self.result = next(iter(self.node.element_dict.values()))
            
        elif self.node.is_function: # function nodes
            args = [node_dict[id(sub_node)].result for sub_node in self.node.function_args]
            kwargs = {kw: node_dict[id(self.node.function_kwargs[kw])].result for kw in self.node.function_kwargs.keys()}
            if len(args) + len(kwargs) == len(self.node.last_nodes): # pure function node or init function node
                current_function = None
                try:
                    sub_config = config[self.node.node_manager.element_nodes[id(self.node)]]
                    current_function = self.node.element_dict[sub_config]
                except:
                    assert len(self.node.element_dict) == 1, f'no config for {self.node.node_manager.element_nodes[id(self.node)]}'
                    current_function = next(iter(self.node.element_dict.values()))
                self.result = current_function(*args, **kwargs)
            else: # class method node
                self.result = node_dict[id(self.node.last_nodes[0])].result(*args, **kwargs)
        else: # attr nodes
            self.result = getattr(node_dict[id(self.node.last_nodes[0])].result, self.node.attr_name)

        self.end_execution = True