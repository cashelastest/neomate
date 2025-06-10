class NodeAttrError(Exception):
    def __init__(self, node_name, attr_name, message):
        self.node_name = node_name
        self.attr_name = attr_name
        self.message = message
        full_message = f"NodeAttrError in {node_name} model {attr_name} attribute.\n" + message
        super().__init__(full_message)
        
    def __str__(self):
        return self.message

