"""Send maxscript/python files or codelines to 3ds Max.

This is the main sublime plugin file. It currently implements 4 commands
that you can bind to keys:

    - SendFileToMaxCommand aka send_file_to_max
    - SendSelectionToMaxCommand aka send_selection_to_max
    - SelectMaxInstanceCommand aka select_max_instance
    - OpenMaxHelpCommand aka open_max_help

See the README for details on how to use them.
"""
from __future__ import unicode_literals

import os
import webbrowser
import zipfile

import sublime
import sublime_plugin

# Import depending on Sublime version.
ST3 = int(sublime.version()) >= 3000
if ST3:
    from . import winapi
    from . import filters
    from . import constants
else:
    import winapi
    import filters
    import constants

__version__ = "0.9.8"

# Holds the current 3ds Max window object that we send commands to.
# It is filled automatically when sending the first command.
mainwindow = None

# Used to preselect the last 3ds Max window in the quick panel.
last_index = 0


def _get_api_lines():
    """Read the mxs API definition file and return as a list of lines."""
    def get_decoded_lines(file_obj):
        content = file_obj.read()
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            pass
        return content.split("\n")

    # Zipped .sublime-package as installed by package control.
    if ".sublime-package" in constants.APIPATH:
        apifile = os.path.basename(constants.APIPATH)
        package = zipfile.ZipFile(os.path.dirname(constants.APIPATH), "r")
        return get_decoded_lines(package.open(apifile))
    # Expanded folder, e.g. during development.
    else:
        return get_decoded_lines(open(constants.APIPATH))


def _is_maxscriptfile(filepath):
    """Return if the file uses one of the MAXScript file extensions."""
    name, ext = os.path.splitext(filepath)
    return ext in (".ms", ".mcr", ".mse", ".mzp")


def _is_pythonfile(filepath):
    """Return if the file uses a Python file extension."""
    name, ext = os.path.splitext(filepath)
    return ext in (".py",)


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
    global mainwindow

    if mainwindow is None:
        mainwindow = winapi.Window.find_window(
            constants.TITLE_IDENTIFIER)

    if mainwindow is None:
        sublime.error_message(constants.MAX_NOT_FOUND)
        return

    try:
        mainwindow.find_child(text=None, cls="MXS_Scintilla")
    except OSError:
        # Window handle is invalid, 3ds Max has probably been closed.
        # Call this function again and try to find one automatically.
        mainwindow = None
        _send_cmd_to_max(cmd)
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

        is_mxs = _is_maxscriptfile(currentfile)
        is_python = _is_pythonfile(currentfile)

        if is_mxs:
            cmd = 'fileIn @"{0}"\r\n'.format(currentfile)
            _send_cmd_to_max(cmd)
        elif is_python:
            cmd = 'python.executeFile @"{0}"\r\n'.format(currentfile)
            _send_cmd_to_max(cmd)
        else:
            sublime.error_message(constants.NO_SUPPORTED_FILE)


class SendSelectionToMaxCommand(sublime_plugin.TextCommand):
    """Send selected part of the file.

    Selection is extended to full line(s).

    """
    def expand(self, line):
        """Expand selection to encompass whole line."""
        self.view.run_command("expand_selection", {"to": line.begin()})

    def run(self, edit):
        """Analyse selection and determine a method to send it to 3ds Max.

        Single line maxscript commands can be send directly. Python
        commands could, but since we wrap them we may get issues with
        quotation marks or backslashes, so it is safer to send them via
        a temporary file that we import. That is also the method to send
        multiline code, since the mini macrorecorder does not accept
        multiline input.
        """
        def get_mxs_tempfile_import():
            return 'fileIn @"{0}"\r\n'.format(constants.TEMPFILE)

        def get_python_tempfile_import():
            return 'python.executeFile @"{0}"\r\n'.format(constants.TEMPFILE)

        # We need the user to have an actual file opened so that we can
        # derive the language from its file extension.
        currentfile = self.view.file_name()
        if not currentfile:
            sublime.error_message(constants.NOT_SAVED)
            return

        is_mxs = _is_maxscriptfile(currentfile)
        is_python = _is_pythonfile(currentfile)

        regions = [region for region in self.view.sel()]
        for region in regions:
            line = self.view.line(region)
            text = self.view.substr(line)

            is_empty = region.empty()
            is_singleline = len(text.split("\n")) == 1
            is_multiline = not (is_empty or is_singleline)

            if is_multiline:
                self.expand(line)
                _save_to_tempfile(text)
                if not os.path.isfile(constants.TEMPFILE):
                    sublime.error_message(constants.NO_TEMP)
                    return

                if is_mxs:
                    cmd = get_mxs_tempfile_import()
                else:
                    cmd = get_python_tempfile_import()

                _send_cmd_to_max(cmd)
                return
            else:
                if is_empty:
                    self.expand(line)
                    text = self.view.substr(self.view.line(region))
                elif is_singleline:
                    text = self.view.substr(region)

                if is_mxs:
                    cmd = '{0}\r\n'.format(text)
                elif is_python:
                    _save_to_tempfile(text)
                    if not os.path.isfile(constants.TEMPFILE):
                        sublime.error_message(constants.NO_TEMP)
                        return
                    cmd = get_python_tempfile_import()

                _send_cmd_to_max(cmd)
                return


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


class SelectMaxInstanceCommand(sublime_plugin.TextCommand):
    """Display a dialog of open 3ds Max instances to pick one.

    The chosen instance is used from then on to send commands to.
    """
    def run(self, edit):
        item2window = {}
        candidates = winapi.Window.find_windows(
            constants.TITLE_IDENTIFIER)
        for window in candidates:
            text = window.get_text()
            normtext = text.replace("b'", "").replace("'", "")
            item = ("{txt} ({hwnd})".format(txt=normtext,
                                            hwnd=window.get_handle()))
            item2window[item] = window

        items = list(item2window.keys())

        def on_select(idx):
            if idx == -1:
                return

            global last_index
            last_index = idx

            item = items[idx]
            global mainwindow
            mainwindow = item2window[item]

            sublime.message_dialog(constants.PREFIX +
                                   " Now connected to: \n\n" + item)

        def on_highlighted(idx):
            pass

        sublime.active_window().show_quick_panel(items,
                                                 on_select,
                                                 0,
                                                 last_index,
                                                 on_highlighted)


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
            self.completions_list = _get_api_lines()

    def on_query_completions(self, view, prefix, locations):
        if self.is_mxs(view):
            self.completions_list = _get_api_lines()
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
