import sd
from sd.api.sdhistoryutils import SDHistoryUtils
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdbasetypes import float2
from sd.api.sdvaluestring import SDValueString

from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Slot

from mid_export.midutil import nodes as nds
from mid_export.node_bbox import NodeBBox, encapsulate

class MainToolBar(QToolBar):
    def __init__(self, graphViewId, qtUIMgr, sdUIMgr):
        super(MainToolBar, self).__init__(parent = qtUIMgr.getMainWindow())

        self.__graphViewId = graphViewId
        self.__qtUIMgr = qtUIMgr
        self.__sdUIMgr = sdUIMgr
        self.__packMgr = sd.getContext().getSDApplication().getPackageMgr()

        wireORM = self.addAction("ORM")
        wireORM.triggered.connect(self.__wireORM)

    @Slot()
    def __instanceRgba(self):
        graph = self.__qtUIMgr.getCurrentGraph()

        # Some nodes like Merge RGBA nodes or Noise Functions aren't easily spawned,
        # as they're technically instances of another graph, captured within one node.
        
        # This means we have to load the package that contains the graph,
        # then spawn the graph as an Instance Node in our current graph.
        
        # Load the package
        absolute_path = 'C:/Program Files/Adobe/Adobe Substance 3D Designer/resources/packages/rgba_merge.sbs'
        package = self.__packMgr.loadUserPackage(absolute_path)

        # Get the resource (Graph) from the package
        resource = package.getChildrenResources(True)[0]

        # Instance the RGBA Merge Graph into the current graph as a node
        node = graph.newInstanceNode(resource)

        # Close the loaded user package so it doesn't clog the package manager view
        self.__packMgr.unloadUserPackage(package)

        if (node):
            self.__sdUIMgr.focusGraphNode(self.__graphViewId, node)
            return node
        
        return None
    
    def __addOutput(self, identifier:str = 'output', label:str = 'Output', group:str = '', description:str = ''):
        graph = self.__qtUIMgr.getCurrentGraph()

        node = graph.newNode('sbs::compositing::output')
        
        node.setAnnotationPropertyValueFromId('label', SDValueString.sNew(label))
        node.setAnnotationPropertyValueFromId('group', SDValueString.sNew(group))

        node.setAnnotationPropertyValueFromId('identifier', SDValueString.sNew(identifier))
        node.setAnnotationPropertyValueFromId('description', SDValueString.sNew(description))

        return node

    @Slot()
    def __wireORM(self):
        with SDHistoryUtils.UndoGroup("Auto ORM"):
            selected_nodes = self.__qtUIMgr.getCurrentGraph().getNodes()

            outputNodes = nds.getOutputNodes(selected_nodes)

            # If no output nodes are found, return
            if (len(outputNodes) <= 0):
                return

            annotation = SDPropertyCategory(0)

            # ORM nodes will be found via identifier.
            orm = [None, None, None]
            output_group = ''

            for node in outputNodes:
                identifier = node.getPropertyValueFromId('identifier', annotation).get()
                
                # Get the group name from the node for later usage in ORM
                isgroup = node.getPropertyValueFromId('group', annotation)
                if (isgroup and isgroup.get() != ''):
                    output_group = isgroup.get()

                match identifier:
                    case 'ambientocclusion':
                        orm[0] = node
                    case 'roughness':
                        orm[1] = node
                    case 'metallic':
                        orm[2] = node
                    case _:
                        continue
            
            noEmptySlots = [node for node in orm if node is not None]
            
            # If no nodes were found with the identifiers, return
            if (len(noEmptySlots) <= 0):
                return
            # Otherwise, remove all cases of None in the array
            else:
                orm = noEmptySlots

            rgba = self.__instanceRgba()
            rgba_input_props = nds.getNodeProperties(rgba, 1)
            
            # Get the input connections for each ORM output node.
            # These are stored in a dictionary with each output node as a key, 
            # and the value being a list containing the connections.
            # (in this case, there is only one connection per node)
            connections_dict = nds.getInputConnections(orm)

            for i, node in enumerate(orm):
                # If the node is invalid or has no input connections, skip
                if (not node or len(connections_dict[node]) <= 0):
                    continue

                # Get the first (and only) connection of the current output node,
                # And get the node / properties connected with it.
            
                # For connections:
                # The input property & node are at the start of the connection.
                # The output property & node are where the connection ends/leads into.
                connect_prop = connections_dict[node][0].getInputProperty()
                connect_node = connections_dict[node][0].getInputPropertyNode()

                # For nodes:
                # The input property is what goes into the node.
                # The output property is what comes out of the pevious node.
                #
                # i.e. sdOutputNode.newPropertyConnection(sdOutputProperty, sdInputPropertyNode, sdInputProperty)
                #
                # This is confusing since this is the literal opposite definition of connections' inputs/outputs
                connect_node.newPropertyConnectionFromId(connect_prop.getId(), rgba, rgba_input_props[i].getId())

            # Move the node to an appropriate position
            # Start by getting a bounding box surrounding all of the original O/R/M output nodes
            bbox = encapsulate(self.__graphViewId, orm)

            # Set the position of the RGBA Merge to the center right of this box (+250 for spacing)
            rgba_pos = float2(bbox.top_right().x + 250, bbox.center().y)
            rgba.setPosition(rgba_pos)

            # Create an Output Node with appropriate identifier/label/group/position
            op_node = self.__addOutput(identifier='ORM', label='ORM', group=output_group)
            op_node.setPosition(float2(rgba_pos.x + 250, rgba_pos.y))

            # Connect the RGBA node to the Output Node
            rgba_output_prop = nds.getNodeProperties(rgba, 2)[0]
            op_input_prop = nds.getNodeProperties(op_node, 1)[0]
            rgba.newPropertyConnectionFromId(rgba_output_prop.getId(), op_node, op_input_prop.getId())

            # Focus the Output node
            self.__sdUIMgr.focusGraphNode(self.__graphViewId, op_node)