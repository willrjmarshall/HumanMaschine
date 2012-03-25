import Live # This allows us (and the Framework methods) to use the Live API on occasion

from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
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
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section

CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods 
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods

class HumanMaschine(ControlSurface):
    __module__ = __name__
    __doc__ = " ProjectY keyboard controller script "
    
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= ProjectY log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up
        self._setup_mixer_control() # Setup the mixer object
        self._setup_session_control()  # Setup the session object
        self._setup_transport_control()
        self.set_suppress_rebuild_requests(False) # Turn rebuild back on, once we're done setting up


    def _setup_mixer_control(self):
        is_momentary = True # We use non-latching buttons (keys) throughout, so we'll set this as a constant
        num_tracks = 8 # Here we define the mixer width in tracks (a mixer has only one dimension)
        global mixer # We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
        mixer = MixerComponent(num_tracks, 0, with_eqs=False, with_filters=False) #(num_tracks, num_returns, with_eqs, with_filters)
        mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        """set up the mixer buttons"""        
        self.song().view.selected_track = mixer.channel_strip(0)._track
        #mixer.selected_strip().set_mute_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 42))
        #mixer.selected_strip().set_solo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 44))
        #mixer.selected_strip().set_arm_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 46))
        track_select_notes = [36, 38, 40, 41, 43, 45, 47, 35] #more note numbers need to be added if num_scenes is increased
        for index in range(num_tracks):
            mixer.channel_strip(index).set_arm_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, track_select_notes[index]))
	
	for index in range(num_tracks):
	    mixer.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 22 + index))   

    def _setup_session_control(self):
        is_momentary = True
        num_tracks = 8
        num_scenes = 4
        global session #We want to instantiate the global session as a SessionComponent object (it was a global "None" type up until now...)
        session = SessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes)
        session.set_offsets(0, 0) #(track_offset, scene_offset) Sets the initial offset of the red box from top left

        """set up the session buttons"""
        left_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 91)
        right_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 93)
        session_set_track_bank_buttons(right_button, left_button)

        up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 81)
        down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 92)
        session.set_scene_bank_buttons(up_button, down_button) # (up_button, down_button) This is to move the "red box" up or down (increment track up or down, not screen up or down, so they are inversed)

        session.set_mixer(mixer) #Bind the mixer to the session so that they move together
        selected_scene = self.song().view.selected_scene #this is from the Live API
        all_scenes = self.song().scenes
        index = list(all_scenes).index(selected_scene)
        session.set_offsets(0, index) #(track_offset, scene_offset)
            
        session.scene(0).set_launch_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 61)) #step through the scenes (in the session) and assign corresponding note from the launch_notes array

        stop_track_buttons = []
        for index in range(num_tracks):
            stop_track_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 62 + index))   #this would need to be adjusted for a longer array (because we've already used the next note numbers elsewhere)
        session.set_stop_track_clip_buttons(tuple(stop_track_buttons)) #array size needs to match num_tracks 


        clip_launch_notes = [48, 50, 52, 53, 55, 57, 59, 60] #this is a set of seven "white" notes, starting at C3
        for index in range(num_tracks):
            session.scene(0).clip_slot(index).set_launch_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, clip_launch_notes[index])) #step through scenes and assign a note to first slot of each 

    def _setup_transport_control(self):
        is_momentary = True
        transport = TransportComponent()

        transport.set_overdub_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 70))
        transport.set_metronome_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 71))    
           
    def disconnect(self):
        """clean things up on disconnect"""
        ControlSurface.disconnect(self)
        return None
