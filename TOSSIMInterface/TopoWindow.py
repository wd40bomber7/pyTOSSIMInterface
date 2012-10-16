'''
Created on Oct 15, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
import string
import re
from Messages import MessageType


class TopoWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #Variables


        #setup
        super(TopoWindow,self).__init__(sim,"Config Window")
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
        

        self.Show();
        

        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this TopoWindow. 
        '''
        menuBar = super(TopoWindow,self).RebuildMenus();
        
        self.topoDict = dict();
        
        #presetMenu
        for topoFile in self.sim.savedPresets.topoHistory:
            item = self.AddMenuItem(self.topoFileMenu, topoFile, self.__OnTopoSelect)
            self.presetDict[item.GetId()] = topoFile
        self.topoFileMenu.AppendSeparator();
        self.AddMenuItem(self.topoFileMenu, "Browse", self.__OnTopoBrowse)
        
        self.AddMenuItem(self.nodeMenu, "Delete Node", self.__OnNodeRemove)
        self.AddMenuItem(self.nodeMenu, "Add Node", self.__OnNodeAdd)
        
        return menuBar;
        
    def WindowType(self):
        return 3
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
        '''
        stub
        '''
    def __OnTopoBrowse(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.topoFileTextbox.Value = dlg.GetPath()
            self.sim.selectedOptions.topoFileName = self.topoFileTextbox.Value
            #self.Sim.SavePresets()
        dlg.Destroy()

