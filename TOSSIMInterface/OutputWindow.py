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
        self.readPosition = 0; #the line in the list of all received lines this node is reading at
        self.selectedChannels = list();
        self.selectedTypes = list();
        self.selectedNodes = list();
        
        self.displayNodeId = True;
        self.displayChannel = False;
        self.displayType = True;
        
        self.selectedPreset = None;
        self.displayedText = ""
        

        #setup
        super(OutputWindow,self).__init__(sim,"Output Window")
        
        self.control = wx.richtext.RichTextCtrl(self,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_SCROLL)
        #r = wx.TextCtrl(self,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_SCROLL)
        self.control.BeginFontSize(12);
        self.Show(True);
        self.tester = 0
        
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
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateDisplay, self.timer)
        self.timer.Start(250);
        self.UpdateDisplay(None) #force initial update
        
        self.Show();
        #now for a little color test
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
        self.channelCount = len(self.sim.selectedOptions.channelList)
        for channel in self.sim.selectedOptions.channelList:
            item = self.AddMenuItem(self.channelsMenu, channel, self.__OnChannel, channel in self.selectedChannels)
            self.channelDict[item.GetId()] = channel
        
        #nodesMenu
        for node in self.sim.simulationState.currentTopo.nodeDict:
            item = self.AddMenuItem(self.nodesMenu, "Node " + str(node), self.__OnNode, node in self.selectedNodes)
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
    
    def __RenderMessage(self, message):
        rendered = ""
        if self.displayType:
            rendered += "DEBUG " if (message.messageType == MessageType.Debug) else "ERROR "
        if self.displayChannel:
            rendered += "[" + message.channelList[0] + "] "
        if self.displayNodeId:
            rendered += " (" + str(message.nodeId) + ") "
        rendered = rendered[:-1] + ": " + message.messageText.rstrip(); #render color one day?
        #if len(self.displayedText) > 0:
            #rendered = "\n" + rendered
        
        self.displayedText += rendered
        if (message.messageType != MessageType.Debug):
            self.control.BeginTextColour(wx.Color(255,0,0))
        self.control.InsertionPoint = 100000
        self.control.WriteText(rendered);
        self.control.ShowPosition(self.control.GetLastPosition());
        if (message.messageType != MessageType.Debug):
            self.control.EndTextColour()
        
        
    def UpdateDisplay(self, event):
        newData = self.sim.simulationState.messages.RetrieveFilteredList(self.selectedTypes,self.selectedChannels,self.selectedNodes,self.readPosition)
        #print "Updated display. [" + str(self.readPosition) + " -> " + str(newData[0]) + "]"
        self.readPosition = newData[0]
        for message in newData[1]:
            self.__RenderMessage(message);
        if self.channelCount != len(self.sim.selectedOptions.channelList):
            self.RebuildMenus()
    def RebuildDisplay(self):
	self.displayedText = ""
	self.control.Value = ""
        self.readPosition = 0
        self.UpdateDisplay(None)
        
    def WindowType(self):
        return 1
    
    #For the type Menu
    def __OnTypeDebug(self, event):
        if MessageType.Debug in self.selectedTypes:
            self.selectedTypes.remove(MessageType.Debug)
        else:
            self.selectedTypes.append(MessageType.Debug)
        self.selectedPreset = None;
	self.RebuildDisplay()
            
    def __OnTypeError(self, event):
        if MessageType.Error in self.selectedTypes:
            self.selectedTypes.remove(MessageType.Error)
        else:
            self.selectedTypes.append(MessageType.Error)
        self.selectedPreset = None;
        self.RebuildDisplay()
            
    #For the channel Menu
    def __OnChannel(self, event):
        channel = self.channelDict[event.GetId()]
        if channel in self.selectedChannels:
            self.selectedChannels.remove(channel)
        else:
            self.selectedChannels.append(channel)
        self.selectedPreset = None;
        self.RebuildDisplay()
        
    #For the nodes Menu
    def __OnNode(self, event):
        node = self.nodeDict[event.GetId()]
        if node in self.selectedNodes:
            self.selectedNodes.remove(node)
        else:
            self.selectedNodes.append(node)
        self.selectedPreset = None;
        self.RebuildDisplay()
    #For the display Menu
    def __OnDisplayNodeIDs(self, event):
        if self.displayNodeId:
            self.displayNodeId = False
        else:
            self.displayNodeId = True
        self.selectedPreset = None;
        self.RebuildDisplay()
    def __OnDisplayChannels(self, event):
        if self.displayChannel:
            self.displayChannel = False
        else:
            self.displayChannel = True
        self.selectedPreset = None;
        self.RebuildDisplay()
    def __OnDisplayTypes(self, event):
        if self.displayType:
            self.displayType = False
        else:
            self.displayType = True
        self.selectedPreset = None;
        self.RebuildDisplay()
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
	    self.RebuildDisplay()
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
        #self.Sim.SavePresets();
        
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
        #self.Sim.SavePresets();
        