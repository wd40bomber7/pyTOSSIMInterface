'''
Created on Nov 6, 2012

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
        self.readPosition = 0; #the line in the list of all received lines this node is reading at
        #Create menus
        self.topoExpirationMenu = wx.Menu()
        self.nodeMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.topoExpirationMenu);
        #self.RegisterMenu(self.nodeMenu);
        #Append menus
        self.menuBar.Append(self.topoExpirationMenu,"Message Expiration")
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
        
        #Update timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateDisplay, self.timer)
        self.timer.Start(100);
        
        self.Show();
        

        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this TopoWindow. 
        '''
        menuBar = super(TopoWindow,self).RebuildMenus();
        
        self.expireDict = dict();

        item = self.AddMenuItem(self.topoExpirationMenu, ".5", self.__OnTopoSelect)
        self.expireDict[item.GetId()] = .5
        item = self.AddMenuItem(self.topoExpirationMenu, "1", self.__OnTopoSelect)
        self.expireDict[item.GetId()] = 1
        item = self.AddMenuItem(self.topoExpirationMenu, "2", self.__OnTopoSelect)
        self.expireDict[item.GetId()] = 2
        item = self.AddMenuItem(self.topoExpirationMenu, "5", self.__OnTopoSelect)
        self.expireDict[item.GetId()] = 5
        item = self.AddMenuItem(self.topoExpirationMenu, "60", self.__OnTopoSelect)
        self.expireDict[item.GetId()] = 60
        
        
        RelayerTopo() #Do this here so every time your menus are forced to update so is the topo window
        return menuBar;
        
    def WindowType(self):
        return 5
    def RelayerTopo(self):
        '''
        Determines the draw positions of all nodes
        '''
        #First build the graphviz object with the list of connections
        graph=pgv.AGraph()
        onlyOneWay = list()
        #Add each connection only once
        for connection in self.topoData.connectionList:
            firstCheck = connection.fromNode * 1000 + connection.toNode
            secondCheck = connection.toNode * 1000 + connection.fromNode
            if (firstCheck in onlyOneWay) or (secondCheck in onlyOneWay):
                continue;
            onlyOneWay.append(firstCheck)
            graph.add_edge(connection.fromNode, connection.toNode)
            
        graph.node_attr['shape'] = 'point'
        graph.layout() #Uses neato algorithm to create a node network

        #graph.draw("x.png") #This serves no purpose except for debugging
        drawnGraph = graph.draw(None,"plain")
        #print drawnGraph
        layoutData = drawnGraph.splitlines(True)
        nodeLayout = dict() #The location of the different nodes
        
        #These are used to abstract the positions of the data into a % of the screen space
        nodeMinX = nodeMaxX = nodeMinY = nodeMaxY = 0
        nodeSet = False
        
        #Parse the plain text file only for node positions.
        for line in layoutData:
            toParse = re.findall("[\.\-\w]+",line) #Split on spaces, - or . Combine consecutive delimiters
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
        #Use collected information to normalize nodes to be between .1 and .9 position
        #This means they'll be between 10% of the width/height and 90% when being displayed
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
        #Find the best positions for the windows
        for nodeId in nodeLayout:
            node = nodeLayout[nodeId]
            #Find the average location of the "cloud" of nearby nodes
            avgX = 0.0
            avgY = 0.0
            cloudCount = 0.0
            for otherId in nodeLayout:
                if otherId == nodeId:
                    continue
                otherNode = nodeLayout[otherId]
                avgX += otherNode.x
                avgY += otherNode.y
                cloudCount += 1
            avgX /= cloudCount
            avgY /= cloudCount
            #Now create a vector pointing away from that average position
            #this should point away from the majority of nearby nodes
            vectX = node.x-avgX + .0001 #we add .0001 to guarantee there is never length=0
            vectY = node.y-avgY
            #normalize the vector
            vectLength = ((vectX ** 2.0) + (vectY ** 2.0)) ** .5
            vectX /= vectLength
            vectY /= vectLength
            
            #The larger one decides the primary placement of the box
            if abs(vectX) > abs(vectY):
                node.myWindow.x = -1 if vectX < 0 else 1
                node.myWindow.y = vectY-.5
            else:
                node.myWindow.x = vectX-.5
                node.myWindow.y = -1 if vectY < 0 else 1
        
        self.nodePanel.connectedNodes = nodeLayout;
        self.Refresh()
    def UpdateDisplay(self, event):
        newData = self.sim.simulationState.messages.RetrieveFilteredList(list(),list(),list(),self.readPosition)
        self.readPosition = newData[0]
        #for message in newData[1]:
            
    def LoadTopo(self):
        try:
            self.topoData = Simulation.SimTopo(self.currentTopoFile)
            self.sim.savedPresets.addTopo(self.currentTopoFile)
        except:
            self.topoData = None;
            self.displayError("Unable to load selected topo file.");
            return;
        self.RelayerTopo()
            
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
class NodeWindow(object):
    def __init__(self,x=0,y=0):
        #The x and y are -1 to 1 and are multiplied by the width/height and added to the node's position to find the top left corner of the window
        self.x = x
        self.y = y
        self.messages = list()
        self.posMessages = list()
        self.posExpirations = list()
        for i in xrange(0,10):
            self.posMessages.append("")
            self.posExpirations.append(0)
    def mapMessagesToLines(self,dc):
        highestPosMessage = -1
        for i in xrange(0,10):
            if self.posExpirations[i] > 0:
                highestPosMessage = i
        
class Node(object):
    def __init__ (self, node,x=0,y=0):
        self.x = x
        self.y = y
        self.id = node
        self.connections = list()
        self.myWindow = NodeWindow()

class Line(object):
    def __init__(self,a,b):
        self.a = a
        self.b = b
        
    def distToNode(self, n):
        #Find minimum distance from a line to this node. Equation from Stack overflow
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
            
        #Third draw windows
        #process of drawing windows.
        #1. Break text into lines based off of allowed length
        #2. Draw a solid white background for the total actual lines
        #3. Draw a thick border including a thin title bar
        #4. Draw a think border between slot messages and regular messages 
        #5. Color alternating message boxes in a grey color
        #6. Draw messages in black over the background

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawnodes(dc)