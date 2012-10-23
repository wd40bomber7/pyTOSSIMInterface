'''
Created on Oct 17, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
import string
import re
from Messages import MessageType


class InjectionWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #Variables


        #setup
        super(InjectionWindow,self).__init__(sim,"Injection Window")
        #self.BackgroundColour()
        self.LoadInjects()
        #Create menus
        self.injectMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.injectMenu);
        #Append menus
        self.menuBar.Append(self.injectMenu,"Inject")
        
        
        #Build dialog
        baseVSize = wx.BoxSizer(wx.HORIZONTAL)
        
        nameHSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"Source node")
        nameHSize.Add(label,0,wx.CENTER, 8);
        self.sourceBox = wx.ListBox(self,wx.ID_ANY,style=wx.LB_MULTIPLE)
        nameHSize.Add(self.sourceBox,1,wx.CENTER, 8);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,10);

        nameHSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"Destination node")
        nameHSize.Add(label,0,wx.CENTER, 8);
        self.destinationBox = wx.ListBox(self,wx.ID_ANY,style=wx.LB_MULTIPLE)
        nameHSize.Add(self.destinationBox,1,wx.CENTER, 8);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,10);
        
        nameHSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"%other% node")
        nameHSize.Add(label,0,wx.CENTER, 8);
        self.nodeBox = wx.ListBox(self,wx.ID_ANY)
        nameHSize.Add(self.nodeBox,1,wx.CENTER, 8);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,10);

        nameHSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"%message%")
        nameHSize.Add(label,0,wx.CENTER, 8);
        self.messageText = wx.TextCtrl(self,wx.ID_ANY);
        nameHSize.Add(self.messageText,1,wx.CENTER, 8);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        baseVSize.AddSpacer(10,10);        
        #self.UpdateDisplay()
        
        self.RebuildMenus()
        self.SetSizer(baseVSize)
        self.Show();
        
    def LoadInjects(self):
        self.injects = list()
        injectFile = open("injects.txt","rb")
        for line in injectFile:
            if (len(line.strip()) <= 0):
                continue
            cmd = line.split(':')
            self.injects.append(Inject(cmd[0],int(cmd[1]),cmd[2]))
        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this OutputWindow. Used for new lists of nodes, or channels
        '''
        menuBar = super(InjectionWindow,self).RebuildMenus();
        
        self.injectDict = dict();
        
        #InjectMenu
        for i in self.injects:
            item = self.AddMenuItem(self.injectMenu, "Inject " + i.text, self.__OnInject)
            self.injectDict[item.GetId()] = i
        
        #rebuild node list
        for node in self.sim.simulationState.currentTopo.nodeDict:
            self.sourceBox.Append(str(node.myId))
            self.destinationBox.Append(str(node.myId))
            self.nodeBox.Append(str(node.myId))
        
        return menuBar;
    
        # def AddMessage(self, message):
    
        
    def WindowType(self):
        return 4
    #browse buttons
    
    
    
    #For the inject menu
    def __OnInject(self, event):
        selInject = self.injectDict[event.GetId()]
        self.sourceBox.se
        

class Inject(object):
    def __init__(self,text,protocol,injectText):
        self.text = text
        self.protocol = protocol
        self.injectText = injectText