import ctypes

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


class GuessStringType(object):
    """
    Decorator that guesses the correct version (A or W) to call
    based on the types of the strings passed as parameters.

    Calls the B{ANSI} version if the only string types are ANSI.

    Calls the B{Unicode} version if Unicode or mixed string types are passed.

    The default if no string arguments are passed depends on the value of the
    L{t_default} class variable.

    @type fn_ansi: function
    @ivar fn_ansi: ANSI version of the API function to call.
    @type fn_unicode: function
    @ivar fn_unicode: Unicode (wide) version of the API function to call.

    @type t_default: type
    @cvar t_default: Default string type to use.
        Possible values are:
         - type('') for ANSI
         - type(u'') for Unicode
    """

    # ANSI and Unicode types
    t_ansi = type('')
    t_unicode = type(u'')

    # Default is ANSI for Python 2.x
    t_default = t_ansi

    def __init__(self, fn_ansi, fn_unicode):
        """
        @type  fn_ansi: function
        @param fn_ansi: ANSI version of the API function to call.
        @type  fn_unicode: function
        @param fn_unicode: Unicode (wide) version of the API function to call.
        """
        self.fn_ansi = fn_ansi
        self.fn_unicode = fn_unicode

        # Copy the wrapped function attributes.
        try:
            self.__name__ = self.fn_ansi.__name__[:-1]  # remove the A or W
        except AttributeError:
            pass
        try:
            self.__module__ = self.fn_ansi.__module__
        except AttributeError:
            pass
        try:
            self.__doc__ = self.fn_ansi.__doc__
        except AttributeError:
            pass

    def __call__(self, *argv, **argd):

        # Shortcut to self.t_ansi
        t_ansi = self.t_ansi

        # Get the types of all arguments for the function
        v_types = [type(item) for item in argv]
        v_types.extend([type(value) for (key, value) in argd.items()])

        # Get the appropriate function for the default type
        if self.t_default == t_ansi:
            fn = self.fn_ansi
        else:
            fn = self.fn_unicode

        # If at least one argument is a Unicode string...
        if self.t_unicode in v_types:

            # If al least one argument is an ANSI string,
            # convert all ANSI strings to Unicode
            if t_ansi in v_types:
                argv = list(argv)
                for index in range(len(argv)):
                    if v_types[index] == t_ansi:
                        argv[index] = (argv[index])
                for (key, value) in argd.items():
                    if type(value) == t_ansi:
                        argd[key] = (value)

            # Use the W version
            fn = self.fn_unicode

        # If at least one argument is an ANSI string,
        # but there are no Unicode strings...
        elif t_ansi in v_types:

            # Use the A version
            fn = self.fn_ansi

        # Call the function and return the result
        return fn(*argv, **argd)


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


