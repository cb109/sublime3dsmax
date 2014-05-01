""" Send maxscript files or codelines to 3ds Max.
    
    Known issues that need to be fixed:
        - Sending a multiline selection is currently broken (maybe ST3 API for that changed?)
        - The maxscript syntax coloring file does not work/is not recognized 
"""


import os
import sys
import sublime
import sublime_plugin

# ST3 import fix
version = (int)(sublime.version())
if version > 3000 or version == "":
    plugin_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(plugin_path)

import winapi


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

MAX_TITLE_IDENTIFIER = r"Autodesk 3ds Max"


def isMaxscriptFile(file):
    """ Checks if file is a maxscript by extension. 
    """
    name, ext = os.path.splitext(file)
    if ext in (".ms", ".mcr"):
        return True
    else:
        return False


def sendCmdToMax(cmd):
    """ Tries to find the 3ds Max window by title and 
    the mini macrorecorder by class. Sends a string command 
    and a return-key buttonstroke to it to evaluate the command.
    """
    gMainWindow = winapi.Window.find_window(MAX_TITLE_IDENTIFIER)
    gMiniMacroRecorder = None
    if gMainWindow is not None:
        gMiniMacroRecorder = gMainWindow.find_child(text=None, cls="MXS_Scintilla")
    else:
        sublime.error_message(MAX_NOT_FOUND)
    if gMiniMacroRecorder is not None:
        sublime.status_message('Send to 3ds Max: {cmd}'.format(**locals())[:-1])  # Cut ';'
        cmd = cmd.encode("utf-8")  # Needed for ST3!
        gMiniMacroRecorder.send(winapi.WM_SETTEXT, 0, cmd)
        gMiniMacroRecorder.send(winapi.WM_CHAR, winapi.VK_RETURN, 0)
        gMiniMacroRecorder = None
    else:
        sublime.error_message(RECORDER_NOT_FOUND)


def saveToTempFile(text):
    """ Stores code in a temporary maxscript file. 
    """
    with open(TEMP, "w") as tempFile:
        tempFile.write(text)


class SendFileToMaxCommand(sublime_plugin.TextCommand):
    """ Sends the current file by using 'fileIn <file>'.
    """
    def run(self, edit):
        currentfile = self.view.file_name()
        if currentfile is None:
            sublime.error_message(NOT_SAVED)
            return

        if isMaxscriptFile(currentfile):
            cmd = 'fileIn (@"{currentfile}");'.format(**locals())
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
                cmd = '{text};'.format(**locals())
                sendCmdToMax(cmd)

            # Else send all lines where something is selected
            # This only works by saving to a tempfile first,
            # as the mini macro recorder does not accept multiline input
            else:
                line = self.view.line(region)
                self.view.run_command("expand_selection", {"to": line.begin()})
                regiontext = self.view.substr(self.view.line(region))
                saveToTempFile(regiontext)
                global TEMP
                if os.path.exists(TEMP):
                    cmd = r'fileIn (@"{TEMP}");'.format(**locals())
                    sendCmdToMax(cmd)
                else:
                    sublime.error_message(NO_TEMP)
