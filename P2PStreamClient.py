from P2PStreamClientGUI import PlaybackInterface

class StreamClient:
    
    def __init__(self, client_ip, client_base_port, filename, fileoffset):
        print("[DBG_Streamclient] Init enter with Args, client_ip: " + client_ip + ", client_base_port: " + str(client_base_port) + ", filename: " + filename + ", fileoffset: " + str(fileoffset))
        self.client_ip, self.client_base_port, self.filename, self.fileoffset = client_ip, client_base_port, filename, fileoffset
        self.client_port1 = client_base_port   #5000
        self.client_port2 = client_base_port+1 #5001
        self.client_port3 = client_base_port+2 #5002
        self.client_port4 = client_base_port+3 #5003
        self.host_port1 = client_base_port+5 #5005
        self.host_port2 = client_base_port+7 #5007

        self.client_str = " rtpbin name=rtpbin latency=100 udpsrc caps=application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H263-1998 port=" + str(self.client_port1) + " ! "

        self.client_str += "rtpbin.recv_rtp_sink_0 rtpbin. ! rtph263pdepay ! avdec_h263 ! videoconvert ! autovideosink udpsrc port=" + str(self.client_port2)  + " ! "

        self.client_str += "rtpbin.recv_rtcp_sink_0 rtpbin.send_rtcp_src_0 ! udpsink port=" + str(self.host_port1)  + " sync=false async=false "

        self.client_str += "udpsrc caps=application/x-rtp,media=(string)audio,clock-rate=(int)8000,encoding-name=(string)AMR,encoding-params=(string)1,octet-align=(string)1 port=" + str(self.client_port3) + " ! "

        self.client_str += "rtpbin.recv_rtp_sink_1 rtpbin. ! rtpamrdepay ! amrnbdec ! audioconvert ! audioresample ! autoaudiosink udpsrc port=" + str(self.client_port4) + " ! "

        self.client_str += "rtpbin.recv_rtcp_sink_1 rtpbin.send_rtcp_src_1 ! udpsink port="+ str(self.host_port2)  + " sync=false async=false"

        print("[DBG_Streamclient] client_port1: " + str(self.client_port1) + ", client_port2: " + str(self.client_port2) + ", client_port3: " + str(self.client_port3))
        print("[DBG_Streamclient] client_port4: " + str(self.client_port4) + ", host_port1: " + str(self.host_port1) + ", host_port2: " + str(self.host_port2))
        print("[DBG_Streamclient] client_str:\n" + self.client_str)


    def startReceiving(self):
        print("[DBG_Streamclient] start receiving")
        PlaybackInterface(self.client_str) # Add size of file parameter here as well.
#        self.player = Gst.parse_launch(self.client_str);
#        self.player.set_state(Gst.State.PLAYING) 
