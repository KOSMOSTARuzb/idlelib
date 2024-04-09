import tkinter, tkinter.messagebox
from pynput.keyboard import Key, Listener
import socket
import threading
import pymsgbox
import time
import kosmostar_values
import networkin

HOST = None
PORT = kosmostar_values.port
scan_found = None
uploading = None
downloading = None
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
is_connected = False
is_connecting = False
disable_next_popup = False
number_of_chars = 3
class KeyListner:
    def __init__(self):
        self.listener = Listener(on_press = self.onpress)
        self.key = None
        self.got = 0
        self.listener.start()
    def onpress(self,key):
        if self.got==0:
            self.key = str(key)
        elif self.got==number_of_chars:
            self.key += str(key)
            self.listener.stop()
            return 0
        else:
            self.key += str(key)
        self.got+=1

def get_next_key()->str:
    KL = KeyListner()
    while KL.got < number_of_chars:
        time.sleep(0.1)
    time.sleep(0.1)
    return str(KL.key)

def show_error(e:str):
    global disable_next_popup
    if disable_next_popup:
        disable_next_popup = False
        return None
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
    global is_connected, HOST, is_connecting
    if is_connecting:
        show_error("Stand by,\n\nLaunching Python Interpreter...")
        return False
    else:
        is_connecting = True
    try:
        if HOST == None:
            HOST = networkin.scan_network(PORT)
        s.connect((HOST, PORT))
        is_connected=True
        is_connecting=False
        return True
    except ConnectionRefusedError:
        show_error("Unable to launch Python IDE.")
    except Exception as e:
        show_error("Unable to launch Python IDE.\n\n"+str(e))
    is_connecting = False
    return False
def uploader(slot:str, content):
    global uploading
    if slot == 'f7':
        return None
    if not is_connected:
        if not get_connected():
            show_error('Not launched, try restarting the app...')
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
            show_error('Not launched, try restarting the app...')
        return None
    content = 'recv:' + slot
    s.sendall(content.encode('utf-8'))
    print('requested, waiting...')
    content = s.recv(kosmostar_values.max_bytes_to_transfer).decode('utf-8')
    print('received')
    if content == kosmostar_values.null:
        print('Nothing')
        return None
    return content
def download()->str|None:
    print("download command")
    global downloading
    slot = get_next_key()
    return downloader(slot)
def comment_code(org:str)->str:
    lines = org.strip().splitlines()
    new = ""
    for i in lines:
        if i.strip():
            new = new + '\n# ' + i
    return new
if __name__ == '__main__':
    try:
        import idlelib.pyshell
    except ImportError:
        print(3)
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
