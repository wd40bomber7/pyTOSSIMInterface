'''
Created on Oct 12, 2012

@author: wd40bomber7
'''


import wx.richtext;
import PrimaryFrame;
import Simulation
from Messages import MessageType


class OutputWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #Variables
        self.selectedChannels = list();
        self.selectedTypes = list();
        self.selectedNodes = list();
        
        self.displayNodeId = True;
        self.displayChannel = False;
        self.displayType = True;
        
        self.selectedPreset = None;
        

        #setup
        super(OutputWindow,self).__init__(sim,"Output Window")
        
        r = wx.richtext.RichTextCtrl(self,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_SCROLL)
        #r = wx.TextCtrl(self,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_SCROLL)
        self.control = r;
        #r.GetCaret().Hide();
        r.BeginFontSize(12);
        r.BeginTextColour(wx.Color(255,0,0))
        self.Show(True);
        self.tester = 0
        self.r = r
        #for i in range(1,75):
            #r.WriteText("test " + str(i));
            #time.sleep(.25);
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.timer.Start(250);
        
        #Create menus
        self.typeMenu = wx.Menu()
        self.channelsMenu = wx.Menu()
        self.nodesMenu = wx.Menu()
        self.displayMenu = wx.Menu()
        self.presetMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.typeMenu);
        self.RegisterMenu(self.channelsMenu);
        self.RegisterMenu(self.nodesMenu);
        self.RegisterMenu(self.displayMenu);
        self.RegisterMenu(self.presetMenu);
        #Append menus
        self.menuBar.Append(self.typeMenu,"Message Types");
        self.menuBar.Append(self.channelsMenu,"Channels");
        self.menuBar.Append(self.nodesMenu,"Nodes");
        self.menuBar.Append(self.displayMenu,"Display");
        self.menuBar.Append(self.presetMenu,"Presets");
        
        self.RebuildMenus()
        
        self.Show();
        #now for a little color test
    def Update(self, event):
        if self.tester > 50:
            self.timer.Stop();
        self.tester+=1;
        #self.r.Freeze();
        #self.r.Newline();
        #self.r.MoveToParagraphEnd();
        self.r.BeginFontSize(12);
        self.r.BeginTextColour(wx.Color(255,0,0))
        self.r.InsertionPoint = 100000 #hopefully big enough
        self.r.WriteText("test " + str(self.tester) + "\n");
        self.r.ShowPosition(self.r.GetLastPosition());
        #self.r.Scroll(1000,1000)
        #self.r.
        #self.r.Thaw();
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this OutputWindow. Used for new lists of nodes, or channels
        '''
        print "REBUILDING"
        menuBar = super(OutputWindow,self).RebuildMenus();
        
        
        self.channelDict = dict();
        self.nodeDict = dict();
        self.presetDict = dict();
        
        #type menu
        self.testerValue = self.AddMenuItem(self.typeMenu, "Debug", self.__OnTypeDebug, MessageType.Debug in self.selectedTypes)
        self.AddMenuItem(self.typeMenu, "Error", self.__OnTypeError, MessageType.Error in self.selectedTypes)
        
        #channelsMenu
        for channel in self.sim.selectedOptions.channelList:
            item = self.AddMenuItem(self.channelsMenu, channel, self.__OnChannel, channel in self.selectedChannels)
            self.channelDict[item.GetId()] = channel
        
        #nodesMenu
        for node in self.sim.simulationState.currentTopo.nodeDict:
            item = self.AddMenuItem(self.nodesMenu, "Node " + str(node), self.__OnNode, node in self.selectedChannels)
            self.nodeDict[item.GetId()] = node

        #self.nodesMenu.AppendSeparator();
        #item = self.AddMenuItem(self.nodesMenu, "All Nodes", self.__OnNode, node in self.selectedChannels)
        #self.nodeDict[item.GetId()] = node
        
        #displayMenu
        self.AddMenuItem(self.displayMenu, "Node Ids", self.__OnDisplayNodeIDs, self.displayNodeId)
        self.AddMenuItem(self.displayMenu, "Channels", self.__OnDisplayChannels, self.displayChannel)
        self.AddMenuItem(self.displayMenu, "Message Types", self.__OnDisplayTypes, self.displayType)
        
        #presetMenu
        for preset in self.sim.savedPresets.outputPresets:
            item = self.AddMenuItem(self.presetMenu, preset.name, self.__OnPreset, preset == self.selectedPreset)
            self.presetDict[item.GetId()] = preset
        self.presetMenu.AppendSeparator();
        self.AddMenuItem(self.presetMenu, "Remove Existing Preset", self.__OnPresetRemove)
        self.AddMenuItem(self.presetMenu, "Add Current as New Preset", self.__OnPresetAdd)
        
        return menuBar;
    
        # def AddMessage(self, message):
    
        
    def WindowType(self):
        return 1
    
    #For the type Menu
    def __OnTypeDebug(self, event):
        if MessageType.Debug in self.selectedTypes:
            self.selectedTypes.remove(MessageType.Debug)
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.selectedTypes.append(MessageType.Debug)
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
            
    def __OnTypeError(self, event):
        if MessageType.Error in self.selectedTypes:
            self.selectedTypes.remove(MessageType.Error)
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.selectedTypes.append(MessageType.Error)
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
            
    #For the channel Menu
    def __OnChannel(self, event):
        channel = self.channelDict[event.GetId()]
        if channel in self.selectedChannels:
            self.selectedChannels.remove(channel)
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.selectedChannels.append(channel)
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
    #For the nodes Menu
    def __OnNode(self, event):
        node = self.nodeDict[event.GetId()]
        if node in self.selectedChannels:
            self.selectedChannels.remove(node)
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.selectedChannels.append(node)
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
    #For the display Menu
    def __OnDisplayNodeIDs(self, event):
        if self.displayNodeId:
            self.displayNodeId = False
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.displayNodeId = True
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
    def __OnDisplayChannels(self, event):
        if self.displayChannel:
            self.displayChannel = False
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.displayChannel = True
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
    def __OnDisplayTypes(self, event):
        if self.displayNodeId:
            self.displayNodeId = False
            self.typeMenu.FindItemById(event.GetId()).Check(False)
        else:
            self.displayNodeId = True
            self.typeMenu.FindItemById(event.GetId()).Check(True)
        self.selectedPreset = None;
    #For the presets Menu
    def __OnPreset(self, event):
        if self.selectedPreset != self.presetDict[event.GetId()]:
            self.selectedPreset = self.presetDict[event.GetId()]
            self.selectedChannels = self.selectedPreset.selectedChannels[:]
            self.selectedTypes = self.selectedPreset.selectedTypes[:]
            self.selectedNodes = self.selectedPreset.selectedNodes[:]
            self.displayChannel = self.selectedPreset.displayChannel
            self.displayNodeId = self.selectedPreset.displayNodeId;
            self.displayType = self.selectedPreset.displayType;
            self.RebuildMenus();
    def __OnPresetRemove(self, event):  
        presetsList = list();
        presetsDict = dict();
        for preset in self.sim.savedPresets.outputPresets:
            presetsList.append(preset.name);
            presetsDict[preset.name] = preset;
        dlg = wx.SingleChoiceDialog(self, "Choose a preset to remove.", "Preset List",presetsList, wx.CHOICEDLG_STYLE)
 
        if dlg.ShowModal() == wx.ID_OK:
            self.sim.savedPresets.outputPresets.remove(presetsDict[dlg.GetStringSelection()]);
        dlg.Destroy()
        self.RebuildMenus();
        self.sim.SavePresets();
        
    def __OnPresetAdd(self, event):
        dialog = wx.TextEntryDialog(None,"Choose a name for the preset:", "Preset Name","");
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            for preset in self.sim.savedPresets.outputPresets:
                if name == preset.name:
                    self.displayError("Preset names must be unique.");
                    dialog.Destroy();
                    return;
            newPreset = Simulation.SimOutput()
            newPreset.selectedChannels = self.selectedChannels[:]
            newPreset.selectedNodes = self.selectedNodes[:]
            newPreset.selectedTypes = self.selectedTypes[:]
            newPreset.displayChannel = self.displayChannel;
            newPreset.displayNodeId = self.displayNodeId;
            newPreset.displayType = self.displayType;
            newPreset.name = name;
            self.sim.savedPresets.outputPresets.append(newPreset);
            self.RebuildMenus();
        dialog.Destroy()
        self.sim.SavePresets();
        