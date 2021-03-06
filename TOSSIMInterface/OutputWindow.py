'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

import wx.richtext;
import PrimaryFrame;
import Simulation
import time
import cProfile

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
        self.excludedChannels = list();
        self.excludedTypes = list();
        self.excludedNodes = list();
        
        self.displayNodeId = True;
        self.displayChannel = False;
        self.displayType = True;
        
        self.defaultPreset = None;
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
        if self.defaultPreset is None:
            self.__buildPreset("default")
            print "Built preset"
        else:
            self.__loadPreset(self.defaultPreset)
            self.RebuildMenus()
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateDisplay, self.timer)
        self.timer.Start(100);
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
        self.testerValue = self.AddMenuItem(self.typeMenu, "Debug", self.__OnTypeDebug,not MessageType.Debug in self.excludedTypes)
        self.AddMenuItem(self.typeMenu, "Error", self.__OnTypeError,not MessageType.Error in self.excludedTypes)
        
        #channelsMenu
        self.channelCount = len(self.sim.selectedOptions.channelList)
        for channel in self.sim.selectedOptions.channelList:
            item = self.AddMenuItem(self.channelsMenu, channel, self.__OnChannel, not channel in self.excludedChannels)
            self.channelDict[item.GetId()] = channel
        
        #nodesMenu
        if not self.sim.simulationState.currentTopo is None:
            for node in self.sim.simulationState.currentTopo.nodeDict:
                item = self.AddMenuItem(self.nodesMenu, "Node " + str(node), self.__OnNode, not node in self.excludedNodes)
                self.nodeDict[item.GetId()] = node

        #self.nodesMenu.AppendSeparator();
        #item = self.AddMenuItem(self.nodesMenu, "All Nodes", self.__OnNode, node in self.excludedChannels)
        #self.nodeDict[item.GetId()] = node
        
        #displayMenu
        self.AddMenuItem(self.displayMenu, "Node Ids", self.__OnDisplayNodeIDs, self.displayNodeId)
        self.AddMenuItem(self.displayMenu, "Channels", self.__OnDisplayChannels, self.displayChannel)
        self.AddMenuItem(self.displayMenu, "Message Types", self.__OnDisplayTypes, self.displayType)
        
        #presetMenu
        for preset in self.sim.savedPresets.outputPresets:
            if preset.name != "default":
                item = self.AddMenuItem(self.presetMenu, preset.name, self.__OnPreset, preset == self.selectedPreset)
                self.presetDict[item.GetId()] = preset
            else:
                self.defaultPreset = preset;
                self.presetMenu.AppendSeparator();
                self.AddMenuItem(self.presetMenu, "Remove Existing Preset", self.__OnPresetRemove)
                self.AddMenuItem(self.presetMenu, "Add Current as New Preset", self.__OnPresetAdd)
        
        return menuBar;
    
    def __RenderMessage(self, message):
        start = time.clock()
        renderList = list()
        if self.displayType:
            renderList.append("DEBUG" if (message.messageType == MessageType.Debug) else "ERROR")
        if self.displayChannel:
            renderList.append(" [")
            renderList.append(message.channelList[0])
            renderList.append("]")
        if self.displayNodeId:
            renderList.append(" (")
            renderList.append(str(message.nodeId))
            renderList.append(")")
        renderList.append(": ")
        renderList.append(message.messageText.rstrip()); #render color one day?
        rendered = ''.join(renderList);
        
        if (message.messageType != MessageType.Debug):
            self.control.BeginTextColour(wx.Color(255,0,0))
        self.control.InsertionPoint = 100000
        second = time.clock()
        self.control.WriteText(rendered);
        third  = time.clock()
        self.control.ShowPosition(self.control.GetLastPosition());
        if (message.messageType != MessageType.Debug):
            self.control.EndTextColour()
        last = time.clock()
        return [second-start,third-second,last-third]
        
    
    def UpdateDisplay(self, event):
        simple = [0,0,0]
        newData = self.sim.simulationState.messages.RetrieveFilteredList(self.excludedTypes,self.excludedChannels,self.excludedNodes,self.readPosition)
        #print "Updated display. [" + str(self.readPosition) + " -> " + str(newData[0]) + "]"
        self.readPosition = newData[0]
        for message in newData[1]:
            o = self.__RenderMessage(message)
            simple[0] += o[0]
            simple[1] += o[1]
            simple[2] += o[2]
            
        if self.channelCount != len(self.sim.selectedOptions.channelList):
            print "[0] Rebuilt menus"
            self.RebuildMenus()
        if (len(newData[1]) > 0):
            print "[1]: Added " + str(len(newData[1])) + " new messages in " + str(simple[0]) + ":" + str(simple[1]) + ":" + str(simple[2])
    
    
    def RebuildDisplay(self):
        self.displayedText = ""
        self.control.Value = ""
        self.readPosition = 0
        self.UpdateDisplay(None)
        
    def WindowType(self):
        return 1
    
    #Save default preset
    def OnClose(self, event):
        self.__overWritePreset(self.defaultPreset)
        #finish clean up
        super(OutputWindow,self).OnClose(event)
        #For the type Menu
    def __OnTypeDebug(self, event):
        if MessageType.Debug in self.excludedTypes:
            self.excludedTypes.remove(MessageType.Debug)
        else:
            self.excludedTypes.append(MessageType.Debug)
        self.selectedPreset = None;
        self.RebuildDisplay()
            
    def __OnTypeError(self, event):
        if MessageType.Error in self.excludedTypes:
            self.excludedTypes.remove(MessageType.Error)
        else:
            self.excludedTypes.append(MessageType.Error)
        self.selectedPreset = None;
        self.RebuildDisplay()
        
    #For the channel Menu
    def __OnChannel(self, event):
        channel = self.channelDict[event.GetId()]
        if channel in self.excludedChannels:
            self.excludedChannels.remove(channel)
        else:
            self.excludedChannels.append(channel)
        self.selectedPreset = None;
        self.RebuildDisplay()
        
    #For the nodes Menu
    def __OnNode(self, event):
        node = self.nodeDict[event.GetId()]
        if node in self.excludedNodes:
            self.excludedNodes.remove(node)
        else:
            self.excludedNodes.append(node)
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
            self.__loadPreset(self.selectedPreset)
            self.RebuildMenus();
            self.RebuildDisplay()
    def __OnPresetRemove(self, event):  
        presetsList = list();
        presetsDict = dict();
        for preset in self.sim.savedPresets.outputPresets:
            if preset.name != "default":
                presetsList.append(preset.name);
                presetsDict[preset.name] = preset;
                dlg = wx.SingleChoiceDialog(self, "Choose a preset to remove.", "Preset List",presetsList, wx.CHOICEDLG_STYLE)
 
        if dlg.ShowModal() == wx.ID_OK:
            self.sim.savedPresets.outputPresets.remove(presetsDict[dlg.GetStringSelection()]);
        dlg.Destroy()
        self.RebuildMenus();
        
    def __OnPresetAdd(self, event):
        dialog = wx.TextEntryDialog(None,"Choose a name for the preset:", "Preset Name","");
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            for preset in self.sim.savedPresets.outputPresets:
                if name == preset.name:
                    self.displayError("Preset names must be unique.");
                    dialog.Destroy()
                    return;
            self.__buildPreset(name)
            #TODO: Rebuild menus of all output windows here and elsewhere
            self.RebuildMenus()
        dialog.Destroy()
        
    def __buildPreset(self, name):
        newPreset = Simulation.SimOutput()
        newPreset.excludedChannels = self.excludedChannels[:]
        newPreset.excludedNodes = self.excludedNodes[:]
        newPreset.excludedTypes = self.excludedTypes[:]
        newPreset.displayChannel = self.displayChannel;
        newPreset.displayNodeId = self.displayNodeId;
        newPreset.displayType = self.displayType;
        newPreset.name = name;
        self.sim.savedPresets.outputPresets.append(newPreset);
    def __loadPreset(self, preset):
        self.excludedChannels = preset.excludedChannels[:]
        self.excludedTypes = preset.excludedTypes[:]
        self.excludedNodes = preset.excludedNodes[:]
        self.displayChannel = preset.displayChannel
        self.displayNodeId = preset.displayNodeId;
        self.displayType = preset.displayType;
    def __overWritePreset(self, toReplace):
        toReplace.excludedChannels = self.excludedChannels[:]
        toReplace.excludedNodes = self.excludedNodes[:]
        toReplace.excludedTypes = self.excludedTypes[:]
        toReplace.displayChannel = self.displayChannel;
        toReplace.displayNodeId = self.displayNodeId;
        toReplace.displayType = self.displayType;
        