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
        layoutData = drawnGraph.sp