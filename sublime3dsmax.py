"""Send maxscript/python files or codelines to 3ds Max.

This file currently implements 3 commands that you can bind to keys:

    - SendFileToMaxCommand aka send_file_to_max
    - SendSelectionToMaxCommand aka send_selection_to_max
    - OpenMaxHelpCommand aka open_max_help

See the README for details on how to use them.
"""
from __future__ import unicode_literals

import os
import webbrowser

import sublime
import sublime_plugin

# Import depending on Sublime version.
version = int(sublime.version())
ST3 = version >= 3000
if ST3:
    from . import winapi
    from . import filters
    from . import constants
else:
    import winapi
    import filters
    import constants


def _is_maxscriptfile(filepath):
    """Return if the file uses one of the MAXScript file extensions."""
    name, ext = os.path.splitext(filepath)
    return ext in (".ms", ".mcr", ".mse", ".mzp")


def _is_pythonfile(filepath):
    """Return if the file uses a Python file extension."""
    name, ext = os.path.splitext(filepath)
    return ext in (".py")


def _save_to_tempfile(text):
    """Store code in a temporary maxscript file."""
    with open(constants.TEMPFILE, "w") as tempfile:
        if ST3:
            tempfile.write(text)
        else:
            text = text.encode("utf-8")
            tempfile.write(text)


def _send_cmd_to_max(cmd):
    """Try to find the 3ds Max window by title and the mini
    macrorecorder by class.

    Sends a string command and a return-key buttonstroke to it to
    evaluate the command.

    """
    mainwindow = winapi.Window.find_window(constants.TITLE_IDENTIFIER)
    if mainwindow is None:
        sublime.error_message(constants.MAX_NOT_FOUND)
        return

    minimacrorecorder = mainwindow.find_child(text=None, cls="MXS_Scintilla")
    # If the mini macrorecorder was not found, there is still a chance
    # we are targetting an ancient Max version (e.g. 9) where the
    # listener was not Scintilla based, but instead a rich edit box.
    if minimacrorecorder is None:
        statuspanel = mainwindow.find_child(text=None, cls="StatusPanel")
        if statuspanel is None:
            sublime.error_message(constants.RECORDER_NOT_FOUND)
            return
        minimacrorecorder = statuspanel.find_child(text=None, cls="RICHEDIT")
        # Verbatim strings (the @ at sign) are also not yet supported.
        cmd = cmd.replace("@", "")
        cmd = cmd.replace("\\", "\\\\")

    if minimacrorecorder is None:
        sublime.error_message(constants.RECORDER_NOT_FOUND)
        return

    sublime.status_message('Send to 3ds Max: {cmd}'.format(
        **locals())[:-1])  # Cut ';'
    cmd = cmd.encode("utf-8")  # Needed for ST3!
    minimacrorecorder.send(winapi.WM_SETTEXT, 0, cmd)
    minimacrorecorder.send(winapi.WM_CHAR, winapi.VK_RETURN, 0)
    minimacrorecorder = None


class SendFileToMaxCommand(sublime_plugin.TextCommand):
    """Send the current file by using 'fileIn <file>'."""

    def run(self, edit):
        currentfile = self.view.file_name()
        if currentfile is None:
            sublime.error_message(constants.NOT_SAVED)
            return

        if _is_maxscriptfile(currentfile):
            cmd = 'fileIn (@"{currentfile}")\r\n'.format(**locals())
            _send_cmd_to_max(cmd)

        elif _is_pythonfile(currentfile):
            cmd = constants.PYTHON_COMMAND_TEMPLATE.format(
                filepath=currentfile)
            _send_cmd_to_max(cmd)

        else:
            sublime.error_message(constants.NO_MXS_FILE)


class SendSelectionToMaxCommand(sublime_plugin.TextCommand):
    """Send selected part of the file.

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
                _send_cmd_to_max(cmd)

            # Else send all lines where something is selected
            # This only works by saving to a tempfile first,
            # as the mini macro recorder does not accept multiline input
            else:
                line = self.view.line(region)
                self.view.run_command("expand_selection",
                                      {"to": line.begin()})
                regiontext = self.view.substr(self.view.line(region))
                _save_to_tempfile(regiontext)
                if os.path.exists(constants.TEMPFILE):
                    if currentfile:
                        if _is_maxscriptfile(currentfile):
                            cmd = 'fileIn (@"%s")\r\n' % constants.TEMPFILE
                        else:
                            cmd = ('python.executefile (@"%s")\r\n' %
                                   constants.TEMPFILE)
                        _send_cmd_to_max(cmd)
                    else:
                        sublime.error_message(constants.NO_FILE)
                else:
                    sublime.error_message(constants.NO_TEMP)


class OpenMaxHelpCommand(sublime_plugin.TextCommand):
    """Open the online MAXScript help searching for the current selection."""

    # Based on: https://forum.sublimetext.com/t/select-word-under-cursor-for-further-processing/10913  # noqa
    def run(self, edit):
        for region in self.view.sel():
            if region.begin() == region.end():
                word = self.view.word(region)
            else:
                word = region
            if not word.empty():
                key = self.view.substr(word)
                query_param = "?query=" + key
                url = constants.ONLINE_MAXSCRIPT_HELP_URL + query_param
                webbrowser.open(url, new=0, autoraise=True)


class Completions(sublime_plugin.EventListener):
    """Handle auto-completion from file content and the official API.

    To test this feature try typing the following in a .ms file:
        polyOps.
    It should offer autocompletions like:
        polyOps.retriangulate
        polyOps.autosmooth
        ...
    """
    completions_list = []

    def is_mxs(self, view):
        return view.match_selector(view.id(), "source.maxscript")

    def on_activated(self, view):
        if self.is_mxs(view) and not self.completions_list:
            self.completions_list = [line.rstrip('\n')
                                     for line in open(constants.APIPATH)]

    def on_query_completions(self, view, prefix, locations):
        if self.is_mxs(view):
            self.completions_list = [line.rstrip('\n')
                                     for line in open(constants.APIPATH)]
            comp_default = set(view.extract_completions(prefix))
            completions = set(list(self.completions_list))
            comp_default = comp_default - completions
            completions = list(comp_default) + list(completions)
            completions = [(attr, attr) for attr in completions]
            completions = filters.manager.apply_filters(
                view, prefix, locations, completions)
            return completions


def plugin_unloaded():
    """Perform cleanup work."""
    if os.path.isfile(constants.TEMPFILE):
        try:
            os.remove(constants.TEMPFILE)
        except OSError:
            pass
