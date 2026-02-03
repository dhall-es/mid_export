import sd
from sd.api import SDUIMgr
from sd.api.qtforpythonuimgrwrapper import QtForPythonUIMgrWrapper

from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdbasetypes import float2

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot

from mid_export.midutil import nodes as nds
from mid_export.mid_export_toolbar import MainToolBar

from functools import partial

graphViewCreatedCallbackID:int = 0

def onNewGraphViewCreated(graphViewId: int, qtUIMgr: QtForPythonUIMgrWrapper,
                          sdUIMgr: SDUIMgr):
    if (not qtUIMgr):
        return
    
    print(f"New Graph View created. ID: {graphViewId}")

    toolbar = MainToolBar(graphViewId, qtUIMgr, sdUIMgr)
    qtUIMgr.addToolbarToGraphView(
        graphViewId,
        toolbar,
        icon = None,
        tooltip = "Mid Export"
    )
    

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
    ctx = sd.getContext()
    app = ctx.getSDApplication()
    qtUIMgr = app.getQtForPythonUIMgr()
    sdUIMgr = app.getUIMgr()

    if (qtUIMgr):
        global graphViewCreatedCallbackID
        graphViewCreatedCallbackID = qtUIMgr.registerGraphViewCreatedCallback(
            partial(onNewGraphViewCreated, qtUIMgr=qtUIMgr, sdUIMgr=sdUIMgr))

# If this function is present in your plugin,
# it will be called by Designer when unloading the plugin.
def uninitializeSDPlugin():
    pass