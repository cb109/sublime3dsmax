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
import ctypes  # required for windows ui stuff
import threading


MAX_TITLE_IDENTIFIER = r"Autodesk 3ds Max"

# UI element window handles
gMaxThreadProcessID = None
gMainWindow = None
gMiniMacroRecorder = None

LPVOID = ctypes.c_void_p
CHAR = ctypes.c_char
WCHAR = ctypes.c_wchar
BYTE = ctypes.c_ubyte
SBYTE = ctypes.c_byte
WORD = ctypes.c_uint16
SWORD = ctypes.c_int16
DWORD = ctypes.c_uint32
SDWORD = ctypes.c_int32
QWORD = ctypes.c_uint64
SQWORD = ctypes.c_int64
SHORT = ctypes.c_short
USHORT = ctypes.c_ushort
INT = ctypes.c_int
UINT = ctypes.c_uint
LONG = ctypes.c_long
ULONG = ctypes.c_ulong
LONGLONG = ctypes.c_int64        # c_longlong
ULONGLONG = ctypes.c_uint64       # c_ulonglong
LPSTR = ctypes.c_char_p
LPWSTR = ctypes.c_wchar_p
INT8 = ctypes.c_int8
INT16 = ctypes.c_int16
INT32 = ctypes.c_int32
INT64 = ctypes.c_int64
UINT8 = ctypes.c_uint8
UINT16 = ctypes.c_uint16
UINT32 = ctypes.c_uint32
UINT64 = ctypes.c_uint64
LONG32 = ctypes.c_int32
LONG64 = ctypes.c_int64
ULONG32 = ctypes.c_uint32
ULONG64 = ctypes.c_uint64
DWORD32 = ctypes.c_uint32
DWORD64 = ctypes.c_uint64
BOOL = ctypes.c_int
FLOAT = ctypes.c_float
PVOID = LPVOID
HANDLE = LPVOID
HWND = HANDLE
addressof = ctypes.addressof
sizeof = ctypes.sizeof
SIZEOF = ctypes.sizeof
POINTER = ctypes.POINTER
Structure = ctypes.Structure
Union = ctypes.Union
WINFUNCTYPE = ctypes.WINFUNCTYPE
windll = ctypes.windll
WNDENUMPROC = WINFUNCTYPE(BOOL, HWND, PVOID)
NULL = None
INFINITE = -1
TRUE = 1
FALSE = 0
WPARAM = DWORD
LPARAM = LPVOID
LRESULT = LPVOID
ERROR_SUCCESS = 0
ERROR_NO_MORE_FILES = 18


# DWORD WINAPI GetLastError(void);
def GetLastError():
    _GetLastError = windll.kernel32.GetLastError
    _GetLastError.argtypes = []
    _GetLastError.restype = DWORD
    return _GetLastError()


# void WINAPI SetLastError(
#   __in  DWORD dwErrCode
# );
def SetLastError(dwErrCode):
    _SetLastError = windll.kernel32.SetLastError
    _SetLastError.argtypes = [DWORD]
    _SetLastError.restype = None
    _SetLastError(dwErrCode)


def MAKE_WPARAM(wParam):
    """
    Convert arguments to the WPARAM type.
    Used automatically by SendMessage, PostMessage, etc.
    You shouldn't need to call this function.
    """
    wParam = ctypes.cast(wParam, LPVOID).value
    if wParam is None:
        wParam = 0
    return wParam


def MAKE_LPARAM(lParam):
    """
    Convert arguments to the LPARAM type.
    Used automatically by SendMessage, PostMessage, etc.
    You shouldn't need to call this function.
    """
    return ctypes.cast(lParam, LPARAM)


class __WindowEnumerator (object):
    """
    Window enumerator class. Used internally by the window enumeration APIs.
    """
    def __init__(self):
        self.hwnd = list()

    def __call__(self, hwnd, lParam):
##        print hwnd  # XXX DEBUG
        self.hwnd.append(hwnd)
        return TRUE


class __EnumWndProc (__WindowEnumerator):
    pass


# windows functions and constants
# stuff for finding and analyzing UI Elements
#EnumWindows = ctypes.windll.user32.EnumWindows
def EnumWindows():
    _EnumWindows = windll.user32.EnumWindows
    _EnumWindows.argtypes = [WNDENUMPROC, LPARAM]
    _EnumWindows.restype = bool

    EnumFunc = __EnumWndProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    if not _EnumWindows(lpEnumFunc, NULL):
        errcode = GetLastError()
        if errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
            raise ctypes.WinError(errcode)
    return EnumFunc.hwnd


# BOOL CALLBACK EnumChildProc(
#     HWND hwnd,
#     LPARAM lParam
# );
class __EnumChildProc (__WindowEnumerator):
    pass


# BOOL EnumChildWindows(
#     HWND hWndParent,
#     WNDENUMPROC lpEnumFunc,
#     LPARAM lParam
# );
def EnumChildWindows(hWndParent=NULL):
    _EnumChildWindows = windll.user32.EnumChildWindows
    _EnumChildWindows.argtypes = [HWND, WNDENUMPROC, LPARAM]
    _EnumChildWindows.restype = bool

    EnumFunc = __EnumChildProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    SetLastError(ERROR_SUCCESS)
    _EnumChildWindows(hWndParent, lpEnumFunc, NULL)
    errcode = GetLastError()
    if errcode != ERROR_SUCCESS and errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
        raise ctypes.WinError(errcode)
    return EnumFunc.hwnd


