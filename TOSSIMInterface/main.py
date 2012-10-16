'''
Created on Oct 11, 2012

@author: wd40bomber7
'''

if __name__ == '__main__':
    pass


import wx
import Simulation
import OutputWindow
import ConfigWindow
import TopoWindow
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o","--override-config",action="store_true",dest="override", default = False,
                  help="Prevents config changes from being saved")
parser.add_option("-p","--python-child",dest="pythonChild", default=None, metavar="FILE",
                  help="Selects the tC.py python child process")
parser.add_option("-t","--topo",dest="topo", default=None, metavar="FILE",
                  help="Selects the topo file loaded");
parser.add_option("-n","--noise",dest="noise", default=None, metavar="FILE",
                  help="Selects the noise file loaded");                 
parser.add_option("-c","--channels",dest="channels", default=None,
                  help="A comma separated list of channels");
parser.add_option("-s","--start",action="store_true",dest="start", default=False,
                  help="Start the simulation immediately")
parser.add_option("-w","--window",dest="window", default=None,
                  help="Choose window to start immediately. Options: config,output,topo");

(options, args) = parser.parse_args(sys.argv)

programState = Simulation.Sim()
if options.override:
    programState.EnableOverride()    
programState.LoadPresets()

if not options.pythonChild is None:
    programState.selectedOptions.childPythonName = options.pythonChild;
if not options.topo is None:
    programState.selectedOptions.topoFileName = options.topo;
if not options.noise is None:
    programState.selectedOptions.noiseFileName = options.noise;
if not options.channels is None:
    programState.selectedOptions.channelList = options.channels.split(",")


    

app = wx.App(False)

#My cheat for preventing cyclic dependencies
programState.WindowBuilders = dict();
programState.WindowBuilders["OutputWindow"] = OutputWindow.OutputWindow
programState.WindowBuilders["ConfigWindow"] = ConfigWindow.ConfigWindow
programState.WindowBuilders["TopoWindow"] = TopoWindow.TopoWindow

if options.window is None:
    frame = ConfigWindow.ConfigWindow(programState);
elif options.window == "config":
    frame = ConfigWindow.ConfigWindow(programState);
elif options.window == "output":
    frame = OutputWindow.OutputWindow(programState);
else:
    print "Invalid options for -w, type -h or --help to print help."
    exit()
    

if options.start:
    frame.StartSimulation()

app.MainLoop()

print "Quitted?"

if programState.simulationState.ioReadWrite != None:
    programState.simulationState.ioReadWrite.StopThreads();





