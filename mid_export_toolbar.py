import sd
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdbasetypes import float2
from sd.api.sdvaluebool import SDValueBool

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

        printNodeTypes = self.addAction("Node Types")
        printNodeTypes.triggered.connect(self.__printNodeTypes)

        wireORM = self.addAction("ORM")
        wireORM.triggered.connect(self.__wireORM)

        wireRGBA = self.addAction("RGBA")
        wireRGBA.triggered.connect(self.__wireRGBA)

    @Slot()
    def __printNodeTypes(self):
        nodes = self.__qtUIMgr.getCurrentGraphSelectedNodes()
        nds.printNodeTypes(nodes)

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
    
    @Slot()
    def __wireRGBA(self):
        rgba = self.__instanceRgba()
        rgba_props = nds.getNodeProperties([rgba], 1)[rgba]

        graph = self.__qtUIMgr.getCurrentGraph()

        for i, prop in enumerate(rgba_props):
            uniform = graph.newNode('sbs::compositing::uniform')
            uniform.setInputPropertyValueFromId('colorswitch', SDValueBool.sNew(False))

            # print(nds.getNodeProperties([uniform], 2)[uniform][0].getId())
            output_prop = uniform.getPropertyFromId('unique_filter_output', SDPropertyCategory(2))

            # connection = uniform.newPropertyConnection(output_prop, prop, rgba)
            connection = uniform.newPropertyConnectionFromId(output_prop.getId(), rgba, prop.getId())
            print(f"Connect Property {output_prop.getLabel()} ({i}) to {prop.getLabel()}")

            

    @Slot()
    def __wireORM(self):
        # Find ORM Outputs from selected nodes
        selected_nodes = self.__qtUIMgr.getCurrentGraphSelectedNodes()

        # If no nodes are selected, search all nodes
        if (len(selected_nodes) <= 0):
            selected_nodes = self.__qtUIMgr.getCurrentGraph().getNodes()

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
        
        # If no nodes were found with the identifiers, return
        noEmptySlots = [node for node in orm if node is not None]
        if (len(noEmptySlots) <= 0):
            return
        else:
            orm = noEmptySlots

        rgba = self.__instanceRgba()
        rgba_props = nds.getNodeProperties([rgba], 1)[rgba]
        
        # Get the input connections for each ORM output node.
        # These are stored in a dictionary with each output node as a key, 
        # and the value being a list containing the connections.
        # (in this case, there is only one connection per node)
        connections_dict = nds.getInputConnections(orm)

        for i, node in enumerate(orm):
            if (not node or len(connections_dict[node]) <= 0):
                continue

            # The input property & node are at the start of the connection.
            # The output property & node are where the connection ends/leads into.
            input_prop = connections_dict[node][0].getInputProperty()
            input_node = connections_dict[node][0].getInputPropertyNode()

            print(f"Connecting Property {input_prop} {input_prop.getLabel()} to Property {rgba_props[i]} {rgba_props[i].getLabel()}")
            connection = input_node.newPropertyConnectionFromId(input_prop.getId(), rgba, rgba_props[i].getId())
        
        bbox = encapsulate(self.__graphViewId, orm)
        rgba.setPosition(float2(bbox.top_right().x + 150, bbox.center().y))
        self.__sdUIMgr.focusGraphNode(self.__graphViewId, rgba)