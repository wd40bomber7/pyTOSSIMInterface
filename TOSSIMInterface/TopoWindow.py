'''
Created on Oct 15, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
import io
import pygraphviz as pgv

class TopoWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #Variables
        self.drawingConnection = True
        #self.Bind(event, handler, source, id, id2)
        #setup
        super(TopoWindow,self).__init__(sim,"Topo Edit Window")
        #self.BackgroundColour()
        
        #Create menus
        self.topoFileMenu = wx.Menu()
        self.nodeMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.topoFileMenu);
        self.RegisterMenu(self.nodeMenu);
        #Append menus
        self.menuBar.Append(self.topoFileMenu,"Topo Files")
        self.menuBar.Append(self.nodeMenu,"Nodes")
        
        self.RebuildMenus()
        
        self.sketch = SketchWindow(self, -1)
        self.Show();
        

        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this TopoWindow. 
        '''
        menuBar = super(TopoWindow,self).RebuildMenus();
        
        self.topoDict = dict();
        #Make this an open/save/save as/new menu setup. Open should be a submenu
        #presetMenu
        for topoFile in self.sim.savedPresets.topoHistory:
            item = self.AddMenuItem(self.topoFileMenu, topoFile, self.__OnTopoSelect)
            self.topoDict[item.GetId()] = topoFile
        self.topoFileMenu.AppendSeparator();
        self.AddMenuItem(self.topoFileMenu, "Browse", self.__OnTopoBrowse)
        
        self.AddMenuItem(self.nodeMenu, "Delete Node", self.__OnNodeRemove)
        self.AddMenuItem(self.nodeMenu, "Add Node", self.__OnNodeAdd)
        
        return menuBar;
        
    def WindowType(self):
        return 3
    def RelayerTopo(self):
        '''
        Determines the draw positions of all nodes
        '''
        #First build the graphviz object with the list of connections
        graph=pgv.AGraph()
        for connection in self.topoData.connectionList:
            graph.add_edge(connection.fromNode, connection.toNode)
            
        graph.node_attr['shape'] = 'point'
        graph.layout() #Uses neato algorithm to create a node network
        memoryFile = io.BytesIO()
        graph.draw(memoryFile,"plain")
        
        layoutData = memoryFile.getvalue().splitlines(True)
        memoryFile.close()
        nodeLayout = dict() #The location of the different nodes
        
        #These are used to abstract the positions of the data into a % of the screen space
        nodeMinX = nodeMaxX = nodeMinY = nodeMaxY = 0
        nodeSet = False
        
        for line in layoutData:
            toParse = line.split(" ");
            if toParse[0] == "node":
                n = Node(int(toParse[1]),float(toParse[2]),float(toParse[3]))
                node = self.topoData.nodeDict[n.id]
                #This loops through all SimNode objects in the SimNode object for this node and adds them to this node's connections
                for on in node.connectNodes:
                    n.connections.append(on.myId);
                if not nodeSet:
                    nodeMinX = nodeMaxX = n.x
                    nodeMinY = nodeMaxY = n.y
                    nodeSet = True
                else:
                    nodeMinX = min(nodeMinX,n.x)
                    nodeMaxX = max(nodeMaxX,n.x)
                    nodeMinY = min(nodeMinY,n.y)
                    nodeMaxY = max(nodeMaxY,n.y)
                nodeLayout[n.id] = n
        for nodeId in nodeLayout:
            node = nodeLayout[nodeId]
            print "<" + str(node.x) + "," + str(node.y) + ">"
            if nodeMinX == nodeMaxX:
                node.x = .5
            else:
                node.x = (node.x - nodeMinX)/(nodeMaxX - nodeMinX) * .8 + .1
            if nodeMinY == nodeMaxY:
                node.y = .5
            else:
                node.y = (node.y - nodeMinY)/(nodeMaxY - nodeMinY) * .8 + .1
            
                
        self.sketch.connectedNodes = nodeLayout;
        self.Refresh()
        
    def LoadTopo(self):
        #try:
        self.topoData = Simulation.SimTopo(self.currentTopoFile)
        self.sim.savedPresets.addTopo(self.currentTopoFile)
        #except:
        #    self.topoData = None;
        #    self.displayError("Unable to load selected topo file.");
        #    return;
        self.RelayerTopo()
    #browse buttons
    def __OnNodeAdd(self, event):
        '''
        stub
        '''
    def __OnNodeRemove(self, event):
        '''
        stub
        '''
    def __OnTopoSelect(self, event):
        self.currentTopoFile = self.topoDict[event.GetId()]
        self.LoadTopo()
        
    def __OnTopoBrowse(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.currentTopoFile = dlg.GetPath()
            self.LoadTopo()
            #self.Sim.SavePresets()
        dlg.Destroy()
        
    #Editing handlers
    def __OnMouseMove(self, event):
        '''
        stub
        '''
    def __OnMouseLeave(self, event):
        '''
        stub
        '''
    def __OnMouseLeftDown(self, event):
        '''
        stub
        '''
    def __OnMouseLeftUp(self, event):
        '''
        stub
        '''
    def __OnMouseRightClick(self, event):
        '''
        stub
        '''
class Node(object):
    def __init__ (self, node,x=0,y=0):
        self.x = x
        self.y = y
        self.id = node
        self.connections = list()
class SketchWindow(wx.Window):

    def __init__ (self, parent,ID):

        wx.Window.__init__(self, parent, ID)
        
        n = Node(node=Simulation.SimNode(5))
        self.lonelyNodes = [n,n,n]
        self.connectedNodes = dict()
        
        self.Buffer = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)


    def InitBuffer(self):
        size=self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer=wx.EmptyBitmap(size.width,size.height)
        dc=wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.Drawnodes(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def Drawnodes(self,dc):
        width,height=self.GetClientSizeTuple()

        #First draw connections
        pen=wx.Pen('red',4)
        dc.SetPen(pen)
        for nodeId in self.connectedNodes:
            node = self.connectedNodes[nodeId]
            x1 = node.x*width
            y1 = node.y*height
            for neighborId in node.connections:
                neighborNode = self.connectedNodes[neighborId]
                x2 = neighborNode.x*width
                y2 = neighborNode.y*height
                dc.DrawLine(x1,y1,x2,y2) 
                
        #Second draw nodes
        pen=wx.Pen('blue',8)
        dc.SetPen(pen)
        for nodeId in self.connectedNodes:
            node = self.connectedNodes[nodeId]
            x = node.x*width
            y = node.y*height
            
            dc.DrawLabel(str(node.id),wx.Rect(x=x-25,y=y-20,width=45,height=20))
            dc.DrawCircle(x,y,3)   
            

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawnodes(dc)