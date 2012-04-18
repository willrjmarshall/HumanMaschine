from _Framework.ChannelStripComponent import ChannelStripComponent 
TRACK_FOLD_DELAY = 5
class MaschineChanStripComponent(ChannelStripComponent):
    ' Subclass of channel strip component using select button for (un)folding tracks '

    def __init__(self):
        ChannelStripComponent.__init__(self)
        self._toggle_fold_ticks_delay = -1
        self._register_timer_callback(self._on_timer)
        self._show_playing_clip_ticks_delay = -1


    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        ChannelStripComponent.disconnect(self)


    def _select_value(self, value):
        ChannelStripComponent._select_value(self, value)

        if (self.is_enabled() and (self._track != None)):
          if (value >= 1):
              if self.application().view.is_view_visible('Detail/Clip'):
                  self.application().view.show_view('Detail/DeviceChain')
                  self.application().view.is_view_visible('Detail/DeviceChain')
              else:
                  self.application().view.show_view('Detail/Clip')
                  self.application().view.is_view_visible('Detail/Clip')
          
          if (self._track.is_foldable and (self._select_button.is_momentary() and (value != 0))):
              self._toggle_fold_ticks_delay = TRACK_FOLD_DELAY
          else:
              self._toggle_fold_ticks_delay = -1

    def _on_timer(self):
        if (self.is_enabled() and (not self._shift_pressed)):
            if (self._show_playing_clip_ticks_delay > -1):
                if (self._show_playing_clip_ticks_delay == 0):
                    song = self.song()
                    playing_slot_index = song.view.selected_track.playing_slot_index
                    if (playing_slot_index > -1):
                        song.view.selected_scene = song.scenes[playing_slot_index]
                        if song.view.highlighted_clip_slot.has_clip:
                            self.application().view.show_view('Detail/Clip')
                self._show_playing_clip_ticks_delay -= 1