# int WINAPI GetWindowText(
#   __in   HWND hWnd,
#   __out  LPTSTR lpString,
#   __in   int nMaxCount
# );
def GetWindowTextA(hWnd):
    _GetWindowTextA = windll.user32.GetWindowTextA
    _GetWindowTextA.argtypes = [HWND, LPSTR, ctypes.c_int]
    _GetWindowTextA.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(CHAR)
    while 1:
        lpString = ctypes.create_string_buffer(nMaxCount)
        nCount = _GetWindowTextA(hWnd, lpString, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return str(lpString.value)


def GetWindowTextW(hWnd):
    _GetWindowTextW = windll.user32.GetWindowTextW
    _GetWindowTextW.argtypes = [HWND, LPWSTR, ctypes.c_int]
    _GetWindowTextW.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(CHAR)
    while 1:
        lpString = ctypes.create_string_buffer(nMaxCount)
        nCount = _GetWindowTextW(hWnd, lpString, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return str(lpString.value)

GetWindowText = GuessStringType(GetWindowTextA, GetWindowTextW)


# int GetClassName(
#     HWND hWnd,
#     LPTSTR lpClassName,
#     int nMaxCount
# );
def GetClassNameA(hWnd):
    _GetClassNameA = windll.user32.GetClassNameA
    _GetClassNameA.argtypes = [HWND, LPSTR, ctypes.c_int]
    _GetClassNameA.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(CHAR)
    while 1:
        lpClassName = ctypes.create_string_buffer(nMaxCount)
        nCount = _GetClassNameA(hWnd, lpClassName, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return str(lpClassName.value)


def GetClassNameW(hWnd):
    _GetClassNameW = windll.user32.GetClassNameW
    _GetClassNameW.argtypes = [HWND, LPWSTR, ctypes.c_int]
    _GetClassNameW.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(WCHAR)
    while 1:
        lpClassName = ctypes.create_unicode_buffer(nMaxCount)
        nCount = _GetClassNameW(hWnd, lpClassName, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return str(lpClassName.value)

GetClassName = GuessStringType(GetClassNameA, GetClassNameW)


# BOOL WINAPI SetWindowText(
#   __in      HWND hWnd,
#   __in_opt  LPCTSTR lpString
# );
def SetWindowTextA(hWnd, lpString = None):
    _SetWindowTextA = windll.user32.SetWindowTextA
    _SetWindowTextA.argtypes = [HWND, LPSTR]
    _SetWindowTextA.restype  = bool
    _SetWindowTextA.errcheck = RaiseIfZero
    _SetWindowTextA(hWnd, lpString)


def SetWindowTextW(hWnd, lpString = None):
    _SetWindowTextW = windll.user32.SetWindowTextW
    _SetWindowTextW.argtypes = [HWND, LPWSTR]
    _SetWindowTextW.restype  = bool
    _SetWindowTextW.errcheck = RaiseIfZero
    _SetWindowTextW(hWnd, lpString)

SetWindowText = GuessStringType(SetWindowTextA, SetWindowTextW)


# LRESULT SendMessage(
#     HWND hWnd,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def SendMessageA(hWnd, Msg, wParam = 0, lParam = 0):
    _SendMessageA = windll.user32.SendMessageA
    _SendMessageA.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendMessageA.restype  = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendMessageA(hWnd, Msg, wParam, lParam)

def SendMessageW(hWnd, Msg, wParam = 0, lParam = 0):
    _SendMessageW = windll.user32.SendMessageW
    _SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendMessageW.restype  = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendMessageW(hWnd, Msg, wParam, lParam)

SendMessage = GuessStringType(SendMessageA, SendMessageW)


def FindWindowA(lpClassName=None, lpWindowName=None):
    _FindWindowA = windll.user32.FindWindowA
    _FindWindowA.argtypes = [LPSTR, LPSTR]
    _FindWindowA.restype = HWND

    hWnd = _FindWindowA(lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd



def FindWindowW(lpClassName=None, lpWindowName=None):
    _FindWindowW = windll.user32.FindWindowW
    _FindWindowW.argtypes = [LPWSTR, LPWSTR]
    _FindWindowW.restype  = HWND

    hWnd = _FindWindowW(lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd

FindWindow = GuessStringType(FindWindowA, FindWindowW)


class Window(object):
    def __init__(self, hWnd):
        self.hWnd = hWnd

    def get_handle(self):
        if self.hWnd is None:
            raise ValueError("No window handle set!")
        return self.hWnd

    def get_classname(self):
        return GetClassName(self.get_handle())

    def get_text(self):
        try:
            return GetWindowText(self.get_handle())
        except WindowsError:
            return None

    def find_child(self, text=None, cls=None):
        childs = [Window(w) for w in EnumChildWindows(self.get_handle())]
        for w in childs:
            wndText = w.get_text()
            wndCls = w.get_classname()
            #print(wndText)
            #print(wndCls)
            if text is None and cls is None:
                return None
            if text is None and cls in wndCls:
                return w
            if cls is None and text in wndText:
                return w
            if cls in wndCls and text is None:
                return w
        return None

    def send(self, uMsg, wParam=None, lParam=None, dwTimeout=None):
        """
        Send a low-level window message syncronically.

        @type  uMsg: int
        @param uMsg: Message code.

        @param wParam:
            The type and meaning of this parameter depends on the message.

        @param lParam:
            The type and meaning of this parameter depends on the message.

        @param dwTimeout: Optional timeout for the operation.
            Use C{None} to wait indefinitely.

        @rtype:  int
        @return: The meaning of the return value depends on the window message.
            Typically a value of C{0} means an error occured. You can get the
            error code by calling L{win32.GetLastError}.
        """
        #print(uMsg)
        #print(wParam)
        #print(lParam)
        return SendMessage(self.get_handle(), uMsg, wParam, lParam)

    @staticmethod
    def find_window(text):
        for w in [Window(h) for h in EnumWindows()]:
            window_text = w.get_text()
            if window_text is not None and text in window_text:
                return w
        return None
