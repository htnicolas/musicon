# Class to handle MIDI communications
# TODO -03/09/20- : Handle Midi Learn

import sys
import time
import logging
import pdb

import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

from MidiOutWrapper import MidiOutWrapper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MidiCom(object):
    def __init__(self, virtual_port_name):
        """
        Manages communication using the MIDI protocol
        """
        assert isinstance(virtual_port_name, str)

        midiout = rtmidi.MidiOut()

        # Ask user to select which port they want to send MIDI data on
        available_ports = midiout.get_ports()

        if len(available_ports) == 0:
            # Open a virtual port
            logger.info("Opening virtual port: {}".format(virtual_port_name))
            midiout.open_virtual_port(virtual_port_name)
        else:
            # Add virtual port to the list of physical ports
            available_ports.append("{} (virtual)".format(virtual_port_name))
            port_dict = {k:v for k, v in enumerate(available_ports)}
            logger.info("Available ports:")
            logger.info(port_dict)

            while True:
                port_select = int(input("Select which port number to use:\n"))

                # The last port is the virtual port
                if port_select == len(available_ports):
                    midiout.open_virtual_port(virtual_port_name)
                    break
                else:
                    try:
                        logger.info("Opening port #{}: {}".format(port_select, port_dict[port_select]))
                        midiout.open_port(port_select)
                        break
                    except Exception as e:
                        logger.exception(e)
                        pdb.set_trace()

        self.mid = MidiOutWrapper(midiout)


    def midimap(self, cc_val_dict):
        """
        Send out CC for each parameter that needs to be midimapped
        """
        assert isinstance(cc_val_dict, dict)

        cc_val = 0
        prompt = "Press a key:\n-'a' for angle\n- 's' for spread\n- 'q' to quit midilearn\n"


    def send(self, cc_val_dict, channel):
        """
        Send out CC numbers
        :cc_val_dict:   Dictionary containing {<cc_number>: <cc_val>}
                        where cc_number is the control change number
                        and cc_val is the control change value (spread, angle...)
        """
        assert isinstance(cc_val_dict, dict)

        for cc_num, send_val in cc_val_dict.items():
            logger.info("#CC_{}, val: {}".format(cc_num, send_val))
            self.mid.send_control_change(cc_num, send_val, channel)

if __name__ == '__main__':
    """
    Note: The following are mappings for the NS3
    CC1:   Mod wheel
    CC11:  Foot Controller
    CC56:  Resonance
    CC59:  Cutoff
    CC82:  Effect 1 on/off (127/0)
    CC84:  Effect 1 org/piano/synth (0/64/127)
    CC85:  Effect 1 Amount
    CC86:  Effect 1 Rate
    """

    import time

    channel = 1
    cc_num_spread = 3
    cc_num_angle = 4
    midi_mapping = {cc_num_spread: 0, cc_num_angle: 120}

    mc = MidiCom(virtual_port_name = "vport_test")
    # mc.send(midi_mapping)
    for k in range(0, 127):
        time.sleep(1)
        mc.send({59: k}, channel)
        # mc.send({133: k})
