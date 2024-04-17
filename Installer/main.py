import os
import zipfile
import winreg
import sys

def get_registry_subkeys(key_path):
    """Retrieves a list of subkeys within a specified registry key path."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            subkey_count = winreg.QueryInfoKey(key)[0]  # Number of subkeys
            subkeys = []
            for i in range(subkey_count):
                subkeys.append(winreg.EnumKey(key, i))

            return subkeys
    except FileNotFoundError:
        print(f"Registry key '{key_path}' not found.")
        return None

def get_reg_value(key_path:str, value_name:str):
    """Extracts value from the registry."""

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            executable_path, _ = winreg.QueryValueEx(key, value_name)
            return executable_path
    except FileNotFoundError:
        print("Registry key or value not found.")
        return None

def extract_zip(zip_path, destination_path):
    """Extracts zip to the directory."""
    
    print("From:",zip_path)
    print("To",destination_path)
    print("Extracting...")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path) 
    
    print("IDLElib extracted successfully!")

def get_zip_path():

    if getattr(sys, 'frozen', False):  # Check if running as a frozen executable
        data_dir = sys._MEIPASS
    else:
        data_dir = os.path.dirname(__file__)  # Use current directory when running normally
    return os.path.join(data_dir,'idlelib.zip')
if __name__ == "__main__":
    key_path = r"Software\Python\PythonCore"
    print("Looking for python installation...")
    subkeys = get_registry_subkeys(key_path)

    if subkeys:
        subkeys.sort(reverse=True)
        print("Found",subkeys)
        
        key_path+='\\' + subkeys[0]
        key_path+='\\Idle'
        print("Getting value of",key_path)
        
        idle_path = os.path.dirname(get_reg_value(key_path,''))
        
        idlelib_zip_path = get_zip_path()
        
        extract_zip(idlelib_zip_path, idle_path)

    else:
        print("No python installation found or an error occurred.")
        print("Extracting idlelib to current directory...")
        try:
            os.mkdir('idlelib')
            
            idlelib_zip_path = get_zip_path()
            
            extract_zip(idlelib_zip_path, 'idlelib')
        except Exception as e:
            print(e.with_traceback())
os.system('pause')