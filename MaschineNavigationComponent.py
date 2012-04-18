import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
SHOW_PLAYING_CLIP_DELAY = 5

class MaschineNavigationComponent(ControlSurfaceComponent):
  __doc__= ' Component for navigating the currently selected device, and toggling between device and clip view '

  def __init__(self, left_button = None, right_button = None, 
      detail_toggle_button = None, clip_track_button = None):
    ControlSurfaceComponent.__init__(self)

    self.left_button = left_button  
    self.right_button = right_button  
    self.toggle_button = detail_toggle_button  
    self.clip_track_button = clip_track_button  

    identify_sender = True
    self.left_button.add_value_listener(self.nav_value, identify_sender)
    self.right_button.add_value_listener(self.nav_value, identify_sender)

    self.toggle_button.add_value_listener(self.detail_toggle_value)
    self.clip_track_button.add_value_listener(self.clip_toggle_value)

  def detail_toggle_value(self, value):
    if self.is_enabled() and value != 0:
      if (not self.application().view.is_view_visible('Detail')):
          self.application().view.show_view('Detail')
      else:
          self.application().view.hide_view('Detail')	    

  def clip_toggle_value(self, value):
    if self.is_enabled() and value != 0:
      if (not self.application().view.is_view_visible('Detail')):
          self.application().view.show_view('Detail')
      if (not self.application().view.is_view_visible('Detail/DeviceChain')):
          self.application().view.show_view('Detail/DeviceChain')
      else:
          self.application().view.show_view('Detail/Clip')

      

  def nav_value(self, value, sender):
    modifier_pressed = True
    if sender == self.left_button:
      direction = Live.Application.Application.View.NavDirection.left
    else:
      direction = Live.Application.Application.View.NavDirection.right
    self.application().view.scroll_view(direction, 'Detail/DeviceChain', (not modifier_pressed))


