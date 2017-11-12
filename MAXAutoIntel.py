# Copyright (c) 2014, Luca Faggion
# All rights reserved.
#
#This file is provided under the following terms:
#
#		*Attribution:You must give appropriate credit, provide a link to the license, 
#		 and indicate if changes were made. You may do so in any reasonable manner, but 
#		 not in any way that suggests the licensor endorses you or your use.
#		*ShareAlike: If you remix, transform, or build upon the material, you must 
#		 distribute your contributions under the same license as the original.
#		*No additional restrictions: You may not apply legal terms or technological measures
#		 that legally restrict others from doing anything the license permits.
#
# license : http://creativecommons.org/licenses/by-sa/4.0/legalcode

import os
import sublime
import sublime_plugin
import re
import json

class AutoCompleteFilter(sublime_plugin.EventListener):

	#filter completions based on a string / return Completion_List_filter
	def APICompletionsFilter(self,typedWord,completions,view):
		completions_list_filter = []
		rg = view.line(view.sel()[0])
		dotRG = view.word(view.sel()[0])
		dot = view.substr(dotRG)
		dotEn = dot.encode("hex")
		if dotEn[0:2] == "2e":

			#select the word that is needed to filter the completion list
			selprev = view.substr(view.word(sublime.Region(dotRG.a - 2, dotRG.b - 2)))
			selprev = selprev.replace(".","")
			selprev = re.sub(r'[^\w]', ' ', selprev)
			selprev = selprev.replace(" ", "")
			selprev = selprev + "."
			chShift = len(selprev)
			for c in completions:
				try:
					if len(selprev) > 0 :
						if selprev.lower() in c.lower()[0:chShift]:
							completions_list_filter.append((c,c))

				except UnicodeDecodeError:
					print(c)
					continue
			return completions_list_filter
		else:
			for c in completions:
				try:
					if len(typedWord) > 0:
						if typedWord.lower() in c.lower():
							completions_list_filter.append((c,c))

				except UnicodeDecodeError:
					print(c)
					continue

			return completions_list_filter


	def on_query_completions(self, view, prefix, locations):
		if view.match_selector(view.id(),"source.maxscript"):
			# extend word-completions
			Default = view.extract_completions(prefix)
			completions = self.APICompletionsFilter(prefix,Default,view)
			return completions
