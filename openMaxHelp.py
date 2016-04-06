import sublime, sublime_plugin
import subprocess
import webbrowser

'''
Code taken from : https://forum.sublimetext.com/t/select-word-under-cursor-for-further-processing/10913
'''
class open_max_help(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if region.begin() == region.end():
                word = self.view.word(region)
            else:
                word = region
            if not word.empty():
                key = self.view.substr(word)
                url = "http://docs.autodesk.com/3DSMAX/16/ENU/MAXScript-Help//index.html?query=" + key
                webbrowser.open(url, new=0, autoraise=True)