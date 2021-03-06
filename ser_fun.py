# -*- coding: utf-8 -*-
"""
ser_fun: 
    Functions related to making serial connections to instruments in the
    Kroll lab.
@author: Amanda Gao
"""
import serial
import time
import sys
import glob
import os

def make_safe_filename(s):
    """
    Makes an inputted filename safe if it isn't already.
    """
    def safe_char(c):
        if c.isalnum() or c in ['.', '-', '_', '\\', ':']:
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")

    
def log_mcpc_data(cnxn, filename):  
    """
    Converts MCPC output from cnxn to tabular format and logs output to a file 
    named filename.
    
    :returns: a 16x2 matrix of variable name and 
    value parameters.
    """
    cnxn.write(b'status\r\n')
    resp = cnxn.read(254).decode('utf-8')
    resp = (resp.strip()).split('\r\n')
    
    # Accounting for the occasional empty string
    if len(resp)<5:
        return
        
    resp = [x.split(' ') for x in resp]
    # Flatten the list
    resp = [item.strip() for sublist in resp for item in sublist]
    # Split on '=' and set attribute to value
    resp = [item.split('=') for item in resp]
    
    # Construct the csv data.
    string=time.strftime('%m/%d/%Y %H:%M:%S')
    for row in resp:
        string=string+','+row[1]
    string+='\n'
    
    file = open(filename,'a')
    file.write(string)
    file.close()
    
    return resp

def find_ports():
    """
    Opens the list of ports that are connected.
        
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
        
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def gen_default_filename():
    """
    :returns: a default filename str in the form mcpc_YYYY-MM-DD_hh_mm.csv
    """
    return 'mcpc_'+time.strftime('%Y-%m-%d_%H-%M.csv')

def is_path_valid(filePath):
    """
    :returns: true if path is valid
              false if path is invalid
    """
    if os.path.exists(filePath):
    #the file is there
        return True
    elif os.access(os.path.dirname(filePath), os.W_OK):
    #the file does not exists but write privileges are given
        return True
    else:
    #can not write there
        return False