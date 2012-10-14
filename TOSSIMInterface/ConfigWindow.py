'''
Created on Oct 12, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
from Messages import MessageType


class ConfigWindow(PrimaryFrame.MainWindow):
    '''
    A MDI child class made for displaying output
    '''

    def __init__(self,sim):
        '''
        Constructor
        '''
        #Variables


        #setup
        super(ConfigWindow,self).__init__(sim,"Output Window")
        
        
        #Create menus
        self.presetMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.presetMenu);
        #Append menus
        self.menuBar.Append(self.presetMenu,"Presets");
        
        self.RebuildMenus()
        
        self.Show();
        #now for a little color test
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this OutputWindow. Used for new lists of nodes, or channels
        '''
        print "REBUILDING"
        menuBar = super(ConfigWindow,self).RebuildMenus();
        
        self.presetDict = dict();
        
        #presetMenu
        for preset in self.sim.savedPresets.outputPresets:
            item = self.AddMenuItem(self.presetMenu, preset.name, self.__OnPreset)
            self.presetDict[item.GetId()] = preset
        self.presetMenu.AppendSeparator();
        self.AddMenuItem(self.presetMenu, "Remove Existing Preset", self.__OnPresetRemove)
        self.AddMenuItem(self.presetMenu, "Add Current as New Preset", self.__OnPresetAdd)
        
        return menuBar;
    
        # def AddMessage(self, message):
    
        
    def WindowType(self):
        return 1
    
    #For the presets Menu
    def __OnPreset(self, event):
        '''
        stub
        '''
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
        