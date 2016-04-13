"""Constants used across modules."""

import os


# The 3ds Max 2014 help (==16) seems the last one to allow for readable
# query parameters to be added. For versions above, the docs seem to be
# generated dynamically and using very human-unfriendly urls.
ONLINE_MAXSCRIPT_HELP_URL = (
    r"http://docs.autodesk.com/3DSMAX/16/ENU/MAXScript-Help/index.html")

APIPATH = os.path.dirname(os.path.realpath(__file__)) + "\maxscript.api"

# Create the tempfile in "Packages" (ST2) / "Installed Packages" (ST3).
TEMPFILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "Send_to_3ds_Max_Temp.ms")

TITLE_IDENTIFIER = "Autodesk 3ds Max"
PREFIX = "Sublime3dsMax:"
NO_MXS_FILE = PREFIX + " File is not a MAXScript file (*.ms, *.mcr)"
NO_TEMP = PREFIX + " Could not write to temp file"
NOT_SAVED = PREFIX + " File must be saved before sending to 3ds Max"
MAX_NOT_FOUND = PREFIX + " Could not find a 3ds max instance."
RECORDER_NOT_FOUND = PREFIX + " Could not find MAXScript Macro Recorder"
NO_FILE = PREFIX + " No file currently open"

PYTHON_COMMAND_TEMPLATE = """
try
    python.executefile (@"{filepath}")\r\n
catch
    python.run (@"{filepath}")\r\n
"""
