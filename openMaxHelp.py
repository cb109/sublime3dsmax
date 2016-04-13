import sublime, sublime_plugin
import subprocess
import webbrowser


ONLINE_MAXSCRIPT_HELP_URL = r"http://docs.autodesk.com/3DSMAX/16/ENU/MAXScript-Help/index.html"  # noqa


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
                url = ONLINE_MAXSCRIPT_HELP_URL + query_param
                webbrowser.open(url, new=0, autoraise=True)