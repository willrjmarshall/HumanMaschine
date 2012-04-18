from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session

class MaschineSessionComponent(SessionComponent):
  __module__ = __name__
  __doc__ = "For das blinkenlichts"

  def __init__(self, num_tracks, num_scenes):
    SessionComponent.__init__(self, num_tracks, num_scenes)
    self.counter = 0
    self.on = True

  """ Called on timer """
  def flash_clip_slots(self):
    # Increment the frame counter
    self.counter = self.counter  + 1

    # Every 100 frames trigger pulse
    if self.counter == 2:
      # And reset the counter
      self.counter = 0

      for scene_index in range(4):
        for track_index in range(4):

          # Get the clip slot for each scene/track - row/column
          clip_slot = self.scene(scene_index).clip_slot(track_index)

          if clip_slot.has_clip(): 
            if clip_slot._clip_slot.clip.is_triggered or clip_slot._clip_slot.clip.is_playing or clip_slot._clip_slot.clip.is_recording:
              if self.on:
                value_to_send = clip_slot._started_value
              else:
                value_to_send = 0 
              clip_slot._launch_button.send_value(value_to_send)

      self.on = not self.on

