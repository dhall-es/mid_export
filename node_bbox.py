import sd
from sd.api.sdbasetypes import float2, float4

class NodeBBox():
    def __init__(self, bbox: float4):
        self.x = bbox.x
        self.y = bbox.y
        self.width = bbox.z
        self.height = bbox.w

    def top_left(self):
        return float2(self.x, self.y)
    
    def top_right(self):
        return float2(self.x + self.width, self.y)
    
    def bottom_left(self):
        return float2(self.x, self.y + self.height)

    def bottom_right(self):
        return float2(self.x + self.width, self.y + self.height)
    
    def center(self):
        return float2(self.x + self.width / 2, self.y + self.height / 2)
    
def encapsulate(graphViewID: int, nodes):
    sdUiMgr = sd.getContext().getSDApplication().getUIMgr()
    minPos = None
    maxPos = None

    for i, node in enumerate(nodes):
        bbox = sdUiMgr.getGraphNodeBBox(graphViewID, node)

        if (i == 0):
            minPos = float2(bbox.x, bbox.y)
            maxPos = float2(bbox.x + bbox.z, bbox.y + bbox.w)
            continue
    
        minPos.x = min(minPos.x, bbox.x)
        minPos.y = min(minPos.y, bbox.y)

        maxPos.x = max(maxPos.x, bbox.x + bbox.z)
        maxPos.y = max(maxPos.y, bbox.y + bbox.w)
    
    width = maxPos.x - minPos.x
    height = maxPos.y - minPos.y

    return NodeBBox(float4(minPos.x, minPos.y, width, height))