## **IDLEB** – Python IDLE edition with backup feature

> This is just two buttons:

[![Preview of IDLEB][preview_image]][preview_image_url]


# The funtional changes
Two options added to the `Run` menu:
Save & Run...
Restore & Run...

# Save functionality
When clicked, waits for a key press(e.g. g) and sends the current file contents to host computer.
The host computer saves the file.

# Restore functionality
When clicked, waits for a key press(e.g. g) and sends request to host computer.
The host computer sends the file back.
IDE commant current code and inserts received code after it.

# Error codes
`Stand by, Launching Python Interpreter...` - Connection in progress...

`Unable to launch Python IDE.` - No servers found<sub>when errorcode is not given</sub>
Connection error<sub>with errorcode</sub>

`Error: Unknown\nFile does not exist.` - No code is available in the server with this name.<sub>(when restoring)</sub>

`Not launched.` - Not connected(`try restarting`).

`Work in progress` - Upload/Restore progress running in the background.

## Install instructions
Just copy the contents into your `%localappdata%\Programs\Python\Python311\Lib\idlelib` <sub>(in windows only)</sub>

[//]: # (LINKS)
[preview_image]: https://github.com/KOSMOSTARuzb/idlelib/blob/main/screenshots/menubar.png "Preview of IDLEB"
[preview_image_url]: https://github.com/KOSMOSTARuzb/idlelib/blob/main/screenshots/menubar.png
