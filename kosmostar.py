
import tkinter, tkinter.messagebox
from pynput.keyboard import Key, Listener
import socket
import threading
import pymsgbox
import time
import idlelib.kosmostar_values
import netifaces

HOST = None
PORT = idlelib.kosmostar_values.port
scan_found = None
max_threads = 50
uploading = None
downloading = None
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
is_connected = False
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
def get_ip()->list[tuple[str,str,str]]:#interface, ip, subnet mask
    j = []
    interfaces = netifaces.interfaces()

    # Iterate through interfaces
    for interface in interfaces:
        # Check if the interface has IPv4 addresses
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            ipv4_addresses = netifaces.ifaddresses(interface)[netifaces.AF_INET]

            for address_info in ipv4_addresses:
                if address_info['addr']!='127.0.0.1' and not ':' in address_info['addr']:
                    j.append((interface,address_info['addr'],address_info['netmask']))
    return j
def get_ip_range()->list[tuple[int,int]]:# ip start, ip finish
    ips = get_ip()
    j=[]
    for i in ips:
        ip_parts=i[1].split('.')
        mask_parts=i[2].split('.')
        j1s = 0
        j2s = 0
        for l in range(4):
            j1 = int(ip_parts[l]) & int(mask_parts[l])
            jt = int(mask_parts[l]) ^ 255
            j2 = jt | int(ip_parts[l])
            j1s =j1s*256 + j1
            j2s =j2s*256 + j2
        j.append((j1s,j2s))
    return j
def to_ip(IP:int)->str:
    ip = str(IP//16777216)
    ip += '.' + str(IP%16777216//65536)
    ip += '.' + str(IP%65536//256)
    ip += '.' + str(IP%256)
    return ip
def scan_ip(IP:int,port:int)->bool:
    global scan_found
    ip = to_ip(IP)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(0.5)
    result = soc.connect_ex((ip,port))
    if result == 0:
        print('Open port found:',ip,':',port)
        scan_found = ip
        soc.close()

    soc.close()
def scan_chunk(start,stop,port):
    global scan_found
    threads = []
    for i in range(start, stop+1):
        if scan_found == None:
            threading.Thread()
            threads.append(threading.Thread(target=lambda: scan_ip(i,port)))
            threads[-1].start()
    alive = True
    while alive:
        alive = False
        for i in threads:
            if i.is_alive():
                alive = True
def scan_network(port:int)->str:#ip address
    global scan_found
    scan_found = None
    ips = get_ip_range()
    print('scanning')

    for ip_start, ip_end in ips:
        for IP in range(ip_start, ip_end+1,max_threads):
            if scan_found==None:
                scan_chunk(IP,min(IP+max_threads,ip_end+1),port)
            else:
                return scan_found
    show_error("No Hosts found on local network")
    global disable_next_popup
    disable_next_popup = True
    return '127.0.0.1'
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
    global is_connected, HOST
    try:
        if HOST == None:
            HOST = scan_network(PORT)
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
