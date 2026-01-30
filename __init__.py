import sd
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdbasetypes import float2

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot

from mid_export.midutil import nodes as nds

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
    pass

# If this function is present in your plugin,
# it will be called by Designer when unloading the plugin.
def uninitializeSDPlugin():
    pass

def getQTUIMgr():
    return sd.getContext().getSDApplication().getQtForPythonUIMgr()

def getSDUIMgr():
    return sd.getContext().getSDApplication().getUIMgr()

def create_menu(menuName):
    uiMgr = getQTUIMgr()

    preexisting_menu = uiMgr.findMenuFromObjectName(menuName)

    if (preexisting_menu):
        uiMgr.deleteMenu(menuName)

    # Create a new menu.
    menu = uiMgr.newMenu(menuTitle = "Mid Export", objectName = menuName)

    # Create a new action.
    a_node_types = QAction(parent = menu, text = "Print Selected Node Types", triggered = printSelectedNodeTypes)
    a_node_inputs = QAction(parent = menu, text = "Print Nodes Connected To Inputs", triggered = printConnectedInputs)
    a_node_defprop = QAction(parent = menu, text = "Print Definition Properties", triggered = printDefProps)
    a_node_orm = QAction(parent = menu, text = "Generate ORM Outputs", triggered = autoWireORM)

    # Add the action to the menu.
    menu.addAction(a_node_types)
    menu.addAction(a_node_inputs)
    menu.addAction(a_node_defprop)
    menu.addAction(a_node_orm)

@Slot()
def printSelectedNodeTypes():
    uiMgr = getQTUIMgr()

    current_selected = uiMgr.getCurrentGraphSelectedNodes()
    # nds.printNodeTypes(current_selected)
    for node in current_selected:
        print(node.getDefinition().getId())

@Slot()
def printConnectedInputs():
    uiMgr = getQTUIMgr()

    nodes = uiMgr.getCurrentGraphSelectedNodes()
    connected_nodes = nds.getConnectedInputNodes(nodes)
    nodes = list(connected_nodes.keys())

    for node in nodes:
        print(f"Node {node.getDefinition().getLabel()}:")
        nds.printNodeTypes(connected_nodes[node])

@Slot()
def printDefProps():
    uiMgr = getQTUIMgr()

    nodes = uiMgr.getCurrentGraphSelectedNodes()
    nds.printNodeDefinitionProperties(nodes)

@Slot()
def autoWireORM():
    uiMgr = getQTUIMgr()

    selected_nodes = uiMgr.getCurrentGraphSelectedNodes()
    outputNodes = nds.getOutputNodes(selected_nodes)

    if (len(outputNodes) <= 0):
        return

    annotation = SDPropertyCategory(0)

    # ORM nodes will be found via identifier.
    orm = [None, None, None]

    for node in outputNodes:
        identifier = node.getPropertyValueFromId('identifier', annotation).get()
        match identifier:
            case 'ambientocclusion':
                orm[0] = node
            case 'roughness':
                orm[1] = node
            case 'metallic':
                orm[2] = node
            case _:
                continue
    
    getNodeBounds(orm)

    new = uiMgr.getCurrentGraph().newNode('sbs::compositing::uniform')
    getSDUIMgr().focusGraphNode(0, new)

def getNodeBounds(nodes):
    minimum = nodes[0].getPosition()
    maximum = nodes[0].getPosition()
    
    for node in nodes:
        pos = node.getPosition()

        minimum.x = min(minimum.x, pos.x)
        minimum.y = min(minimum.y, pos.y)

        maximum.x = max(maximum.x, pos.x)
        maximum.y = max(maximum.y, pos.y)
    
    median = float2((minimum.x + maximum.x) / 2, (minimum.y + maximum.y) / 2)

    out = {
        'min':minimum,
        'max':maximum,
        'median':median
    }

    return out

def getMeanPosition(nodes):
    total = float2(0, 0)
    for node in nodes:
        total.x += node.getPosition().x
        total.y += node.getPosition().y

    total.x /= len(nodes)
    total.y /= len(nodes)

    return total

def printNodeNames(nodes):
    for node in nodes:
        print(node.getDefinition().getLabel())

create_menu("mid_export.main_menu")