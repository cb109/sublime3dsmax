Sublime 3ds Max
===============

**Sends MAXScript/Python files or selected lines to 3ds Max.**

![](https://media.giphy.com/media/l4FGyySBwndeeloic/giphy.gif)

Benefit from Sublime as an editor without having to enter 3ds Max everytime you want to evaluate some code. Best used on a split- or two-monitor setup.

The plugin works by iterating all opened windows and searching for *Autodesk 3ds Max* to find the MAXScript Listener handle, that then gets pasted the code or import command. 3ds Max is found and communicated with automatically. You can choose which one to talk to if there are multiple running instances of 3ds Max.

A lot of people have contributed their work to make this tool better, I want to thank all contributors and encourage you to check out their websites at the bottom of this page!


How to install using Sublime Package Control
------------------
If you don't have Package Control installed, get it here: [Package Control](https://sublime.wbond.net/installation#st2)

1. In Sublime start *Package Control -> Install Package*
2. Search for **Send to 3ds Max** and hit Enter to install


How to install manually
------------------
1. Download the repository
2. In Sublime Text go to *Preferences -> Browse Packages*
3. Create a folder named *Send to 3ds Max*
4. Extract the contents to the folder
5. Restart Sublime


How to setup in Sublime
------------------
There are four available commands:

* **send_file_to_max**: Execute the current file. Allowed file types are: \*.ms, \*.mcr, \*.py
* **send_selection_to_max**: Execute the current selection. No selection will execute the line where the cursor is. Selecting something on a single line will execute exactly that selection, so it is possible to select small snippets. Selecting something over multiple lines will execute these full lines for quickly executing certain blocks of code.
* **select_max_instance**: If you have multiple instances running, this command lets you choose which one to communicate with. Your choice is remembered until Sublime is closed.
* **open_max_help**: Open the MAXScript online documentation and search for your currently selected text.

Note: You must work with actual files that have been saved to disk, so that it can detect whether you are working with MAXScript or Python code by looking at the file extension.

To set shortcuts for the commands, edit your **Key Bindings - User** file and bind to any key you like (I mimic the MAXScript Listener keys here):
```
{ "keys": ["ctrl+e"], "command": "send_file_to_max" },
{ "keys": ["shift+enter"], "command": "send_selection_to_max"},
{ "keys": ["ctrl+shift+e"], "command": "select_max_instance" },
{ "keys": ["f1"], "command" : "open_max_help"}
```

Hope you like it!


Contributing
------------

If you want to contribute, please fork this repository, add your changes and submit a pull request for the ``develop`` branch. Please try to adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/) and remember: commit early, commit often and use meaningful commit messages. Thanks :)

Original authors:
* [Christoph Bülter](http://www.cbuelter.de)
* [Johannes Becker](http://alfastuff.wordpress.com)

Contributors:
* [Christian Deiß](http://de.linkedin.com/pub/christian-dei%C3%9F/2a/915/ba5)
* [Daniel Santana](http://github.com/dgsantana)
* [Ettore Pancini](http://bitbucket.org/epancini)
* [Rogier van Etten](http://twitter.com/captainkeytar)
* [Luca Faggion](https://github.com/darkimage)
* [Johan Boekhoven](https://www.linkedin.com/in/johanboekhoven)
