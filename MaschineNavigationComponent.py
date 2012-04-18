import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
SHOW_PLAYING_CLIP_DELAY = 5

class MaschineNavigationComponent(ControlSurfaceComponent):
  __doc__= ' Component for navigating the currently selected device, and toggling between device and clip view '

  def __init__(self, left_button = None, right_button = None, on_off_button = None,
      metronome_button = None):
    ControlSurfaceComponent.__init__(self)

    self.left_button = left_button  
    self.right_button = right_button  

    identify_sender = True
    self.left_button.add_value_listener(self.nav_value, identify_sender)
    self.right_button.add_value_listener(self.nav_value, identify_sender)


  def nav_value(self, value, sender):
    modifier_pressed = True
    if sender == self.left_button:
      direction = Live.Application.Application.View.NavDirection.left
    else:
      direction = Live.Application.Application.View.NavDirection.right
    self.application().view.scroll_view(direction, 'Detail/DeviceChain', (not modifier_pressed))