def FindWindowW(lpClassName=None, lpWindowName=None):
    _FindWindowW = windll.user32.FindWindowW
    _FindWindowW.argtypes = [LPWSTR, LPWSTR]
    _FindWindowW.restype = HWND

    hWnd = _FindWindowW(lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd


def GetWindowTextW(hWnd):
    _GetWindowTextW = windll.user32.GetWindowTextW
    _GetWindowTextW.argtypes = [HWND, LPWSTR, ctypes.c_int]
    _GetWindowTextW.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(CHAR)
    while 1:
        lpString = ctypes.create_string_buffer("", nMaxCount)
        nCount = _GetWindowTextW(hWnd, lpString, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return lpString.value


def SetWindowTextW(hWnd, lpString=None):
    _SetWindowTextW = windll.user32.SetWindowTextW
    _SetWindowTextW.argtypes = [HWND, LPWSTR]
    _SetWindowTextW.restype = bool
    _SetWindowTextW.errcheck = RaiseIfZero
    _SetWindowTextW(hWnd, lpString)


def SendMessageW(hWnd, Msg, wParam=0, lParam=0):
    _SendMessageW = windll.user32.SendMessageW
    _SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendMessageW.restype = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendMessageW(hWnd, Msg, wParam, lParam)


class Window(object):
    def __init__(hwnd):
        pass

#EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
#EnumChildWindows = ctypes.windll.user32.EnumChildWindows
FindWindowEx = ctypes.windll.user32.FindWindowExW

GetClassName = ctypes.windll.user32.GetClassNameW
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindow = ctypes.windll.user32.GetWindow
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

PostMessage = ctypes.windll.user32.PostMessageA
SendMessage = ctypes.windll.user32.SendMessageA

WM_SETTEXT = 0x0C
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x102  # the alternative to WM_KEYDOWN
VK_RETURN = 0x0D  # Enter key

# attaching is required for SendMessage and the like to actually work like it should
AttachThreadInput = ctypes.windll.user32.AttachThreadInput


class ThreadWinLParm(ctypes.Structure):
    """lParam object to get a name to and an object back from a windows
    enumerator function.

    .. seealso:: :func:`_getChildWindowByName`
    """
    _fields_ = [
        ("name", ctypes.c_wchar_p),
        ("cls", ctypes.c_wchar_p),
        ("hwnd", ctypes.POINTER(ctypes.c_long)),
        ("enumPos", ctypes.c_int),
        ("_enum", ctypes.c_int)  # keep track of current enum step
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
    if param.name is None and param.cls is not None:
        if param.cls in cbuff.value:  # == param.cls:
            param.hwnd = hwnd
            return False
    elif param.cls is None and param.name is not None:
        if buff.value == param.name:
            param.hwnd = hwnd
            return False
    elif param.cls is not None and param.name is not None:
        if buff.value == param.name and param.cls in cbuff.value:  # == param.cls:
            param.hwnd = hwnd
            return False
    else:  # both values are None, print the current element
        print ("wnd cls: "+cbuff.value+" name: "+buff.value+" enum: "+str(param._enum))
    return True


def getChildWindowByName(hwnd, name=None, cls=None):
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
    param = ThreadWinLParm(name=name, cls=cls, _enum=-1)
    lParam = ctypes.byref(param)
    EnumChildWindows(hwnd, EnumWindowsProc(_getChildWindowByName), lParam)
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
    param = ThreadWinLParm(name=None, cls=None, enumPos=pos, _enum=-1)
    EnumChildWindows(hwnd, EnumWindowsProc(_getChildWindowByEnumPos), ctypes.byref(param))
    return param.hwnd


def attachThreads(hwnd):
    """tell Windows to attach the program and the max threads.

    This will give us some benefits in control, for example SendMessage calls to
    the max thread will only return when Max has processed the message, amazing!

    """
    thread = GetWindowThreadProcessId(hwnd, 0)  # max thread
    global gMaxThreadProcessID
    gMaxThreadProcessID = thread
    thisThread = threading.current_thread().ident  # program thread
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
            #attachThreads(gMainWindow)

            # Find MAXScript Mini Listener
            global gMiniMacroRecorder
            gMiniMacroRecorder = getMXSMiniMacroRecorder()
            return False
    return True


def connectToMax():
#    global gMainWindow
#    global gMiniMacroRecorder
#    gMainWindow = system.System.find_window(None, MAX_TITLE_IDENTIFIER)
#    if gMainWindow is not None:
#        for w in gMainWindow.get_children():
#            if w.get_classname() in 'MXS_Scintilla':
#                gMiniMacroRecorder = w
#                break
#    return (gMainWindow is not None)
    global gMainWindow
    for w in EnumWindows():
        if 
    #EnumWindows(EnumWindowsProc(_getWindows), 0)
    return (gMainWindow is not None)


def fireCommand(command):
    """Executes the command string in Max.
    ';' at end needed for ReturnKey to be accepted."""
    global gMiniMacroRecorder
    #gMiniMacroRecorder.send(win32.WM_SETTEXT, str(command))
    SendMessageW(gMiniMacroRecorder, WM_SETTEXT, 0, command)
    SendMessageW(gMiniMacroRecorder, WM_CHAR, VK_RETURN, 0)
