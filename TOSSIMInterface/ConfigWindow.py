'''
Created on Oct 12, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
import string
import re
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
        super(ConfigWindow,self).__init__(sim,"Config Window")
        #self.BackgroundColour()
        
        #Create menus
        self.presetMenu = wx.Menu()
        #Register menus
        self.RegisterMenu(self.presetMenu);
        #Append menus
        self.menuBar.Append(self.presetMenu,"Presets")
        
        self.RebuildMenus()
        
        #Build dialog
        baseVSize = wx.BoxSizer(wx.VERTICAL)
        
        nameHSize = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,wx.ID_ANY,"Python File: ")
        nameHSize.Add(label,0,wx.RIGHT, 8);
        self.pythonChildTextbox = wx.TextCtrl(self,wx.ID_ANY);
        self.Bind(wx.EVT_TEXT, self.__OnPythonChildChange, self.pythonChildTextbox)
        nameHSize.Add(self.pythonChildTextbox, 1)
        nameHSize.AddSpacer(10,-1)
        button = wx.Button(self,wx.ID_ANY,"Browse");
        self.Bind(wx.EVT_BUTTON, self.__OnPythonBrowse, button)
        nameHSize.Add(button,0,wx.RIGHT);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,-1);
        
        nameHSize = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,wx.ID_ANY,"Topo File: ")
        nameHSize.Add(label,0,wx.RIGHT, 8);
        self.topoFileTextbox = wx.TextCtrl(self,wx.ID_ANY);
        self.Bind(wx.EVT_TEXT, self.__OnTopoFileChange, self.topoFileTextbox)
        nameHSize.Add(self.topoFileTextbox, 1)
        nameHSize.AddSpacer(10,-1)
        button = wx.Button(self,wx.ID_ANY,"Browse");
        self.Bind(wx.EVT_BUTTON, self.__OnTopoBrowse, button)
        nameHSize.Add(button,0,wx.RIGHT);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,-1);
        
        nameHSize = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,wx.ID_ANY,"Noise File: ")
        nameHSize.Add(label,0,wx.RIGHT, 8);
        self.noiseFileTextbox = wx.TextCtrl(self,wx.ID_ANY);
        self.Bind(wx.EVT_TEXT, self.__OnNoiseFileChange, self.noiseFileTextbox)
        nameHSize.Add(self.noiseFileTextbox, 1)
        nameHSize.AddSpacer(10,-1)
        button = wx.Button(self,wx.ID_ANY,"Browse");
        self.Bind(wx.EVT_BUTTON, self.__OnNoiseBrowse, button)
        nameHSize.Add(button,0,wx.RIGHT);
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,-1);
        
        opcountHSize = wx.BoxSizer(wx.HORIZONTAL);
        label = wx.StaticText(self,wx.ID_ANY,"Opcount per second: ")
        opcountHSize.Add(label,0,wx.RIGHT, 8);
        self.opCountTextbox = wx.TextCtrl(self,wx.ID_ANY,validator=NumericObjectValidator());
        self.Bind(wx.EVT_TEXT, self.__OnOpCountChange, self.opCountTextbox)
        opcountHSize.Add(self.opCountTextbox, 1)
        
        baseVSize.AddSizer(opcountHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,-1);
        

        label = wx.StaticText(self,wx.ID_ANY,"List of All Valid Channels")
        baseVSize.Add(label, 0, wx.CENTER, 10)
        self.channelListBox = wx.ListBox(self,wx.ID_ANY)
        baseVSize.Add(self.channelListBox,2,wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM,10)
        
        nameHSize = wx.BoxSizer(wx.HORIZONTAL)
        self.autoLearnCheckbox = wx.CheckBox(self,wx.ID_ANY,"Autolearn New Channels")
        self.Bind(wx.EVT_CHECKBOX, self.__OnAutoChannelLearnChange, self.autoLearnCheckbox)
        nameHSize.Add(self.autoLearnCheckbox,0,wx.LEFT,10)
        button = wx.Button(self,wx.ID_ANY,"Add Channel");
        self.Bind(wx.EVT_BUTTON, self.__OnChannelAdd, button)
        nameHSize.Add(button,0,wx.CENTER,10)
        button = wx.Button(self,wx.ID_ANY,"Delete Channel");
        self.Bind(wx.EVT_BUTTON, self.__OnChannelRemove, button)
        nameHSize.Add(button,0,wx.RIGHT,10)
        
        baseVSize.AddSizer(nameHSize, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        baseVSize.AddSpacer(10,-1);
        
        self.UpdateDisplay()
        
        self.SetSizer(baseVSize)
        self.Show();
        
    def UpdateDisplay(self):
        self.pythonChildTextbox.Value = self.sim.selectedOptions.childPythonName
        self.noiseFileTextbox.Value = self.sim.selectedOptions.noiseFileName
        self.topoFileTextbox.Value = self.sim.selectedOptions.topoFileName
        self.opCountTextbox.Value = str(self.sim.selectedOptions.opsPerSecond)
        self.autoLearnCheckbox.Value = self.sim.selectedOptions.autolearnChannels
        self.channelListBox.Set(self.sim.selectedOptions.channelList)
        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this OutputWindow. Used for new lists of nodes, or channels
        '''
        print "REBUILDING"
        menuBar = super(ConfigWindow,self).RebuildMenus();
        
        self.presetDict = dict();
        
        #presetMenu
        for preset in self.sim.savedPresets.configPresets:
            item = self.AddMenuItem(self.presetMenu, preset.name, self.__OnPreset)
            self.presetDict[item.GetId()] = preset
        self.presetMenu.AppendSeparator();
        self.AddMenuItem(self.presetMenu, "Remove Existing Preset", self.__OnPresetRemove)
        self.AddMenuItem(self.presetMenu, "Add Current as New Preset", self.__OnPresetAdd)
        
        return menuBar;
    
        # def AddMessage(self, message):
    
        
    def WindowType(self):
        return 2
    #browse buttons
    def __OnPythonBrowse(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            wildcard="Python files (*.py)|*.py|All files (*.*)|*.*",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.pythonChildTextbox.Value = dlg.GetPath()
            self.sim.selectedOptions.childPythonName = self.pythonChildTextbox.Value
            #self.Sim.SavePresets()
        dlg.Destroy()
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
    def __OnNoiseBrowse(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.noiseFileTextbox.Value = dlg.GetPath()
            self.sim.selectedOptions.noiseFileName = self.noiseFileTextbox.Value
            #self.Sim.SavePresets()
        dlg.Destroy()
    #for the dialog
    def __OnPythonChildChange(self, event):
        self.sim.selectedOptions.childPythonName = self.pythonChildTextbox.Value
        #self.Sim.SavePresets()
        
    def __OnTopoFileChange(self, event):
        self.sim.selectedOptions.topoFileName = self.topoFileTextbox.Value
        self.TopoUpdate()
        
    def __OnNoiseFileChange(self, event):
        self.sim.selectedOptions.noiseFileName = self.noiseFileTextbox.Value
        #self.Sim.SavePresets()
        
    def __OnOpCountChange(self, event):
        self.sim.selectedOptions.opsPerSecond = int(self.opCountTextbox.Value)
        #self.Sim.SavePresets()
        
    def __OnAutoChannelLearnChange(self, event):
        self.sim.selectedOptions.autolearnChannels = self.autoLearnCheckbox.Value
        #self.Sim.SavePresets()
       
    def __OnChannelAdd(self, event):
        dialog = wx.TextEntryDialog(None,"Enter the channel name:", "Channel Name","");
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            if name in self.sim.selectedOptions.channelList:
                self.displayError("Channel names must be unique.");
                dialog.Destroy();
                return;
            if re.match('^[\w]+$', name) is None:
                self.displayError("Channel names must be purely alphanumeric.");
                dialog.Destroy();
                return;
            self.sim.selectedOptions.channelList.append(name)
        dialog.Destroy()
        self.channelListBox.Set(self.sim.selectedOptions.channelList)
        #self.Sim.SavePresets();
        
    def __OnChannelRemove(self, event):
        dlg = wx.SingleChoiceDialog(self, "Choose a preset to remove.", "Preset List",self.sim.selectedOptions.channelList, wx.CHOICEDLG_STYLE)
 
        if dlg.ShowModal() == wx.ID_OK:
            self.sim.selectedOptions.channelList.remove(dlg.GetStringSelection());
        dlg.Destroy()
        self.channelListBox.Set(self.sim.selectedOptions.channelList)
        #self.Sim.SavePresets();
    
    
    #For the presets Menu
    def __OnPreset(self, event):
        selPreset = self.presetDict[event.GetId()]
        self.sim.selectedOptions.childPythonName = selPreset.childPythonName
        self.sim.selectedOptions.opsPerSecond = selPreset.opsPerSecond
        self.sim.selectedOptions.autolearnChannels = selPreset.autolearnChannels
        self.sim.selectedOptions.channelList = list(selPreset.channelList)
        self.UpdateDisplay();
    def __OnPresetRemove(self, event):  
        presetsList = list();
        presetsDict = dict();
        for preset in self.sim.savedPresets.configPresets:
            presetsList.append(preset.name);
            presetsDict[preset.name] = preset;
        dlg = wx.SingleChoiceDialog(self, "Choose a preset to remove.", "Preset List",presetsList, wx.CHOICEDLG_STYLE)
 
        if dlg.ShowModal() == wx.ID_OK:
            self.sim.savedPresets.configPresets.remove(presetsDict[dlg.GetStringSelection()]);
        dlg.Destroy()
        self.RebuildMenus();
        #self.Sim.SavePresets();
        
    def __OnPresetAdd(self, event):
        dialog = wx.TextEntryDialog(None,"Choose a name for the preset:", "Preset Name","");
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            for preset in self.sim.savedPresets.configPresets:
                if name == preset.name:
                    self.displayError("Preset names must be unique.");
                    dialog.Destroy();
                    return;
            newPreset = Simulation.SimOptions()
            newPreset.childPythonName = self.sim.selectedOptions.childPythonName
            newPreset.opsPerSecond = self.sim.selectedOptions.opsPerSecond
            newPreset.autolearnChannels = self.sim.selectedOptions.autolearnChannels
            newPreset.channelList = list(self.sim.selectedOptions.channelList)
            newPreset.name = name;
            self.sim.savedPresets.configPresets.append(newPreset);
            self.RebuildMenus();
        dialog.Destroy()
        #self.Sim.SavePresets();
        
class NumericObjectValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)
    
    def Clone(self):
        return NumericObjectValidator()
    
    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
    
        for x in val:
            if x not in string.digits:
                return False
    
        return True
    
    
    def OnChar(self, event):
        key = event.GetKeyCode()
    
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
    
        if chr(key) in string.digits:
            event.Skip()
    
        return       