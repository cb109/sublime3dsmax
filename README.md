Using Sublime for MAXScript Development
===================================

**Sends MAXScript files or selected lines to the 3ds Max Listener.**

Benefit from Sublime as an editor without having to enter 3ds Max everytime
you want to evaluate some code. Best used on a split- or two-monitor setup. 

The plugin works by iterating all opened windows and searching for "Autodesk 3ds Max" to find
the MAXScript Listener handle, that then gets pasted the code or import command.



Huge thanks to [Johannes](http://alfastuff.wordpress.com "Johannes") for figuring out all the
complicated stuff!


How to install using Sublime Package Control
-----------------------------------
*(If you don't have Package Control installed, get it here: https://sublime.wbond.net/installation#st2)*

1. In Sublime start *Package Control -> Install Package*
2. Search for *Sublime3dsMax* and hit Enter to install

How to install manually
----------------------------------
1. Download the repository
2. In Sublime Text 2 or 3, go to *Preferences -> Browse Packages*
3. Create a folder named *Sublime3dsMax*
4. Extract the contents to the folder
5. Restart Sublime

How to setup in Sublime
----------------------------------
1. Edit your **Key Bindings - User** file and bind to any key you like (I mimic the MAXScript Listener keys here):

```{ "keys": ["ctrl+e"], "command": "send_file_to_max" },

    { "keys": ["shift+enter"], "command": "send_selection_to_max"}```

Hope you like it.

[Author's website: www.cbuelter.de](http://www.cbuelter.de "Author's website: www.cbuelter.de")