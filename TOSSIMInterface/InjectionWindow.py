'''
Created on Oct 17, 2012

@author: wd40bomber7
'''


import wx;
import PrimaryFrame;
import Simulation
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
        self.sim = sim
        
        #setup
        super(InjectionWindow,self).__init__(sim,"Injection Window")
        #self.BackgroundColour()
        #Create menus
        self.injectMenu = wx.Menu()
        #Register menus
        #self.RegisterMenu(self.injectMenu);
        #Append menus
        #self.menuBar.Append(self.injectMenu,"Inject")
        
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        
        self.page1 = ScriptPanel(nb,sim)
        self.page2 = CommandPanel(nb,sim)
        
        nb.AddPage(self.page1, "Start Scripts")
        nb.AddPage(self.page2, "Issuable Commands")
        
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        
        #Build dialog
        self.RebuildMenus()
        self.Show();
        
    def RebuildMenus(self):
        '''
        Rebuilds the menus of this OutputWindow. Used for new lists of nodes, or channels
        '''
        super(InjectionWindow,self).RebuildMenus();
        
        self.page1.RefreshBox()
        
    def WindowType(self):
        return 4
    #browse buttons

#0005:15:4 5-7 Hello world!
#0020:99:1-4 11 cmd ping %src%
#0030:99:1 1-4 cmd kill    

class ScriptPanel(wx.Panel):
    
    def __init__(self, parent, sim):
        wx.Panel.__init__(self, parent)
        
        self.sim = sim
        self.selectedScript = None
        
        bottomSizer = wx.BoxSizer(wx.VERTICAL)
        self.startupLabel = wx.StaticText(self,wx.ID_ANY,"Startup Script: ")
        bottomSizer.Add(self.startupLabel,0,wx.TOP,0)
        
        baseHSize = wx.BoxSizer(wx.HORIZONTAL)
        nameVSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"Saved Startup Scripts")
        nameVSize.Add(label,0,wx.CENTER, 8);
        self.scriptBox = wx.ListBox(self,wx.ID_ANY)
        self.Bind(wx.EVT_LISTBOX, self.__OnScriptSelect, self.scriptBox)
        nameVSize.Add(self.scriptBox,1,wx.EXPAND | wx.CENTER, 8);
        
        
        buttonHSize = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(self,wx.ID_ANY,"Delete");
        self.Bind(wx.EVT_BUTTON, self.__OnScriptDel, button)
        buttonHSize.Add(button,0,wx.RIGHT);
        button = wx.Button(self,wx.ID_ANY,"New");
        self.Bind(wx.EVT_BUTTON, self.__OnScriptNew, button)
        buttonHSize.Add(button,0,wx.RIGHT);
        nameVSize.AddSizer(buttonHSize,0,wx.EXPAND,10)
        
        button = wx.Button(self,wx.ID_ANY,"Set As Startup");
        self.Bind(wx.EVT_BUTTON, self.__OnScriptSet, button)
        #buttonHSize.Add(button,0,wx.RIGHT);
        nameVSize.Add(button,0,wx.RIGHT)
        
        baseHSize.AddSizer(nameVSize, 0, wx.EXPAND, 10)
        baseHSize.AddSpacer(10,10);   


        scriptVSize = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,wx.ID_ANY,"Script Code:")
        scriptVSize.Add(label,0,wx.CENTER, 8);
        self.messageText = wx.TextCtrl(self,wx.ID_ANY,style=wx.TE_MULTILINE);
        self.messageText.SetEditable(False)
        self.Bind(wx.EVT_TEXT, self.__OnScriptChange, self.messageText)
        scriptVSize.Add(self.messageText,1,wx.EXPAND , 8);
        
        baseHSize.AddSizer(scriptVSize, 1, wx.EXPAND, 10)
        baseHSize.AddSpacer(10,10);        
        #self.UpdateDisplay()
        
        bottomSizer.AddSizer(baseHSize,1,wx.EXPAND,1);
        
        self.SetSizer(bottomSizer)
    
    def RefreshBox(self):
        if self.sim.selectedOptions.currentStartupScript is None:
            self.startupLabel.SetLabel("Current selected startup script: [None]")
        else:
            self.startupLabel.SetLabel("Current selected startup script: [" + self.sim.selectedOptions.currentStartupScript.name + "]")
        
        self.scriptBox.Clear()
        for script in self.sim.savedPresets.startScripts:
            self.scriptBox.Append(script.name)
        
        self.__OnScriptSelect(None)
            
            
    def __OnScriptChange(self, event):
        if self.selectedScript is None:
            return
        else:
            self.selectedScript.script = self.messageText.GetValue()
            
    def __OnScriptSelect(self, event):
        selectedName = self.scriptBox.GetStringSelection()
        print "Select change to " + selectedName
        if (selectedName is None) or (len(selectedName) <= 0):
            self.messageText.SetEditable(False)
            self.selectedScript = None
            self.messageText.SetValue("")
            return
        self.messageText.SetEditable(True)
        for script in self.sim.savedPresets.startScripts:
            if script.name == selectedName:
                self.selectedScript = script
                self.messageText.ChangeValue(script.script)
                self.messageText.SetEditable(True)
                break
               
    def __OnScriptSet(self, event):
        selectedName = self.scriptBox.GetStringSelection()
        if (selectedName is None) or (len(selectedName) <= 0):
            self.sim.selectedOptions.currentStartupScript = None
        else:
            for script in self.sim.savedPresets.startScripts:
                if script.name == selectedName:
                    self.sim.selectedOptions.currentStartupScript = script
                    break
        self.RefreshBox()
        
    def __OnScriptNew(self, event):
        name = wx.GetTextFromUser("Enter Script Name:","Script Name")
        if (name is None) or (len(name) < 0):
            return
        newScript = Simulation.SimScript(name)
        self.sim.savedPresets.startScripts.append(newScript)
        self.RefreshBox()
        
    def __OnScriptDel(self, event):
        selectedName = self.scriptBox.GetStringSelection()
        if (selectedName is None) or (len(selectedName) <= 0):
            return
        for script in self.sim.savedPresets.startScripts:
            if script.name == selectedName:
                if self.sim.selectedOptions.currentStartupScript == script:
                    self.sim.selectedOptions.currentStartupScript = None
                self.sim.savedPresets.startScripts.remove(script)
                break
        self.RefreshBox()
    
class CommandPanel(wx.Panel):
    def __init__(self, parent,sim):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self,-1,"Command panel should go here",(20,20))
    
    
    
class Inject(object):
    def __init__(self,text,protocol,injectText):
        self.text = text
        self.protocol = protocol
        self.injectText = injectText