import sys, os
import pygtk
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk, Gdk

class StreamServer:
    
    def __init__(self, client_ip, client_port, filename="/home/ankur/ROUND1.MPG", fileoffset=0.0):
        self.client_ip, self.client_port, self.filename, self.fileoffset = client_ip, client_port, filename, fileoffset
        Gst.init([])
    
    def toString(self):
        result = "client_ip: " + self.client_ip + "\n"
        result += "client_port: " + self.client_port + "\n"
        result += "filename: " + self.filename + "\n"
        result += "offset: " + self.offset + "\n"
        return result

    def prepareStream(self):
        self.player = Gst.parse_launch ("rtpbin name=rtpbin uridecodebin uri=file:///home/ankur/test_video2.mpeg name=decode decode. ! videoconvert ! videoscale ! videorate ! video/x-raw,width=352,height=288,framerate=15/1,pixel-aspect-ratio=1/1 ! videoconvert ! avenc_h263p ! rtph263ppay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 ! queue ! udpsink host=127.0.0.1 port=5000 ts-offset=0 rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=5001 sync=false async=false udpsrc port=5005 ! rtpbin.recv_rtcp_sink_0 autoaudiosrc ! audioconvert ! amrnbenc ! rtpamrpay ! rtpbin.send_rtp_sink_1 rtpbin.send_rtp_src_1 ! queue ! udpsink host=127.0.0.1 port=5002 ts-offset=0 rtpbin.send_rtcp_src_1 ! udpsink host=127.0.0.1 port=5003 sync=false async=false udpsrc port=5007 ! rtpbin.recv_rtcp_sink_1")

    def startStream(self):
    # Move the Stream to PLAYING state
        self.player.set_state(Gst.State.PLAYING) 
