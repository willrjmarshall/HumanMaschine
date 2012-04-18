from _Framework.MixerComponent import MixerComponent 
from MaschineChanStripComponent import MaschineChanStripComponent 

class MaschineMixerComponent(MixerComponent):
    ' Special mixer class that uses return tracks alongside midi and audio tracks '

    def __init__(self, num_tracks):
        MixerComponent.__init__(self, num_tracks)

    def _create_strip(self):
        return MaschineChanStripComponent()
