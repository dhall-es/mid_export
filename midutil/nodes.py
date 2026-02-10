import sd
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdbasetypes import float2

def getNodesProperties(nodes, category, connectableOnly = True):
    '''
    Get the properties of the given nodes.

    :param list[SDNode] nodes: The list of nodes to get the properties from.
    :param int category: The category of properties to return.
    :param bool connectableOnly: Whether to only return connectable properties.
    :returns dict[SDNode, list[SDProperty]]: The nodes and their properties.
    '''
    
    # SDPropertyCategories:
    # Annotation = 0, Input = 1, Output = 2
    sdCategory = SDPropertyCategory(category)
    out = {}

    for node in nodes:
        properties = node.getProperties(sdCategory)

        if (not connectableOnly):
            # don't need to check if properties are connectable, skip
            
            # Note: this could cause a bug involving the difference between lists and SDArrays.
            # Should fix this later.
            out[node] = properties
            continue

        out[node] = []

        for prop in properties:
            # we only reach this if connectableOnly is true, so no need to check
            if (not prop.isConnectable()):
                continue

            out[node] += [prop]
    
    return out

def getNodeProperties(node, category, connectableOnly = True):
    '''
    Get the properties of the given node.

    :param SDNode node: The node to get the properties from.
    :param int category: The category of properties to return.
    \n  (Annotation = 0, Input = 1, Output = 2)\n
    :param bool connectableOnly: Whether to only return connectable properties.
    :returns list[SDProperty]: The nodes properties.
    '''

    return getNodesProperties([node], category, connectableOnly)[node]

def getConnectedInputNodes(nodes):
    '''
    Give a list of nodes and get the nodes connected to their inputs.

    :param list[SDNode] nodes: The list of nodes to get the connected input nodes of.
    :returns dict[SDNode, list[SDNode]]: The given nodes and the nodes connected to their inputs.
    '''

    node_prop_dict = getNodesProperties(nodes, 1, True)
    nodes = list(node_prop_dict.keys())
    out = {}

    for node in nodes:
        out[node] = []
        
        for prop in node_prop_dict[node]:
            connections = node.getPropertyConnections(prop)
        
            for connection in connections:
                out[node] += [connection.getInputPropertyNode()]
    
    return out

def getInputConnections(nodes):
    '''
    Give a list of nodes and get the connections for their inputs.

    :param list[SDNode] nodes: The list of nodes to get the connected input nodes of.
    :returns dict[SDNode, list[SDConnection]]: The given nodes and the connections for their inputs.
    '''

    node_prop_dict = getNodesProperties(nodes, 1, True)
    nodes = list(node_prop_dict.keys())
    out = {}

    for node in nodes:
        out[node] = []
        
        for prop in node_prop_dict[node]:
            connections = node.getPropertyConnections(prop)
        
            for connection in connections:
                out[node] += [connection]
    
    return out

def printNodeTypes(nodes):
    import re

    for node in nodes:
        # node definition ID (e.g. 'sbs::compositing::curve')
        id = node.getDefinition().getId()

        # separate the ID at every ::, then get the last element (e.g. 'curve')
        name = re.split('::', id)[-1]
        if (node.getReferencedResource()):
            print(node.getReferencedResource())
            print(node.getReferencedResource().getIdentifier())
            print(node.getReferencedResource().getUrl())

            continue

        print(name)

def printNodeDefinitionProperties(nodes):
    sdCategory = SDPropertyCategory(0)

    for node in nodes:
        properties = node.getDefinition().getProperties(sdCategory)
        for prop in properties:
            print(f"node {node.getDefinition().getLabel()}, prop {prop.getLabel()}, id = {prop.getId()}, value = {node.getPropertyValue(prop).get()}")

def getOutputNodes(selected_nodes):
    outputNodes = []

    for node in selected_nodes:
        id = node.getDefinition().getId()

        if (id == 'sbs::compositing::output'):
            outputNodes += [node]
    
    return outputNodes

