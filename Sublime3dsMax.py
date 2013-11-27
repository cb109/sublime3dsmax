import sublime, sublime_plugin
import os
import tomax

TEMP = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp.ms")

LISTENER_NOT_FOUND = r"Sublime3dsMax: Could not find MAXScript Listener"
NO_MXS_FILE = r"Sublime3dsMax: File is not a MAXScript file (*.ms, *.mcr)"
NO_TEMP = r"Sublime3dsMax: Could not write to temp file"

def isMaxscriptFile(file):
    name, ext = os.path.splitext(file)
    if ext in (".ms", ".mcr"):
        return True
    else:
        return False

def sendCmdToMax(cmd):
    tomax.connectToMax() # Always connect first
    if tomax.gMiniListener:
        tomax.fireCommand(cmd)
        tomax.gMiniListener = None # Reset for next reconnect
    else:
        print LISTENER_NOT_FOUND

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

        if isMaxscriptFile(currentfile):
            cmd = r'fileIn (@"%s");' % currentfile
            sendCmdToMax(cmd)
        else:
            print NO_MXS_FILE


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
            # as the mini listener does not accept multiline input
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
                    print NO_TEMP
