import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time

from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import SessionZoomingComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.DeviceComponent import DeviceComponent # Class encapsulating all functions in Live's transport section
from _Framework.EncoderElement import EncoderElement # Class encapsulating all functions in Live's transport section


from MaschineSessionComponent import MaschineSessionComponent
from MaschineNavigationComponent import MaschineNavigationComponent
from LooperComponent import LooperComponent
from MaschineMixerComponent import MaschineMixerComponent


CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods 
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods

class HumanMaschine(ControlSurface):
    __module__ = __name__
    __doc__ = "Maschine MIDI controller script"
    
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectY log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up

        self.shift_button = ButtonElement(True, MIDI_CC_TYPE, 5, 104)        

        self._setup_mixer_control() # Setup the mixer object
        self._setup_device_control()
        self._setup_session_control()  # Setup the session object
        self._setup_transport_control()
        self.set_suppress_rebuild_requests(False) # Turn rebuild back on, once we're done setting up

        self._device_selection_follows_track_selection = True

        self._setup_looper()

        MaschineNavigationComponent(
            left_button = ButtonElement(True, MIDI_CC_TYPE, 3, 37), 
            right_button = ButtonElement(True, MIDI_CC_TYPE, 3, 38),
            detail_toggle_button = ButtonElement(True, MIDI_CC_TYPE, 3, 99),
            clip_track_button = ButtonElement(True, MIDI_CC_TYPE, 3, 100))
       #self.override_update()


    def _setup_mixer_control(self):
        is_momentary = True # We use non-latching buttons (keys) throughout, so we'll set this as a constant
        num_tracks = 4 # Here we define the mixer width in tracks (a mixer has only one dimension)
        global mixer # We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
        mixer = MaschineMixerComponent(num_tracks) #(num_tracks, num_returns, with_eqs, with_filters)

        mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)

        for index in range(num_tracks):
            strip = mixer.channel_strip(index)
            strip.set_select_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 48 + index))
            strip.set_mute_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 5, (46 + index)))
            strip.set_solo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 5, (50 + index)))
            strip.set_arm_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 6, (50 + index)))
	

    def _setup_session_control(self):
        is_momentary = True
        num_tracks = 4
        num_scenes = 4
        global session #We want to instantiate the global session as a SessionComponent object (it was a global "None" type up until now...)
        session = MaschineSessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes)
        session.set_offsets(0, 0) #(track_offset, scene_offset) Sets the initial offset of the red box from top left

        matrix = ButtonMatrixElement()

        self._register_timer_callback(session.flash_clip_slots)

        """set up the session buttons"""
        left_button = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 91)
        right_button = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 93)
        session.set_track_bank_buttons(right_button, left_button)

        # Stop buttons
        track_stop_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, 4, (55 + index)) for index in range(num_tracks) ]
        session.set_stop_track_clip_buttons(tuple(track_stop_buttons))

        up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 81)
        down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 92)
        session.set_scene_bank_buttons(down_button, up_button) # (up_button, down_button) This is to move the "red box" up or down (increment track up or down, not screen up or down, so they are inversed)

        session.set_mixer(mixer) #Bind the mixer to the session so that they move together
        selected_scene = self.song().view.selected_scene #this is from the Live API
        all_scenes = self.song().scenes
        index = list(all_scenes).index(selected_scene)
        session.set_offsets(0, index) #(track_offset, scene_offset)

        scene_launch_buttons = []
            
        for scene_index in range(4):
          scene = session.scene(scene_index)
          launch_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, (124 + scene_index))
          scene.set_launch_button(launch_button)
          scene_launch_buttons.append(launch_button)

        clip_launch_notes = [
          [24, 25, 26, 27],
          [20, 21, 22, 23],
          [16, 17, 18, 19],
          [12, 13, 14, 15],
        ]

        for scene_index in range(num_scenes):
          button_row = []
          for track_index in range(num_tracks):
            clip_slot = session.scene(scene_index).clip_slot(track_index)
            clip_slot.set_triggered_to_record_value(127)
            clip_slot.set_recording_value(127)
            clip_slot.set_started_value(127)
            clip_slot.set_stopped_value(127)
            button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 2, clip_launch_notes[scene_index][track_index])
            clip_slot.set_launch_button(button)
            button_row.append(button)
          matrix.add_row(tuple(button_row))

        session_zoom = SessionZoomingComponent(session)
        session_zoom.set_zoom_button(self.shift_button)
        session_zoom.set_nav_buttons(up_button, down_button, left_button, right_button)
        session_zoom.set_scene_bank_buttons(tuple(scene_launch_buttons))
        session_zoom.set_button_matrix(matrix)
        session_zoom.set_stopped_value(0)
        session_zoom.set_selected_value(127)


    def _setup_device_control(self):
      device_param_controls = []
    
      for index in range(8):
        encoder = EncoderElement(MIDI_CC_TYPE, 0, 22 + index, Live.MidiMap.MapMode.absolute)
        device_param_controls.append(encoder)

      device = DeviceComponent()
      device.set_parameter_controls(tuple(device_param_controls))
      self.set_device_component(device)

      device.set_on_off_button(ButtonElement(True, MIDI_CC_TYPE, 3, 51))

    def _setup_transport_control(self):
      is_momentary = True
      transport = TransportComponent()
      transport.set_overdub_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 70))
      transport.set_play_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 108))    
      transport.set_stop_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 109))    
      transport.set_record_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 110))    
      transport.set_metronome_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 52))

      nudge_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 112)
      nudge_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 111)
      transport.set_nudge_buttons(nudge_up_button, nudge_down_button)


      transport.set_tap_tempo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, 113))

    def _setup_looper(self):
      looper = LooperComponent(self)
      is_momentary = True
      loop_on = ButtonElement(is_momentary, MIDI_CC_TYPE, 4, 79) 
      loop_start = ButtonElement(is_momentary, MIDI_CC_TYPE, 4, 80) 
      halve = ButtonElement(is_momentary, MIDI_CC_TYPE, 4, 81) 
      double = ButtonElement(is_momentary, MIDI_CC_TYPE, 4, 82) 
      looper.set_shift_button(self.shift_button)
      looper.set_loop_toggle_button(loop_on)
      looper.set_loop_start_button(loop_start)
      looper.set_loop_double_button(double) 
      looper.set_loop_halve_button(halve) 
           
    def disconnect(self):
        """clean things up on disconnect"""
        ControlSurface.disconnect(self)
        return None
