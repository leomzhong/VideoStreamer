import sys, os
import pygtk
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk, Gdk

class StreamServer:
    
    def __init__(self, client_ip, client_base_port=5000, filename="/home/ankur/ROUND1.MPG", fileoffset=0):
        print "[DBG_Streamserver] Init enter with Args, client_ip: " + client_ip + ", client_base_port: " + str(client_base_port) + ", filename: " + filename + ", fileoffset: " + str(fileoffset)
        self.client_ip, self.client_base_port, self.filename, self.fileoffset = client_ip, client_base_port, filename, fileoffset
        self.client_port1 = client_base_port   #5000
        self.client_port2 = client_base_port+1 #5001
        self.client_port3 = client_base_port+2 #5002
        self.client_port4 = client_base_port+3 #5003
        self.host_port1 = client_base_port+5 #5005
        self.host_port2 = client_base_port+7 #5007
        self.server_str = "rtpbin name=rtpbin uridecodebin uri=file://" + filename + " "

        #Sorry about the lengthy line 
        self.server_str += "name=decode decode. ! videoconvert ! videoscale ! videorate ! video/x-raw,width=352,height=288,framerate=15/1,pixel-aspect-ratio=1/1 ! videoconvert ! avenc_h263p ! rtph263ppay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 ! queue ! "

        self.server_str += "udpsink host=" + self.client_ip + " port=" + str(self.client_port1) + " "

        self.server_str += "ts-offset=0 rtpbin.send_rtcp_src_0 ! "

        self.server_str += "udpsink host=" + self.client_ip + " port=" + str(self.client_port2) + " "

        self.server_str += "sync=false async=false udpsrc port=" +  str(self.host_port1) + " ! "

        #self.server_str += "rtpbin.recv_rtcp_sink_0 autoaudiosrc ! audioconvert ! amrnbenc ! rtpamrpay ! rtpbin.send_rtp_sink_1 rtpbin.send_rtp_src_1 ! queue ! "
        self.server_str += "rtpbin.recv_rtcp_sink_0 decode. ! audioresample ! audioconvert ! amrnbenc ! rtpamrpay ! rtpbin.send_rtp_sink_1 rtpbin.send_rtp_src_1 ! queue ! "

        self.server_str += "udpsink host=" + self.client_ip + " port=" + str(self.client_port3) + " "

        self.server_str += "ts-offset=0 rtpbin.send_rtcp_src_1 ! "

        self.server_str += "udpsink host=" + self.client_ip + " port=" + str(self.client_port4) + " "
       
        self.server_str += "sync=false async=false udpsrc port=" +  str(self.host_port2) + " ! "

        self.server_str += " rtpbin.recv_rtcp_sink_1"

        print "[DBG_Streamserver] client_port1: " + str(self.client_port1) + ", client_port2: " + str(self.client_port2) + ", client_port3: " + str(self.client_port3)
        print "[DBG_Streamserver] client_port4: " + str(self.client_port4) + ", host_port1: " + str(self.host_port1) + ", host_port2: " + str(self.host_port2)
        print "[DBG_Streamserver] server_str:\n" + self.server_str 

        Gst.init([])
    
    def toString(self):
        result = "client_ip: " + self.client_ip + "\n"
        result += "client_base_port: " + self.client_base_port + "\n"
        result += "filename: " + self.filename + "\n"
        result += "offset: " + self.offset + "\n"
        return result

    def prepareStream(self):
        #self.player = Gst.parse_launch ("rtpbin name=rtpbin uridecodebin uri=file:///home/ankur/test_video2.mpeg name=decode decode. ! videoconvert ! videoscale ! videorate ! video/x-raw,width=352,height=288,framerate=15/1,pixel-aspect-ratio=1/1 ! videoconvert ! avenc_h263p ! rtph263ppay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 ! queue ! udpsink host=127.0.0.1 port=5000 ts-offset=0 rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=5001 sync=false async=false udpsrc port=5005 ! rtpbin.recv_rtcp_sink_0 autoaudiosrc ! audioconvert ! amrnbenc ! rtpamrpay ! rtpbin.send_rtp_sink_1 rtpbin.send_rtp_src_1 ! queue ! udpsink host=127.0.0.1 port=5002 ts-offset=0 rtpbin.send_rtcp_src_1 ! udpsink host=127.0.0.1 port=5003 sync=false async=false udpsrc port=5007 ! rtpbin.recv_rtcp_sink_1")
        self.player = Gst.parse_launch(self.server_str);

    def startStream(self):
    # Move the Stream to PLAYING state
        self.player.set_state(Gst.State.PLAYING) 
