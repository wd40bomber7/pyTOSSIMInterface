'''
Created on Oct 15, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
import io
import pygraphviz as pgv
import re
from Simulation import SimConnection

class TopoWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #setup
        super(TopoWindow,self).__init__(sim,"Topo Edit Window")
        #Variables
        self.topoData = None

        #Create menus
        self.topoFileMenu = wx.Menu()
        self.nodeMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.topoFileMenu);
        #self.RegisterMenu(self.nodeMenu);
        #Append menus
        self.menuBar.Append(self.topoFileMenu,"Topo Files")
        #self.menuBar.Append(self.nodeMenu,"Nodes")
        
        self.RebuildMenus()
        
        self.nodePanel = SketchWindow(self, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.nodePanel,1,wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        print "Registered panel"
        #Mouse events for editing
        self.nodePanel.Bind(wx.EVT_LEFT_DOWN, self.__OnMouseLeftDown, self.nodePanel)
        self.nodePanel.Bind(wx.EVT_LEFT_UP, self.__OnMouseLeftUp, self.nodePanel)
        self.nodePanel.Bind(wx.EVT_LEAVE_WINDOW, self.__OnMouseLeave, self.nodePanel)
        self.nodePanel.Bind(wx.EVT_MOTION, self.__OnMouseMove, self.nodePanel)
        self.nodePanel.Bind(wx.EVT_RIGHT_DOWN, self.__OnMouseRightClick, self.nodePanel)
        
        self.Show();
        

        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this TopoWindow. 
        '''
        menuBar = super(TopoWindow,self).RebuildMenus();
        
        self.topoDict = dict();
        #Make this an open/save/save as/new menu setup. Open should be a submenu
        #presetMenu
        for i in range(len(self.sim.savedPresets.topoHistory)-1,-1,-1):
            topoFile = self.sim.savedPresets.topoHistory[i]
            item = self.AddMenuItem(self.topoFileMenu, topoFile, self.__OnTopoSelect)
            self.topoDict[item.GetId()] = topoFile
        self.topoFileMenu.AppendSeparator();
        self.AddMenuItem(self.topoFileMenu, "Browse", self.__OnTopoBrowse)
        self.AddMenuItem(self.topoFileMenu, "New", self.__OnTopoNew)
        
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
        onlyOneWay = list()
        for connection in self.topoData.connectionList:
            firstCheck = connection.fromNode * 1000 + connection.toNode
            secondCheck = connection.toNode * 1000 + connection.fromNode
            if (firstCheck in onlyOneWay) or (secondCheck in onlyOneWay):
                continue;
            onlyOneWay.append(firstCheck)
            graph.add_edge(connection.fromNode, connection.toNode)
            
        graph.node_attr['shape'] = 'point'
        graph.layout() #Uses neato algorithm to create a node network

        #graph.draw("x.png")
        #graph.draw("x.txt","plain")
        drawnGraph = graph.draw(None,"plain")
        #print drawnGraph
        layoutData = drawnGraph.splitlines(True)
        nodeLayout = dict() #The location of the different nodes
        
        #These are used to abstract the positions of the data into a % of the screen space
        nodeMinX = nodeMaxX = nodeMinY = nodeMaxY = 0
        nodeSet = False
        
        for line in layoutData:
            toParse = re.findall("[\.\-\w]+",line)
            if len(toParse) > 3 and toParse[0] == "node":
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
            if nodeMinX == nodeMaxX:
                node.x = .5
            else:
                node.x = (node.x - nodeMinX)/(nodeMaxX - nodeMinX) * .8 + .1
            if nodeMinY == nodeMaxY:
                node.y = .5
            else:
                node.y = (node.y - nodeMinY)/(nodeMaxY - nodeMinY) * .8 + .1
            
                
        self.nodePanel.connectedNodes = nodeLayout;
        self.Refresh()
    def SaveTopo(self):
        #try:
            self.topoData.WriteTopoFile()
        #except:
        #    self.displayError("Failed to save topo file! Changes not saved.")
    def LoadTopo(self):
        try:
            self.topoData = Simulation.SimTopo(self.currentTopoFile)
            self.sim.savedPresets.addTopo(self.currentTopoFile)
        except:
            self.topoData = None;
            self.displayError("Unable to load selected topo file.");
            return;
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
    def __OnTopoNew(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a filename",
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.currentTopoFile = dlg.GetPath()
            try:
                self.topoData = Simulation.SimTopo()
                self.topoData.topoFileName = self.currentTopoFile
                self.topoData.AddConnection(1, 2)
                self.topoData.AddConnection(2, 1)
                self.topoData.WriteTopoFile()
                self.sim.savedPresets.addTopo(self.currentTopoFile)
                self.RebuildMenus()
            except:
                self.topoData = None
                self.displayError("Unable to create topo file there.")
                return;
            
            self.RelayerTopo()
        dlg.Destroy()        
    #Editing handlers
    def __OnMouseMove(self, event):
        if not self.nodePanel.nodeFrom is None:
            self.nodePanel.lineX = event.GetX()
            self.nodePanel.lineY = event.GetY()
            self.Refresh()
        
    def __OnMouseLeave(self, event):
        self.nodePanel.nodeFrom = None
        self.Refresh()
        
    def __OnMouseLeftDown(self, event):
        #print "Click at (" + str(event.GetX()) + "," + str(event.GetY()) + ")"
        if self.topoData is None:
            return
        
        selectedNode = None
        for pos in self.nodePanel.nodePositions:
            distanceSquared = (pos.x-event.GetX()) ** 2 + (pos.y-event.GetY()) ** 2
            if distanceSquared < 80:
                selectedNode = pos
        if selectedNode is None:
            return
        self.nodePanel.nodeFrom = selectedNode
        self.nodePanel.lineX = event.GetX()
        self.nodePanel.lineY = event.GetY()
        
    def __OnMouseLeftUp(self, event):
        if not self.nodePanel.nodeFrom is None:
            selectedNode = None
            for pos in self.nodePanel.nodePositions:
                distanceSquared = (pos.x-event.GetX()) ** 2 + (pos.y-event.GetY()) ** 2
                if distanceSquared < 80:
                    selectedNode = pos
            if (not selectedNode is None) and (selectedNode.id != self.nodePanel.nodeFrom.id):
                toSimNode = self.topoData.nodeDict[selectedNode.id]
                fromSimNode = self.topoData.nodeDict[self.nodePanel.nodeFrom.id]
                self.topoData.connectionList.append(SimConnection(fromSimNode.myId,toSimNode.myId))
                self.topoData.connectionList.append(SimConnection(toSimNode.myId,fromSimNode.myId))
                toSimNode.connectNodes.append(fromSimNode)
                fromSimNode.connectNodes.append(toSimNode)
            elif not selectedNode is None:
                print "Adding stand alone node"
                self.topoData.AddNode(self.topoData.nodeDict[self.nodePanel.nodeFrom.id])
            
            self.nodePanel.nodeFrom = None
            self.RelayerTopo()
            self.SaveTopo()
        
    def __OnMouseRightClick(self, event):
        #First see if they're removing a node
        if self.topoData is None:
            return
        selectedNode = None
        for pos in self.nodePanel.nodePositions:
            distanceSquared = (pos.x-event.GetX()) ** 2 + (pos.y-event.GetY()) ** 2
            if distanceSquared < 80:
                selectedNode = pos
        if not selectedNode is None:
            #Remove from connections list
            self.topoData.RemoveNode(selectedNode.id)
            self.RelayerTopo()
            self.SaveTopo()
            return
        
        
        p = Node(0,event.GetX(),event.GetY())
        selectedConnection = None
        for line in self.nodePanel.nodeConnections:
            dist = line.distToNode(p)
            if dist < 10:
                selectedConnection = line;
        if selectedConnection is None:
            return;
        self.topoData.RemoveConnection(selectedConnection.a.id, selectedConnection.b.id)
        self.RelayerTopo()
        self.SaveTopo()
        
class Node(object):
    def __init__ (self, node,x=0,y=0):
        self.x = x
        self.y = y
        self.id = node
        self.connections = list()
class Line(object):
    def __init__(self,a,b):
        self.a = a
        self.b = b
        
    def distToNode(self, n):
        #Find minimum distance from a point to this node. Equation from Stack overflow
        self.n = n
        lengthSquared = (self.a.x-self.b.x) ** 2 + (self.a.y-self.b.y) ** 2
        if lengthSquared == 0.0:
            return ((self.a.x-self.n.x) ** 2 + (self.a.y-self.n.y) ** 2) ** 0.5
        proj = (self.n.x - self.a.x)*(self.b.x - self.a.x) + (self.n.y - self.a.y)*(self.b.y - self.a.y)
        proj = proj/lengthSquared
        if proj < 0.0:
            return ((self.a.x-self.n.x) ** 2 + (self.a.y-self.n.y) ** 2) ** 0.5
        elif proj > 1.0:
            return ((self.b.x-self.n.x) ** 2 + (self.b.y-self.n.y) ** 2) ** 0.5
        projX = self.a.x + proj*(self.b.x - self.a.x)
        projY = self.a.y + proj*(self.b.y - self.a.y)
        return ((projX-self.n.x) ** 2 + (projY-self.n.y) ** 2) ** 0.5
        
class SketchWindow(wx.Panel):

    def __init__ (self, parent,ID):

        wx.Panel.__init__(self, parent, ID)
        
        n = Node(node=Simulation.SimNode(5))
        self.lonelyNodes = [n,n,n]
        self.connectedNodes = dict()
        self.nodePositions = list()
        self.nodeConnections = list()
        self.lineX = self.lineY = -1.0
        self.nodeFrom = None
        
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
        #self.Drawnodes(dc)
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
                self.nodeConnections.append(Line(Node(node.id,x1,y1),Node(neighborNode.id,x2,y2)))
                
        #Second draw nodes
        pen=wx.Pen('blue',8)
        dc.SetPen(pen)
        for nodeId in self.connectedNodes:
            node = self.connectedNodes[nodeId]
            x = node.x*width
            y = node.y*height
            
            dc.DrawLabel(str(node.id),wx.Rect(x=x-25,y=y-20,width=45,height=20))
            dc.DrawCircle(x,y,3) 
            #Store the position for later use  
            self.nodePositions.append(Node(nodeId,x,y))
            
        #Finally draw line
        if not self.nodeFrom is None:
            pen=wx.Pen('red',4)
            dc.SetPen(pen)
            dc.DrawLine(self.lineX,self.lineY,self.nodeFrom.x,self.nodeFrom.y)

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawnodes(dc)