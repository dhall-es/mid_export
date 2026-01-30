import sd
from sd.api.sdproperty import SDPropertyCategory
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
    print("mid_export initialized successfully")

# If this function is present in your plugin,
# it will be called by Designer when unloading the plugin.
def uninitializeSDPlugin():
    pass

def getUIMgr():
    return sd.getContext().getSDApplication().getQtForPythonUIMgr()

def create_menu(menuName):
    uiMgr = getUIMgr()

    preexisting_menu = uiMgr.findMenuFromObjectName(menuName)

    if (preexisting_menu):
        uiMgr.deleteMenu(menuName)

    # Create a new menu.
    menu = uiMgr.newMenu(menuTitle = "Mid Export", objectName = menuName)

    # Create a new action.
    a_node_types = QAction(parent = menu, text = "Print Selected Node Types", triggered = printSelectedNodeTypes)
    a_node_inputs = QAction(parent = menu, text = "Print Nodes Connected To Inputs", triggered = printConnectedInputs)

    # Add the action to the menu.
    menu.addAction(a_node_types)
    menu.addAction(a_node_inputs)

@Slot()
def printSelectedNodeTypes():
    uiMgr = getUIMgr()

    current_selected = uiMgr.getCurrentGraphSelectedNodes()
    printNodeTypes(current_selected)

@Slot()
def printConnectedInputs():
    uiMgr = getUIMgr()

    nodes = uiMgr.getCurrentGraphSelectedNodes()
    connected_nodes = getConnectedInputNodes(nodes)
    nodes = list(connected_nodes.keys())

    for node in nodes:
        print(f"Node {node.getDefinition().getLabel()}:")
        printNodeTypes(connected_nodes[node])

def printNodeNames(nodes):
    for node in nodes:
        print(node.getDefinition().getLabel())

def printNodeTypes(nodes):
    import re

    for node in nodes:
        # node definition ID (e.g. 'sbs::compositing::curve')
        id = node.getDefinition().getId()

        # separate the ID at every ::, then get the last element (e.g. 'curve')
        name = re.split('::', id)[-1]

        print(name)

def getNodeProperties(nodes, category, connectableOnly = True):
    '''
    Get the properties of the given nodes.

    :param list[SDNode] nodes: The list of nodes to get the properties from.
    :param list[SDPropertyCategory] category: The category of properties to return.
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
            out[node] = properties
            continue

        out[node] = []

        for prop in properties:
            # we only reach this if connectableOnly is true, so no need to check
            if (not prop.isConnectable()):
                continue

            out[node] += [prop]
    
    return out
            
def getConnectedInputNodes(nodes):
    '''
    Give a list of nodes and get the nodes connected to their inputs.

    :param list[SDNode] nodes: The list of nodes to get the connected input nodes of.
    :returns dict[SDNode, list[SDNode]]: The given nodes and the nodes connected to their inputs.
    '''

    node_prop_dict = getNodeProperties(nodes, 1, True)
    nodes = list(node_prop_dict.keys())
    out = {}

    for node in nodes:
        out[node] = []
        
        for prop in node_prop_dict[node]:
            connections = node.getPropertyConnections(prop)
        
            for connection in connections:
                out[node] += [connection.getInputPropertyNode()]
    
    return out

create_menu("mid_export.main_menu")