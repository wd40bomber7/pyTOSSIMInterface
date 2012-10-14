'''
Created on Oct 11, 2012

@author: wd40bomber7
'''

if __name__ == '__main__':
    pass


import wx;
import Simulation;
import OutputWindow;
import ConfigWindow;



programState = Simulation.Sim()
programState.LoadPresets()

app = wx.App(False)

#My cheat for preventing cyclic dependencies
programState.WindowBuilders = dict();
programState.WindowBuilders["OutputWindow"] = OutputWindow.OutputWindow
programState.WindowBuilders["ConfigWindow"] = ConfigWindow.ConfigWindow

frame = ConfigWindow.ConfigWindow(programState);

app.MainLoop()

print "Quitted?"

if programState.simulationState.ioReadWrite != None:
    programState.simulationState.ioReadWrite.StopThreads();





