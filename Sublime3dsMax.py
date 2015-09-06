"""Send maxscript files or codelines to 3ds Max."""

from __future__ import unicode_literals

import os
import sublime
import sublime_plugin

# Import depending on Sublime version
version = int(sublime.version())
ST3 = version > 3000 or version == ""
if ST3:
    from . import winapi
else:
    import winapi


# Create the tempfile in "Packages" (ST2) / "Installed Packages" (ST3)
TEMP = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "Send_to_3ds_Max_Temp.ms")

TITLE_IDENTIFIER   = "Autodesk 3ds Max"
PREFIX             = "Sublime3dsMax:"
NO_MXS_FILE        = PREFIX + " File is not a MAXScript file (*.ms, *.mcr)"
NO_TEMP            = PREFIX + " Could not write to temp file"
NOT_SAVED          = PREFIX + " File must be saved before sending to 3ds Max"
MAX_NOT_FOUND      = PREFIX + " Could not find a 3ds max instance."
RECORDER_NOT_FOUND = PREFIX + " Could not find MAXScript Macro Recorder"
NO_FILE            = PREFIX + " No file currently open"


def is_maxscriptfile(filepath):
    name, ext = os.path.splitext(filepath)
    return ext in (".ms", ".mcr")


def is_pythonfile(filepath):
    name, ext = os.path.splitext(filepath)
    return ext in (".py")


def send_cmd_to_max(cmd):
    """Tries to find the 3ds Max window by title and the mini
    macrorecorder by class.

    Sends a string command and a return-key buttonstroke to it to
    evaluate the command.

    """
    mainwindow = winapi.Window.find_window(TITLE_IDENTIFIER)
    if mainwindow is None:
        sublime.error_message(MAX_NOT_FOUND)
        return

    minimacrorecorder = mainwindow.find_child(text=None, cls="MXS_Scintilla")
    # If the mini macrorecorder was not found, there is still a chance
    # we are targetting an ancient Max version (e.g. 9) where the
    # listener was not Scintilla based, but instead a rich edit box.
    if minimacrorecorder is None:
        statuspanel = mainwindow.find_child(text=None, cls="StatusPanel")
        if statuspanel is None:
            sublime.error_message(RECORDER_NOT_FOUND)
            return
        minimacrorecorder = statuspanel.find_child(text=None, cls="RICHEDIT")
        # Verbatim strings (the @ at sign) are also not yet supported.
        cmd = cmd.replace("@", "")
        cmd = cmd.replace("\\", "\\\\")

    if minimacrorecorder is None:
        sublime.error_message(RECORDER_NOT_FOUND)
        return

    sublime.status_message('Send to 3ds Max: {cmd}'.format(
        **locals())[:-1])  # Cut ';'
    cmd = cmd.encode("utf-8")  # Needed for ST3!
    minimacrorecorder.send(winapi.WM_SETTEXT, 0, cmd)
    minimacrorecorder.send(winapi.WM_CHAR, winapi.VK_RETURN, 0)
    minimacrorecorder = None


def save_to_tempfile(text):
    """Stores code in a temporary maxscript file."""
    with open(TEMP, "w") as tempfile:
        if ST3:
            tempfile.write(text)
        else:
            text = text.encode("utf-8")
            tempfile.write(text)


class SendFileToMaxCommand(sublime_plugin.TextCommand):
    """Sends the current file by using 'fileIn <file>'."""

    def run(self, edit):
        currentfile = self.view.file_name()
        if currentfile is None:
            sublime.error_message(NOT_SAVED)
            return

        if is_maxscriptfile(currentfile):
            cmd = 'fileIn (@"{currentfile}")\r\n'.format(**locals())
            send_cmd_to_max(cmd)

        elif is_pythonfile(currentfile):
            cmd = 'python.executefile (@"%s")\r\n' % currentfile
            send_cmd_to_max(cmd)

        else:
            sublime.error_message(NO_MXS_FILE)


class SendSelectionToMaxCommand(sublime_plugin.TextCommand):
    """Sends selected part of the file.

    Selection is extended to full line(s).

    """
    def run(self, edit):
        currentfile = self.view.file_name()
        for region in self.view.sel():
            text = None

            # If nothing selected, send single line
            if region.empty():
                line = self.view.line(region)
                text = self.view.substr(line)
                cmd = '{text};'.format(**locals())
                send_cmd_to_max(cmd)

            # Else send all lines where something is selected
            # This only works by saving to a tempfile first,
            # as the mini macro recorder does not accept multiline input
            else:
                line = self.view.line(region)
                self.view.run_command("expand_selection",
                                     {"to": line.begin()})
                regiontext = self.view.substr(self.view.line(region))
                save_to_tempfile(regiontext)
                if os.path.exists(TEMP):
                    if currentfile:
                        if is_maxscriptfile(currentfile):
                            cmd = 'fileIn (@"%s")\r\n' % TEMP
                        else:
                            cmd = 'python.executefile (@"%s")\r\n' % TEMP
                        send_cmd_to_max(cmd)
                    else:
                        sublime.error_message(NO_FILE)
                else:
                    sublime.error_message(NO_TEMP)
