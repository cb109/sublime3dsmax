import sublime
import sublime_plugin
import re

class FilterManager(object):

    Filters = []

    def addFilter(self,cfilter,index=None):
        if index == None:
            self.Filters.append(cfilter)
        else:
            self.Filters.insert(index,cfilter)

    def ApplyFilters(self,view, prefix, locations, completions):
        print self.Filters
        for f in self.Filters:
            if f.Filter(view, prefix, locations, completions) != None:
                completions = f.Filter(view, prefix, locations, completions)
                
        return completions

class Filter(object):

    def Filter(self,view, prefix, locations, completions):
        pass

CompletionsFilter = FilterManager()
CompletionsFilter.addFilter(Filter())
import filters