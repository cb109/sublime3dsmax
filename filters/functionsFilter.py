import sublime
import sublime_plugin
import re
import Filter_Manager

class functionsFilter(Filter_Manager.Filter):
	
	def Filter(self,view, prefix, locations, completions):
		return [("test \tfuntion","test")]

Filter_Manager.CompletionsFilter.addFilter(functionsFilter())