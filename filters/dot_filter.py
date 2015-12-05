import sublime
import sublime_plugin
import re
import Filter_Manager

class dotFilter(Filter_Manager.Filter):

    def dotfilter(self,view):
        dot = view.substr(sublime.Region(view.sel()[0].a -1 ,view.sel()[0].b))
        if ord(dot[0]) == 46:
            return True
        else:
            return False

    def Filter(self,view, prefix, locations, completions):
        if self.dotfilter(view):
            completions_list_filter = []
            wordstart = view.word(sublime.Region(view.sel()[0].a -1 ,view.sel()[0].b)).a
            prefix = view.substr(sublime.Region(wordstart,view.sel()[0].b))
            for c in completions:
                try:
                    if len(prefix) > 0 :
                        if prefix.lower() in c[0].lower()[0:len(prefix)]:
                            completions_list_filter.append((c[0],c[1]))

                except UnicodeDecodeError:
                    continue
            return completions_list_filter


Filter_Manager.CompletionsFilter.addFilter(dotFilter())