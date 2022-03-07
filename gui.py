import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font
import tkinter.ttk as ttk
import types
#import serial.tools.list_ports
#import threading
#import time

#from mcuDevice import *
from enum import Enum

class MT(Enum):
    DATA = 0
    CMD = 1
    RSP = 2
    NTF = 3
    
class GID(Enum):
    Core = 0
    RF = 1
    NFCEE = 2
    Proprietary = 0x0F

#mt_dict = {MT.DATA:'Data Packet',MT.CMD:'Command Msg',MT.RSP:'Response Msg',MT.NTF:'Notification Msg'}
pbf_dict = {0:'Complete',1:'Segment'}
#gid_dict = {0:'Core',1:'RF',2:'NFCEE',15:'Proprietary'}
core_oid_dict = {0:'RESET',1:'INIT',2:'SET_CONFIG',3:'GET_CONFIG',4:'CONN_CREATE',5:'CONN_CLOSE',6:'CONN_CREDITS',7:'GENERIC_ERROR',8:'INTERFACE_ERROR'}
rf_oid_dict = {0:'DISCOVER_MAP',1:'SET_LISTEN_MODE_ROUTING',2:'GET_LISTEN_MODE_ROUTING',3:'DISCOVER',4:'DISCOVER_SELECT',5:'INTF_ACTIVE',6:'DEACTIVATE',7:'FIELD_INFO',8:'T3T_POLLING',9:'NFCEE_ACTION',10:'NFCEE_DISCOVERY_REQ',11:'PARAMETER_UPDATE'}
nfcee_oid_dict = {0:'DISCOVER',1:'MODE_SET'}
reset_type_dict = {0:'Keep Configration',1:'Reset Configration'}
status_dict = {0:'OK',1:'REJECTED',2:'RF_FRAME_CORRUPTED',3:'FAILED',4:'NOT_INITED',5:'SYNTAX_ERROR',6:'SEMANTIC_ERROR',9:'INVALID_PARAM',0x0a:'MSG_SIZE_EXCEEDED',0xa0:'DISCOVERY_STARTED',0xa1:'DISCOVERY_TARGET_ACTIVATION_FAILED',0xa2:'DISCOVERY_TEAR_DOWN',0xb0:'RF_TRANS_ERROR',0xb1:'RF_PROTOCOL_ERROR',0xb2:'RF_TIMEOUT',0XC0:'NFCEE_IF_ACTIVE_FAILED',0XC1:'NFCEE_TRANS_ERROR',0XC2:'NFCEE_PROTOCOL_ERROR',0XC3:'NFCEE_TIMEOUT'}
nci_ver_dict = {0x10:'1.0'}
config_status_dict = {0:'RF Config kept',1:'RF Config rest'}


class Application(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.pktVar = tk.StringVar()
        self.resultVar = tk.StringVar()
        self.grid(sticky=tk.NSEW)
        self.createWidgets()

        self.defaultFont = tkinter.font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="微软雅黑",     size=16)



    def createWidgets(self):
        help_frame = ttk.Frame(self)
        help_frame.grid(row = 0, sticky=tk.NSEW, pady = 3)
        help_frame.InfoLable = ttk.Label(help_frame, text="Input NCI HEX packet:", justify=tk.LEFT)
        help_frame.InfoLable.grid(row=0, sticky=tk.W, padx=10)
        help_frame.pktEntry = ttk.Entry(help_frame, justify=tk.LEFT, textvariable=self.pktVar, width=50)
        help_frame.pktEntry.grid(row=1, sticky=tk.W, padx=10)
        

        actionFrame = ttk.Frame(self)
        actionFrame.grid(row = 1, sticky=tk.NSEW, pady=3)

        self.startBtn = ttk.Button(actionFrame, text="Decode", command=self.startTest)
        self.startBtn.grid(padx=10, row = 0, column = 0)
        self.clearBtn = ttk.Button(actionFrame, text="Clear", command=self.clear)
        self.clearBtn.grid(padx=10, row = 0, column = 1)
        
        resultFrame = ttk.Frame(self)
        resultFrame.grid(row = 2, sticky=tk.NSEW, pady=3)

        resultFrame.resultLable = ttk.Label(resultFrame, justify=tk.LEFT, textvariable=self.resultVar)
        resultFrame.resultLable.grid(row=1, sticky=tk.W, padx=10)
        self.resultLable = resultFrame.resultLable

    def clear(self):
        self.pktVar.set('')
        self.resultVar.set('')

    def startTest(self):
        NCIStr = self.pktVar.get()
        NCIData = bytes.fromhex(NCIStr)
        mt = MT((NCIData[0] & 0x70) >> 5)
        #self.resultVar.set("MT:"+mt_dict[mt]+"\n")
        self.resultVar.set("MT:\t"+mt.name+"\n")
        pbf = (NCIData[0] & 0x10) >> 4
        self.resultVar.set(self.resultVar.get()+"PBF:\t"+pbf_dict[pbf]+"\n")
        if mt == MT.DATA:
            #data
            conn_id = NCIData[0] & 0x0f
            self.resultVar.set(self.resultVar.get()+"Conn ID:\t"+str(conn_id)+"\n")
            
        else:
            #control
            gid = GID(NCIData[0] & 0x0f)
            self.resultVar.set(self.resultVar.get()+"GID:\t"+gid.name+"\n")
            if gid == GID.Core:
                oid_dict = core_oid_dict
            elif gid == GID.RF:
                oid_dict = rf_oid_dict
            elif gid == GID.NFCEE:
                oid_dict = nfcee_oid_dict
            else:
                oid_dict = None
            oid = NCIData[1] & 0x3f
            if oid_dict == None:
                self.resultVar.set(self.resultVar.get()+"OID:\t"+str(oid)+"\n")
            else:
                self.resultVar.set(self.resultVar.get()+"OID:\t"+oid_dict[oid]+"\n")
            
        
        payload_len = NCIData[2]
        self.resultVar.set(self.resultVar.get()+"Payload Len:\t"+str(payload_len)+"\n")
        #payload
        payload_decoded = False
        if gid == GID.Core:
            if oid == 0:
                if mt == MT.CMD:
                    resetType = NCIData[3]
                    self.resultVar.set(self.resultVar.get()+"Reset Type:\t"+reset_type_dict[resetType]+"\n")
                    payload_decoded = True
                elif mt == MT.RSP:
                    status = NCIData[3]
                    version = NCIData[4]
                    cfgStatus = NCIData[5]
                    self.resultVar.set(self.resultVar.get()+"Status:\t"+status_dict[status]+"\n")
                    self.resultVar.set(self.resultVar.get()+"NCI Version:\t"+nci_ver_dict[version]+"\n")
                    self.resultVar.set(self.resultVar.get()+"Config Status:\t"+config_status_dict[cfgStatus]+"\n")
                    payload_decoded = True
                elif mt == MT.NTF:
                    reason = NCIData[3]
                    cfgStatus = NCIData[4]
                    self.resultVar.set(self.resultVar.get()+"Reason Code:\t"+hex(reason)+"\n")
                    self.resultVar.set(self.resultVar.get()+"Config Status:\t"+config_status_dict[cfgStatus]+"\n")
                    payload_decoded = True

        if not payload_decoded:
            self.resultVar.set(self.resultVar.get()+"Payload:\t"+NCIStr[6:]+"\n")
            


app = Application()
app.master.title('DAL NCI Decoder V1.2')
app.master.rowconfigure(0, weight=1)
app.master.columnconfigure(0, weight=1)
app.mainloop()
