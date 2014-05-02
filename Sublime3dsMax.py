#   Know issues: In ST3 there seems to be a problem pasting the cmd to 3ds Max.
#   Probably related to ctypes (pressing ENTER etc.) in Python 3.
#   Until fixed this plugin only works for ST2.
#   @dgsantana: the problems were due to unicode in python 3, add __future__ to made it compatible with ST2
from __future__ import print_function, absolute_import, unicode_literals, with_statement
import sublime
import sublime_plugin
import os
import sys

# ST3 import fix
version = (int)(sublime.version())
if version > 3000 or version == "":
    plugin_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(plugin_path)
#import tomax

from . import winapi

# Create the tempfile in "Packages" (ST2) / "Installed Packages" (ST3)
TEMP = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "Send_to_3ds_Max_Temp.ms"
)
NO_MXS_FILE = r"Sublime3dsMax: File is not a MAXScript file (*.ms, *.mcr)"
NO_TEMP = r"Sublime3dsMax: Could not write to temp file"
NOT_SAVED = r"Sublime3dsMax: File must be saved before sending to 3ds Max"
MAX_NOT_FOUND = r"Sublime3dsMax: Could not find a 3ds max instance."
RECORDER_NOT_FOUND = r"Sublime3dsMax: Could not find MAXScript Macro Recorder"


def isMaxscriptFile(file):
    name, ext = os.path.splitext(file)
    if ext in (".ms", ".mcr"):
        return True
    else:
        return False


def sendCmdToMax(cmd):
    sublime.status_message('Connecting to 3ds Max')
    gMainWindow = winapi.Window.find_window(r'Autodesk 3ds Max')
    gMiniMacroRecorder = None
    if gMainWindow is not None:
        gMiniMacroRecorder = gMainWindow.find_child(text=None, cls='MXS_Scintilla')
    else:
        sublime.error_message(MAX_NOT_FOUND)
    if gMiniMacroRecorder is not None:
        gMiniMacroRecorder.send(0x0C, 0, cmd)
        gMiniMacroRecorder.send(0x102, 0x0D, 0)
        gMiniMacroRecorder = None
    else:
        sublime.error_message(RECORDER_NOT_FOUND)


def saveToTemp(text):
    global TEMP
    tempfile = open(TEMP, "w")
    tempfile.write(text)
    tempfile.close()


class SendFileToMaxCommand(sublime_plugin.TextCommand):
    """ Sends the current file by using 'fileIn <file>'.
    """
    def run(self, edit):
        currentfile = self.view.file_name()
        if currentfile is None:
            sublime.error_message(NOT_SAVED)
            return

        if isMaxscriptFile(currentfile):
            cmd = 'fileIn (@"%s");' % currentfile
            sendCmdToMax(cmd)
        else:
            sublime.error_message(NO_MXS_FILE)


class SendSelectionToMaxCommand(sublime_plugin.TextCommand):
    """ Sends selected part of the file.
        Selection is extended to full line(s).
    """
    def run(self, edit):
        for region in self.view.sel():
            text = None

            # If nothing selected, send single line
            if region.empty():
                line = self.view.line(region)
                text = self.view.substr(line)
                cmd = '%s;' % text
                sendCmdToMax(cmd)

            # Else send all lines where something is selected
            # This only works by saving to a tempfile first,
            # as the mini macro recorder does not accept multiline input
            else:
                line = self.view.line(region)
                self.view.run_command("expand_selection", {"to": line.begin()})
                regiontext = self.view.substr(self.view.line(region))
                saveToTemp(regiontext)
                global TEMP
                if os.path.exists(TEMP):
                    cmd = 'fileIn (@"%s");' % TEMP
                    sendCmdToMax(cmd)
                else:
                    sublime.error_message(NO_TEMP)
