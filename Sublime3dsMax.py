import sublime, sublime_plugin
import tomax

class SendFileToMaxCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        view = sublime.Window.active_view(sublime.active_window())
        print "FILENAME:", view.file_name()

        tomax.sendFile(r"C:\Users\Christoph\Desktop\testit.ms")
