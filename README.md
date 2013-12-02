Using Sublime for MAXScript Development
================

**Sends MAXScript files or selected lines to 3ds Max.**

Benefit from Sublime as an editor without having to enter 3ds Max everytime you want to evaluate some code. Best used on a split- or two-monitor setup. The plugin works by iterating all opened windows and searching for "Autodesk 3ds Max" to find the MAXScript Listener handle, that then gets pasted the code or import command.

**Huge thanks to [Johannes](http://alfastuff.wordpress.com "Johannes") for figuring out all the
complicated stuff! Check out his tools and scripts on his website!**

I also added the MAXScript syntax coloring file from [Rogier van Etten](http://www.linkedin.com/in/frambooz "Rogier van Etten").

How to install using Sublime Package Control
------------------
If you don't have Package Control installed, get it here: [Package Control](https://sublime.wbond.net/installation#st2 "https://sublime.wbond.net/installation#st2")

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
There are two available commands: **send_file_to_max** and **send_selection_to_max**.
Sending files will check if they are valid maxscript files (*.ms, *.mcr).

The following keys should be added automatically after package installation.
To change them, edit your **Key Bindings - User** file and bind to any key you like (I mimic the MAXScript Listener keys here):

```{ "keys": ["ctrl+e"], "command": "send_file_to_max" }```

```{ "keys": ["shift+enter"], "command": "send_selection_to_max"}```

Hope you like it.



Author: [www.cbuelter.de](http://www.cbuelter.de "www.cbuelter.de")
