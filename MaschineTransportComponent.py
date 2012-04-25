from _Framework.TransportComponent import TransportComponent 

class MaschineTransportComponent(TransportComponent):
  'Customized transport class that supports BPM up and BPM down buttons'

  def __init__(self, tempo_top = 200, tempo_bottom = 20):
    TransportComponent.__init__(self)
    
    self.tempo_top = tempo_top
    self.tempo_bottom = tempo_bottom


  def increment_bpm(self, ev):
    self.song().tempo = self.song().tempo + 0.1

  def decrement_bpm(self, ev):
    self.song().tempo = self.song().tempo - 0.1

  def _tempo_value(self, value):
    if self.is_enabled(): 
      if value > 100:
        self.song().tempo = self.song().tempo + 0.1 
      else:
        self.song().tempo = self.song().tempo - 0.1 
      self._tempo_control.send_value(100, True)

