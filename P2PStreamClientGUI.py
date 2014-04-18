from os import path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo


class PlaybackInterface:

    PLAY_IMAGE = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON)
    PAUSE_IMAGE = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PAUSE, Gtk.IconSize.BUTTON)

    def __init__(self, launch_str):
        self.main_window = Gtk.Window()


        self.main_window.connect('destroy', self.quit)
        self.main_window.set_default_size(800, 450)

        self.drawingarea = Gtk.DrawingArea()
        self.drawingarea.modify_bg(Gtk.StateType.NORMAL, self.drawingarea.props.style.black)
        self.play_button = Gtk.Button()
        self.slider = Gtk.HScale()

        self.hbox = Gtk.HBox()
        self.hbox.pack_start(self.play_button, False, False, 0)
        
        self.hbox.pack_start(self.slider, True, True, 0)
        
        
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.drawingarea, True, True, 0)
        self.vbox.pack_start(self.hbox, False, False, 0)
        self.main_window.add(self.vbox)
        self.main_window.connect('destroy', self.on_destroy)

        self.play_button.set_image(self.PLAY_IMAGE)
        self.play_button.connect('clicked', self.on_play)

        self.slider.set_range(0, 100)
        self.slider.set_increments(1, 10)
        self.slider.connect('value-changed', self.on_slider_change)

        self.main_window.set_border_width(6)
        self.main_window.set_size_request(600, 50)

        Gst.init([])
        #self.playbin = Gst.parse_launch("rtpbin name=rtpbin latency=100 udpsrc caps=application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H263-1998 port=5000 ! rtpbin.recv_rtp_sink_0 rtpbin. ! rtph263pdepay ! avdec_h263 ! videoconvert ! autovideosink udpsrc port=5001 ! rtpbin.recv_rtcp_sink_0 rtpbin.send_rtcp_src_0 ! udpsink port=5005 sync=false async=false udpsrc caps=application/x-rtp,media=(string)audio,clock-rate=(int)8000,encoding-name=(string)AMR,encoding-params=(string)1,octet-align=(string)1 port=5002 ! rtpbin.recv_rtp_sink_1 rtpbin. ! rtpamrdepay ! amrnbdec ! audioconvert ! audioresample ! autoaudiosink udpsrc port=5003 ! rtpbin.recv_rtcp_sink_1 rtpbin.send_rtcp_src_1 ! udpsink port=5007 sync=false async=false")
        self.playbin = Gst.parse_launch(launch_str)
        self.main_window.show_all()

        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()

        self.bus.connect("message::eos", self.on_finish)

        self.is_playing = False
        
	# This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)
        self.xid = self.drawingarea.get_property('window').get_xid()
        Gtk.main()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def quit(self, window):
        self.playbin.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_finish(self, bus, message):
        self.playbin.set_state(Gst.State.PAUSED)
        self.play_button.set_image(self.PLAY_IMAGE)
        self.is_playing = False
        self.playbin.seek_simple(Gst.Format.TIME, Gst.SEEK_FLAG_FLUSH, 0)
        self.slider.set_value(0)

    def on_destroy(self, window):
        # NULL state allows the pipeline to release resources
        self.playbin.set_state(Gst.State.NULL)
        self.is_playing = False
        Gtk.main_quit()

    def on_play(self, button):
        if not self.is_playing:
            self.play_button.set_image(self.PAUSE_IMAGE)
            self.is_playing = True

            self.playbin.set_state(Gst.State.PLAYING)
            GObject.timeout_add(100, self.update_slider)

        else:
            self.play_button.set_image(self.PLAY_IMAGE)
            self.is_playing = False

            self.playbin.set_state(Gst.State.PAUSED)

    def on_slider_change(self, slider):
        seek_time_secs = slider.get_value()
        self.playbin.seek_simple(Gst.Format.TIME, Gst.SEEK_FLAG_FLUSH | Gst.SEEK_FLAG_KEY_UNIT, seek_time_secs * Gst.SECOND)

    def update_slider(self):
        if not self.is_playing:
            return False # cancel timeout

        try:
            nanosecs = self.playbin.query_position(Gst.Format.TIME)[1]
            duration_nanosecs = self.playbin.query_duration(Gst.Format.TIME)[1]
            # block seek handler so we don't seek when we set_value()
            self.slider.handler_block_by_func(self.on_slider_change)

            self.slider.set_range(0, float(10000000) / Gst.SECOND)
            self.slider.set_value(float(nanosecs) / Gst.SECOND)

            self.slider.handler_unblock_by_func(self.on_slider_change)

        except Gst.QueryError:
            # pipeline must not be ready and does not know position
         pass

        return True # continue calling every 30 milliseconds
