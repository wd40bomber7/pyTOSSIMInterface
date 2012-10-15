'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

import wx
import os.path
import subprocess
import base64
import StringIO
#Windows to open

class MainWindow(wx.Frame):
    '''
    This class is the primary window of the TOSSIM Interface
    '''
        
    frameIcon = StringIO.StringIO(base64.b64decode("R0lGODlhEAAQALMAAP38/fj3+fT09sHBwuXm8crP4oSOsBMxfq+xtkZolky26NPU0vDw7ujo593d3P///ywAAAAAEAAQAAAEf1CghN4js9hijDCKcgxAoiQHUIQHih4G0KKEMcNHXpT58RQ9w8OQ2F0SCcImEXsIFgDLRSN1KB+MgYPRaDi23cWiUV0MEIOzeuGISrEI8RnBeL/HXEfYbgGQvF8BA3wWCE9iDhKED3RpZgwVhIMOiA9QfABoCJuahB9IoExuDxEAOw=="))

    def __init__(self,sim,title):
        '''
        Constructor
        '''
        print "ENTERED"
        super(MainWindow,self).__init__(None, title="TOSSIM Interface - " + title, size=(500,400))
        
        self.topoPaths = dict();
        self.noisePaths = dict();
        self.__menuItems = list();
        self.__boundEvents = list(); #A list of events bound to the menu. Unbound during regeneration
        self.sim = sim;
        self.sim.openWindows.append(self)
        
        #self.RebuildMenus();
        self.Bind(wx.EVT_CLOSE, self.__OnClose, self)

        #add an icon for cool factor
        self.frameIcon.seek(0);
        img = wx.EmptyImage()
        img.LoadStream(self.frameIcon,wx.BITMAP_TYPE_GIF)
        ico = wx.EmptyIcon()
        ico.CopyFromBitmap(img.ConvertToBitmap());
        self.SetIcon(ico);
        
        self.simulationMenu = wx.Menu()
        self.RegisterMenu(self.simulationMenu);
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.simulationMenu,"Simulation")
        self.SetMenuBar(self.menuBar);
        
    def RegisterMenu(self,menu):
        self.__menuItems.append(menu)
    def RebuildMenus(self):
        self.__CleanMenus();
        #Build menus
        
        
        #Simulation Menu
        
        self.AddMenuItem(self.simulationMenu, "Open Output Window", self.__OnShowOutput)
        self.AddMenuItem(self.simulationMenu, "Open Topo Edit Window", self.__OnShowTopo)
        self.AddMenuItem(self.simulationMenu, "Open Command Inject Window", self.__OnShowCommand)
        self.AddMenuItem(self.simulationMenu, "Open Simulation Options Window", self.__OnShowOptions)
        self.simulationMenu.AppendSeparator()

        self.startButton = self.AddMenuItem(self.simulationMenu, "Start", self.__OnSimulationStart)
        self.pauseButton = self.AddMenuItem(self.simulationMenu, "Resume" if self.sim.simulationState.simIsPaused else "Pause", self.__OnSimulationPause)
        self.stopButton = self.AddMenuItem(self.simulationMenu, "Stop", self.__OnSimulationStop)
        self.startButton.Enable(not self.sim.simulationState.simIsRunning)
        self.pauseButton.Enable(self.sim.simulationState.simIsRunning)
        self.stopButton.Enable(self.sim.simulationState.simIsRunning)
        
        #Help Menu
        #self.AddMenuItem(self.helpMenu, "About", self.__OnHelpAbout)
        
       
        #self.SetMenuBar(menuBar)
        return self.menuBar
    def WindowType(self):
        return -1
    
    def AddMenuItem(self, addToMenu, text, bindTo = None, checked = None):
        if checked != None:
            addToMenu.AppendCheckItem(wx.ID_ANY,text);
        else:
            addToMenu.Append(wx.ID_ANY,text);
        
        item = addToMenu.GetMenuItems()[len(addToMenu.GetMenuItems())-1]
        if checked != None:
            item.Check(checked)
        if bindTo != None:
            self.Bind(wx.EVT_MENU, bindTo, item)
            self.__boundEvents.append(item) #hack to make my menus work. Hehe sneakys
        #if not addToMenu in self.__menuItems:
            #addToMenu.myItems = list()
            #self.__menuItems.append(addToMenu)
        #addToMenu.myItems.append(item.GetId());
        return item;

    def __CleanMenus(self):
        for event in self.__boundEvents:
            self.Unbind(wx.EVT_MENU,event);
        del self.__boundEvents[:]
        for menu in self.__menuItems:
            while (menu.GetMenuItemCount() > 0):
                item = menu.FindItemByPosition(0);
                menu.RemoveItem(item);
        print "Menus cleaned"

    def __OnClose(self, event):
        self.sim.openWindows.remove(self);
        self.Destroy();
        
        
    def __OnSimulationStart(self, event):
        if len(self.sim.selectedOptions.childPythonName) <= 0:
            self.displayError("You must set a python file to run in the config window.")
        
    def __OnSimulationPause(self, event):
        '''
        stub
        '''       
    def __OnSimulationStop(self, event):
        '''
        stub
        '''
    #For the windows menu
    def __OnShowOptions(self, event):
        for window in self.sim.openWindows:
            if window.WindowType() == 2:
                window.Iconize(False) #unminimize the window.
                window.Raise()
                return
        self.sim.WindowBuilders["ConfigWindow"](self.sim);
            
        
    def __OnShowOutput(self, event):
        self.sim.WindowBuilders["OutputWindow"](self.sim)
        
    def __OnShowTopo(self, event):
        '''
        stub   
        '''
    def __OnShowCommand(self, event):
        '''
        stub   
        '''
    def __OnShowNoise(self, event):
        '''
        stub   
        '''
    #For the help menu
    def __OnHelpAbout(self, event):
        '''
        stub   
        '''
    def displayError(self,msg):
        dialog = wx.MessageDialog(parent=None,message=msg,caption="Error",style=wx.OK|wx.ICON_INFORMATION);
        dialog.ShowModal();
        dialog.Destroy(); 
        
    #other methods
    def __findProgram(self,program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    
        return None