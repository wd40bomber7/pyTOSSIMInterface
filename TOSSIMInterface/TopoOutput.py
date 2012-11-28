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


class TopoOutput(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #setup
        super(TopoOutput,self).__init__(sim,"Topo Edit Window")
        #Variables
        self.excludedChannels = list() #A list of channels not being shown
        self.topoData = None
        self.readPosition = 0; #the line in the list of all received lines this node is reading at
        #Create menus
        self.windowSizeMenu = wx.Menu()
        self.channelsMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.windowSizeMenu)
        self.RegisterMenu(self.channelsMenu)
        #self.RegisterMenu(self.nodeMenu);
        #Append menus
        self.menuBar.Append(self.channelsMenu,"Channels");
        self.menuBar.Append(self.windowSizeMenu,"Topo Window Size")
        #self.menuBar.Append(self.nodeMenu,"Nodes")
        
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
        
        self.RebuildMenus()
        
        #Update timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateDisplay, self.timer)
        self.timer.Start(100)
        
        self.Show()
        

        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this TopoOutput. 
        '''
        menuBar = super(TopoOutput,self).RebuildMenus();
        
        self.windowDict = dict()
        self.channelDict = dict()
        
        #channelsMenu
        self.channelCount = len(self.sim.selectedOptions.channelList)
        for channel in self.sim.selectedOptions.channelList:
            item = self.AddMenuItem(self.channelsMenu, channel, self.__OnChannel, not channel in self.excludedChannels)
            self.channelDict[item.GetId()] = channel

        #Window size menu
        item = self.AddMenuItem(self.windowSizeMenu,"100", self.__OnWindowSizeChange)
        self.windowDict[item.GetId()] = 100
        item = self.AddMenuItem(self.windowSizeMenu,"200", self.__OnWindowSizeChange)
        self.windowDict[item.GetId()] = 200
        item = self.AddMenuItem(self.windowSizeMenu,"300", self.__OnWindowSizeChange)
        self.windowDict[item.GetId()] = 300
        item = self.AddMenuItem(self.windowSizeMenu,"500", self.__OnWindowSizeChange)
        self.windowDict[item.GetId()] = 500
        
        
        
        self.RelayerTopo() #Do this here so every time your menus are forced to update so is the topo window
        return menuBar;
        
    def WindowType(self):
        return 5
    def RelayerTopo(self):
        '''
        Determines the draw positions of all nodes
        '''
        if self.sim.simulationState.currentTopo is None:
            return
        self.topoData = self.sim.simulationState.currentTopo
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
                dist = ((node.x-otherNode.x) ** 2 + (node.y-otherNode.y) ** 2) ** .5
                if dist > .3:
                    continue
                
                avgX += otherNode.x
                avgY += otherNode.y
                cloudCount += 1
            if cloudCount > 0:
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
                node.myWindow.x = -1 if vectX < 0 else 0
                node.myWindow.y = vectY*.5 - .5
            else:
                node.myWindow.x = vectX*.5 - .5
                node.myWindow.y = -1 if vectY < 0 else 0
        self.nodePanel.connectedNodes = nodeLayout;
        self.Refresh()
    def UpdateDisplay(self, event):
        newData = self.sim.simulationState.messages.RetrieveFilteredList(list(),self.excludedChannels,list(),self.readPosition)
        self.readPosition = newData[0]
        for message in newData[1]:
            node = self.nodePanel.connectedNodes[message.nodeId]
            if message.topoSlot < 0:
                if len(node.myWindow.messages) >= 3:
                    del node.myWindow.messages[0]
                node.myWindow.messages.append(message.messageText)
            else:
                node.myWindow.fixedMessages[message.topoSlot] = message.messageText
                
        if len(newData[1]) > 0:
            self.Refresh()
            
    def LoadTopo(self):
        try:
            self.topoData = Simulation.SimTopo(self.currentTopoFile)
            self.sim.savedPresets.addTopo(self.currentTopoFile)
        except:
            self.topoData = None;
            self.displayError("Unable to load selected topo file.");
            return;
        self.RelayerTopo()
          
    #Menus
    #Window size menu
    def __OnWindowSizeChange(self, event):
        size = self.windowDict[event.GetId()]
        self.nodePanel.windowWidth = size
        self.Refresh()
        
    #For the channel Menu
    def __OnChannel(self, event):
        channel = self.channelDict[event.GetId()]
        if channel in self.excludedChannels:
            self.excludedChannels.remove(channel)
        else:
            self.excludedChannels.append(channel)
        for nodeId in self.nodePanel.connectedNodes:
            node = self.nodePanel.connectedNodes[nodeId]
            node.myWindow.messages = list()
            for i in xrange(0,len(node.myWindow.fixedMessages)):
                node.myWindow.fixedMessages[i] = ""
        self.readPosition = 0
        self.UpdateDisplay(None)
        self.Refresh()
        
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
        #The top 3 regular messages are displayed in the order they are received
        #Fixed messages are displayed in the order they specify and are above the regular messages
        self.messages = list()
        self.fixedMessages = list()
        #These contain two element arrays. The text of the line followed by the color
        self.messageLines = list()
        self.fixedMessageLines = list()
        
        for i in xrange(0,10):
            self.fixedMessages.append("")
            
    def mapMessagesToLines(self,dc,maxLength):
        #Calculate for regular messages
        self.__mapMessageToLineList(dc,maxLength,self.messages,self.messageLines)
        #Calculated for fixed position messages
        highestPosMessage = -1
        fixedLines = list()
        for i in xrange(0,10):
            if len(self.fixedMessages[i]) > 0:
                highestPosMessage = i
        #print "Highest pos: " + str(highestPosMessage)
        for i in xrange(0,highestPosMessage+1):
            fixedLines.append(self.fixedMessages[i])
        self.__mapMessageToLineList(dc,maxLength,fixedLines,self.fixedMessageLines)
        return (len(self.fixedMessageLines),len(self.messageLines),dc.GetTextExtent("A")[1])
        
    def __mapMessageToLineList(self,dc,maxLength,messageList,mapToMessageList):
        lineIsGrey = True
        del mapToMessageList[:]
        for message in messageList:
            #print "Splitting:\"" + message + "\""
            lineIsGrey = not lineIsGrey
            while len(message) > 0:
                cursor = len(message)
                messagePart = message
                while cursor > 0 and dc.GetTextExtent(messagePart)[0] > maxLength:
                    #Move the cursor one word back
                    cursor -= 1
                    while cursor > 0 and message[cursor-1] != ' ':
                        cursor -= 1
                    if cursor > 0:
                        messagePart = message[:cursor]
                #If breaking in between the word failed,break in the middle of the word
                if cursor <= 0:
                    cursor = len(message)
                    while dc.GetTextExtent(messagePart)[0] > maxLength:
                        cursor -= 1
                        messagePart = message[:cursor]
                message = message[cursor:]
                mapToMessageList.append((messagePart,lineIsGrey))
                #print "\t" + messagePart
                
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
        self.windowWidth = 300
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
            
            #dc.DrawLabel(str(node.id),wx.Rect(x=x-25,y=y-20,width=45,height=20))
            dc.DrawCircle(x,y,3) 
            #Store the position for later use  
            self.nodePositions.append(Node(nodeId,x,y))
            
        #Third draw windows
        #process of drawing windows.
        
        for nodeId in self.connectedNodes:
            node = self.connectedNodes[nodeId]
            WindowWidth = self.windowWidth
            #1. Break text into lines based off of allowed length
            size = node.myWindow.mapMessagesToLines(dc,WindowWidth)
            totalHeight = ((size[0]+size[1])*size[2]) + size[2] + 4.0 + 4.0
            #totalHeight = 50
            #2. Draw a solid white background for the total actual lines
            x = node.myWindow.x*WindowWidth+node.x*width
            y = node.myWindow.y*totalHeight+node.y*height
            
            x = max(x,0)
            y = max(y,0)
            x = min(x,width-WindowWidth)
            y = min(y,height-totalHeight)
            
            #3. Draw a thick border including a thin title bar
            brush = wx.Brush('white')
            pen = wx.Pen('black',2)
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawRectangle(x,y,WindowWidth,totalHeight)
            dc.DrawLine(x,y+size[2]-1,x+WindowWidth-1,y+size[2]-1)
            dc.DrawLabel("Node " + str(node.id),wx.Rect(x+2,y,45,20))
            
            #4. Draw a think border between slot messages and regular messages 
            pen = wx.Pen('green',4)
            dc.SetPen(pen)
            dc.DrawLine(x+2,y+size[2]+size[0]*size[2]+2,x+WindowWidth-3,y+size[2]+size[0]*size[2]+2)
            #5. Color alternating message boxes in a grey color
            #6. Draw messages in black over the background
            brush = wx.Brush('grey')
            pen = wx.Pen('grey',1)
            dc.SetPen(pen)
            dc.SetBrush(brush)
            yAt = y+size[2]
            for mes in node.myWindow.fixedMessageLines:
                if mes[1]:
                    dc.DrawRectangle(x+1,yAt,WindowWidth-3,size[2])
                dc.DrawText(mes[0],x+1,yAt)
                yAt += size[2]
            yAt += 4.0
            for mes in node.myWindow.messageLines:
                if mes[1]: #Lines alternate grey and white
                    dc.DrawRectangle(x+1,yAt,WindowWidth-3,size[2])
                dc.DrawText(mes[0],x+1,yAt)
                yAt += size[2]

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawnodes(dc)