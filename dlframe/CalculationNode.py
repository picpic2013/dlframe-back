class CalculationNode:
    def __init__(self, attr_name: str, node_manager, last_node=None, element_dict: dict=None, is_root_node=False) -> None:
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

        self.node_manager._register_node(self)
    
    def __call__(self, *args, **kwargs):
        all_args = []
        for arg in args:
            if type(arg) is not CalculationNode:
                arg = CalculationNode(str(arg), self.node_manager, None, {str(arg): arg}, is_root_node=True)
            all_args.append(arg)

        all_kwargs = {}
        for kw in kwargs.keys():
            arg = kwargs[kw]
            if type(arg) is not CalculationNode:
                arg = CalculationNode(str(arg), self.node_manager, None, {str(arg): arg}, is_root_node=True)
            all_kwargs.setdefault(kw, arg)

        node = CalculationNode('function_call', self.node_manager, self)
        self.next_nodes.append(node)

        node.is_function = True
        node.function_args = all_args
        node.function_kwargs = all_kwargs

        if self.element_dict is not None and len(self.element_dict) > 0 and type(next(iter(self.element_dict.values()))) == type:
            for t in self.element_dict.values():
                assert type(t) == type, 'elements should have same type'
            node.is_init_function = True

        for arg in all_args:
            arg.next_nodes.append(node)
            node.last_nodes.append(arg)
        for kw in all_kwargs.keys(): 
            arg = kwargs[kw]
            arg.next_nodes.append(node)
            node.last_nodes.append(arg)
        
        return node
    
    def __getattr__(self, __name: str):
        if __name == '__iter__':
            return None

        node = CalculationNode(__name, self.node_manager, self)
        self.next_nodes.append(node)
        return node
    
    def __getitem__(self, index):
        node = CalculationNode('__getitem__', self.node_manager, self)
        self.next_nodes.append(node)
        
        return node(index)
    
    def __gt__(self, other):
        self.next_nodes.append(other)
        other.last_nodes.append(self)
        return self

    def __lt__(self, other):
        self.last_nodes.append(other)
        other.next_nodes.append(self)
        return self