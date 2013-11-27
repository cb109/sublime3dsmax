############################################################################
#
#   This module finds 3ds Max and the MAXScript Listener and can
#   send strings and button strokes to it.
#
#   Completely based on m2u: http://alfastuff.wordpress.com/2013/10/13/m2u/
#   and figured out by the amazing Johannes: http://alfastuff.wordpress.com/
#
#   Known issues: EnumPos for childwindows changes,
#   e.g. if using create mode or hierarchy mode.
#   Current workaround is to use the first handle
#   that matches cls="MXS_Scintilla", which is the
#   mini macro recorder, to paste text into.
#
############################################################################

# keeps all the required UI elements of the Max and talks to them
import ctypes #required for windows ui stuff
import threading

MAX_TITLE_IDENTIFIER = r"Autodesk 3ds Max"

# UI element window handles
gMaxThreadProcessID = None
gMainWindow = None
gMiniMacroRecorder = None

# windows functions and constants
# stuff for finding and analyzing UI Elements
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
FindWindowEx = ctypes.windll.user32.FindWindowExW

GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindow = ctypes.windll.user32.GetWindow
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA

WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102 # the alternative to WM_KEYDOWN
VK_RETURN  = 0x0D # Enter key

# attaching is required for SendMessage and the like to actually work like it should
AttachThreadInput = ctypes.windll.user32.AttachThreadInput

class ThreadWinLParm(ctypes.Structure):
    """lParam object to get a name to and an object back from a windows
    enumerator function.

    .. seealso:: :func:`_getChildWindowByName`
    """
    _fields_=[
        ("name", ctypes.c_wchar_p),
        ("cls", ctypes.c_wchar_p),
        ("hwnd", ctypes.POINTER(ctypes.c_long)),
        ("enumPos", ctypes.c_int),
        ("_enum", ctypes.c_int) # keep track of current enum step
    ]

def _getChildWindowByName(hwnd, lParam):
    """callback function to be called by EnumChildWindows, see
    :func:`getChildWindowByName`

    :param hwnd: the window handle
    :param lParam: a :ref:`ctypes.byref` instance of :class:`ThreadWinLParam`

    if name is None, the cls name is taken,
    if cls is None, the name is taken,
    if both are None, all elements are printed
    if both have values, only the element matching both will fit

    """
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    param._enum += 1

    length = 255
    cbuff = ctypes.create_unicode_buffer(length + 1)
    GetClassName(hwnd, cbuff, length+1)
    if param.name == None and param.cls != None:
        #print "no name, but cls"
        if param.cls in cbuff.value:# == param.cls:
            param.hwnd = hwnd
            return False
    elif param.cls == None and param.name != None:
        #print "no cls, but name"
        if buff.value == param.name:
            param.hwnd = hwnd
            return False
    elif param.cls != None and param.name != None:
        #print "cls and name"
        if buff.value == param.name and param.cls in cbuff.value:# == param.cls:
            param.hwnd = hwnd
            return False
    else: #both values are None, print the current element
        print "wnd cls: "+cbuff.value+" name: "+buff.value+" enum: "+str(param._enum)
    return True

def getChildWindowByName(hwnd, name = None, cls = None):
    """find a window by its name or clsName, returns the window's hwnd

    :param hwnd: the parent window's hwnd
    :param name: the name/title to search for
    :param cls: the clsName to search for

    :return: the hwnd of the matching child window

    if name is None, the cls name is taken,
    if cls is None, the name is taken,
    if both are None, all elements are printed
    if both have values, only the element matching both will fit.

    .. seealso:: :func:`_getChildWindowByName`, :func:`getChildWindowByEnumPos`

    """
    param = ThreadWinLParm(name=name,cls=cls,_enum=-1)
    lParam = ctypes.byref(param)
    EnumChildWindows(hwnd, EnumWindowsProc(_getChildWindowByName),lParam)
    print param._enum
    return param.hwnd

def getMXSMiniMacroRecorder():
    """convenience function
    """
    # The function will return the first param that matches the class name.
    # Thankfully, this is the MAXScript Mini Listener.
    global gMainWindow
    miniMacroRecorderHandle = getChildWindowByName(gMainWindow, name=None, cls="MXS_Scintilla")
    return miniMacroRecorderHandle

def _getChildWindowByEnumPos(hwnd, lParam):
    """ callback function, see :func:`getChildWindowByEnumPos` """
    param = ctypes.cast(lParam, ctypes.POINTER(ThreadWinLParm)).contents
    param._enum += 1
    if param._enum == param.enumPos:
        param.hwnd = hwnd
        return False
    return True

def getChildWindowByEnumPos(hwnd, pos):
    """get a child window by its enum pos, return its hwnd

    :param hwnd: the parent window's hwnd
    :param pos: the number to search for

    :return: the hwnd of the matching child window

    This function uses the creation order which is reflected in Windows Enumerate
    functions to get the handle to a certain window. This is useful when the
    name or cls of the desired window is not unique or not given.

    You can count the enum pos by printing all child windows of a window.
    .. seealso:: :func:`getChildWindowByName`

    """
    param = ThreadWinLParm(name = None, cls = None, enumPos = pos, _enum = -1)
    EnumChildWindows( hwnd, EnumWindowsProc(_getChildWindowByEnumPos), ctypes.byref(param))
    return param.hwnd

def attachThreads(hwnd):
    """tell Windows to attach the program and the max threads.

    This will give us some benefits in control, for example SendMessage calls to
    the max thread will only return when Max has processed the message, amazing!

    """
    thread = GetWindowThreadProcessId(hwnd, 0) #max thread
    global gMaxThreadProcessID
    gMaxThreadProcessID = thread
    thisThread = threading.current_thread().ident #program thread
    AttachThreadInput(thread, thisThread, True)

def _getWindows(hwnd, lParam):
    """callback function, find the Max Window (and fill the ui element vars)

    This is a callback function. Windows itself will call this function for
    every top-level window in EnumWindows iterator function.
    .. seealso:: :func:`connectToMax`
    """
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        global MAX_TITLE_IDENTIFIER
        if MAX_TITLE_IDENTIFIER in buff.value:
            global gMainWindow, gMaxThreadProcessID
            gMainWindow = hwnd
            attachThreads(gMainWindow)

            # Find MAXScript Mini Listener
            global gMiniMacroRecorder
            gMiniMacroRecorder = getMXSMiniMacroRecorder()
            return False
    return True

def connectToMax():
    global gMainWindow
    EnumWindows(EnumWindowsProc(_getWindows), 0)
    return (gMainWindow is not None)

def fireCommand(command):
    """Executes the command string in Max.
    ';' at end needed for ReturnKey to be accepted."""
    global gMiniMacroRecorder
    SendMessage(gMiniMacroRecorder, WM_SETTEXT, 0, str(command) )
    SendMessage(gMiniMacroRecorder, WM_CHAR, VK_RETURN, 0)

