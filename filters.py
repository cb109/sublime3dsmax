"""Filtering for auto-completion."""

import sublime


class _BaseFilter(object):
    """Subclass this."""

    def filter(self, view, prefix, locations, completions):
        pass


class DotFilter(_BaseFilter):
    """Provide matching completions when typing a `.` after a keyword."""

    def dotfilter(self, view):
        dot = view.substr(sublime.Region(view.sel()[0].a - 1,
                                         view.sel()[0].b))
        is_dot = ord(dot[0]) == 46
        return is_dot

    def filter(self, view, prefix, locations, completions):
        if self.dotfilter(view):
            completions_list_filter = []
            wordstart = view.word(
                sublime.Region(view.sel()[0].a - 1, view.sel()[0].b)).a
            prefix = view.substr(sublime.Region(wordstart, view.sel()[0].b))
            for c in completions:
                try:
                    if len(prefix) > 0:
                        if prefix.lower() in c[0].lower()[0:len(prefix)]:
                            completions_list_filter.append((c[0], c[1]))
                except UnicodeDecodeError:
                    continue
            return completions_list_filter


class FilterManager(object):
    """Store multiple filter for usage from outside."""

    filters = []

    def add_filter(self, cfilter, index=None):
        if index is None:
            self.filters.append(cfilter)
        else:
            self.filters.insert(index, cfilter)

    def apply_filters(self, view, prefix, locations, completions):
        for f in self.filters:
            filtered = f.filter(view, prefix, locations, completions)
            if filtered is not None:
                completions = filtered
        return completions

manager = FilterManager()
manager.add_filter(DotFilter())
