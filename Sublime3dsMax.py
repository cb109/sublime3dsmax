import sublime
import sublime_plugin
import os
import sys

version = (int) (sublime.version())
if version > 3000 or version == "":
    plugin_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(plugin_path)
import tomax

print ("TOMAX:", tomax)

# Create the tempfile in "Installed Packages"
TEMP = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
	"Send_to_3ds_Max_Temp.ms"
)

print ("TEMP:", TEMP)

NO_MXS_FILE = r"Sublime3dsMax: File is not a MAXScript file (*.ms, *.mcr)"
NO_TEMP = r"Sublime3dsMax: Could not write to temp file"
NOT_SAVED = r"Sublime3dsMax: File must be saved before sending to 3ds Max"
MAX_NOT_FOUND = r"Sublime3dsMax: Could not find a 3ds max instance."
RECORDER_NOT_FOUND = r"Sublime3dsMax: Could not find MAXScript Macro Recorder"
teapot();
def isMaxscriptFile(file):
    name, ext = os.path.splitext(file)
    if ext in (".ms", ".mcr"):
        return True
    else:
        return False

def sendCmdToMax(cmd):
    if not tomax.connectToMax(): # Always connect first
        sublime.error_message(MAX_NOT_FOUND)
        return
    if tomax.gMiniMacroRecorder:
        tomax.fireCommand(cmd)
        tomax.gMiniMacroRecorder = None # Reset for next reconnect
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
            cmd = r'fileIn (@"%s");' % currentfile
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
                cmd = r'%s;' % text
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
                    cmd = r'fileIn (@"%s");' % TEMP
                    sendCmdToMax(cmd)
                else:
                    sublime.error_message(NO_TEMP)
