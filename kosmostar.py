
import tkinter, tkinter.messagebox
from pynput.keyboard import Key, Listener
import socket
import threading
import pymsgbox
import sys
import time
import idlelib.kosmostar_values

HOST = idlelib.kosmostar_values.host
PORT = idlelib.kosmostar_values.port
uploading = None
downloading = None
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
is_connected = False
class KeyListner:
    def __init__(self):
        self.listener = Listener(on_press = self.onpress)
        self.key = None
        self.got = False
        self.listener.start()
    def onpress(self,key):
        self.key = key
        self.listener.stop()
        self.got = True
def get_next_key()->str:
    KL = KeyListner()
    while not KL.got:
        time.sleep(0.1)
    time.sleep(0.1)
    return str(KL.key)
def show_error(e:str):
    try:
        tkinter.NoDefaultRoot()
        tkinter.messagebox.showerror('Error', str(e))
    except:
        try:
            pymsgbox.alert(e,'Error')
        except:
            try:
                print(e)
            except:
                pass
def get_connected():
    global is_connected
    try:
        s.connect((HOST, PORT))
        is_connected=True
        return True
    except Exception as e:
        show_error(str(e))
        return False
def uploader(slot:str, content):
    global uploading
    if slot == 'f7':
        return None
    if not is_connected:
        if not get_connected():
            show_error('Not connected, try restarting the app...')
        return False
    content = 'send:' + slot + '\n' + content
    s.sendall(content.encode('utf-8'))
    print('done')
    uploading = None
    return True
def upload(_:str):
    print("upload command")
    global uploading
    slot = get_next_key()
    if uploading == None:
        uploading = threading.Thread(target=lambda: uploader(slot, _))
        uploading.start()
    elif type(uploading)==threading.Thread:
        if not uploading.is_alive():
            uploading = threading.Thread(target=lambda: uploader(slot, _))
            uploading.start()
        else:
            show_error('Work in progress...\nPlease wait before trying again.')
            
    else:
        show_error('Work in progress...\nPlease wait before trying again.')
def downloader(slot:str):
    if slot == 'f8':
        return None
    if not is_connected:
        if not get_connected():
            show_error('Not connected, try restarting the app...')
        return None
    content = 'recv:' + slot
    s.sendall(content.encode('utf-8'))
    print('requested, waiting...')
    content = s.recv(idlelib.kosmostar_values.max_bytes_to_transfer).decode('utf-8')
    print('received')
    if content == idlelib.kosmostar_values.null:
        print('Nothing')
        return None
    return content
def download()->str|None:
    print("download command")
    global downloading
    slot = get_next_key()
    return downloader(slot)
def comment_code(org:str)->str:
    lines = org.splitlines()
    new = ""
    for i in lines:
        new = new + '\n# ' + i
    return new
if __name__ == '__main__':
    try:
        import idlelib.pyshell
    except ImportError:
        from . import pyshell
        import os
        idledir = os.path.dirname(os.path.abspath(pyshell.__file__))
        if idledir != os.getcwd():
            pypath = os.environ.get('PYTHONPATH', '')
            if pypath:
                os.environ['PYTHONPATH'] = pypath + ':' + idledir
            else:
                os.environ['PYTHONPATH'] = idledir
        pyshell.main()
    else:
        idlelib.pyshell.main()
else:
    get_connected()

# while True:
#     message = input("You: ")
#     s.sendall(message.encode('utf-8'))
#     data = s.recv(1024)
#     print('Received:', data.decode('utf-8'))
