class CalculationNode:
    def __init__(self, attr_name: str, node_manager, last_node=None, element_dict: dict=None, is_root_node=False, *args, **kwargs) -> None:
        self.is_root_node = is_root_node
        
        self.attr_name = attr_name
        self.last_nodes = [last_node] if last_node is not None else []
        self.next_nodes = []
        self.node_manager = node_manager
        self.element_dict = element_dict
        
        self.is_function = False
        self.is_init_function = False
        self.function_args = []
        self.function_kwargs = {}

        self.node_manager.register_node(self)
    
    def __call__(self, *args, **kwargs):
        self.is_function = True

        if self.element_dict is not None and type(next(iter(self.element_dict.values()))) == type:
            for t in self.element_dict.values():
                assert type(t) == type, 'elements should have same type'
            self.is_init_function = True

        all_args = []
        for arg in args:
            if type(arg) is not CalculationNode:
                arg = CalculationNode(str(arg), self.node_manager, None, {str(arg): arg}, is_root_node=True)
            arg.next_nodes.append(self)
            self.last_nodes.append(arg)
            all_args.append(arg)

        all_kwargs = {}
        for kw in kwargs.keys():
            arg = kwargs[kw]
            if type(arg) is not CalculationNode:
                arg = CalculationNode(str(arg), self.node_manager, None, {str(arg): arg}, is_root_node=True)
            arg.next_nodes.append(self)
            self.last_nodes.append(arg)
            all_kwargs.setdefault(kw, arg)

        self.function_args = all_args
        self.function_kwargs = all_kwargs
        return self
    
    def __getattr__(self, __name: str):
        if __name == '__iter__':
            return None

        node = CalculationNode(__name, self.node_manager, self)
        self.next_nodes.append(node)
        return node
    
    def __getitem__(self, index):
        index_arg_node = index
        if type(index) != CalculationNode:
            index_arg_node = CalculationNode(str(index), self.node_manager, None, {str(index): index}, is_root_node=True)

        node = CalculationNode('__getitem__', self.node_manager, self)
        node.is_function = True

        index_arg_node.next_nodes.append(node)
        node.last_nodes.append(index_arg_node)

        node.function_args = [index_arg_node]

        self.next_nodes.append(node)
        return node
    
    def __gt__(self, other):
        self.next_nodes.append(other)
        other.last_nodes.append(self)
        return self

    def __lt__(self, other):
        self.last_nodes.append(other)
        other.next_nodes.append(self)
        return self