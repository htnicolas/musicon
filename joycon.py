import pdb
import logging
import time

from pyjoycon import JoyCon, get_R_id, get_L_id
import tqdm

from MidiCom import MidiCom
from Controller import Controller


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Extrema(object):
    def __init__(self, val):
        self.mmin = val
        self.mmax = val

    def get_min_max(self, val):
        if val < self.mmin:
            self.mmin = val
        if val > self.mmax:
            self.mmax = val
        print(self.mmin, self.mmax)


if __name__ == "__main__":

    try:
        joycon_id = get_R_id()
        joycon = JoyCon(*joycon_id)
    except Exception as e:
        logger.exception("Check your joycon connection")
        raise Exception

    midi_chan = 0

    # Correspondences between joycon controls and midi CC's
    midimap_dict = {
            # "analog_r_horizontal": 14,
            # "analog_r_vertical": 15,
            # "gyro_x": 16,
            # "gyro_y": 17,
            # "gyro_z": 18,
            # "pointer_x": 19,
            # "pointer_y": 20,
            # "pointer_z": 21,
            "btn_r_a": 35,
            "btn_r_b": 36,
            "btn_r_x": 37,
            "btn_r_y": 39,
            # "btn_r_zr": 42,
            "btn_r_r": 43,
            "btn_r_sl": 44,
            "btn_r_sr": 45,
            # "btn_l_down": 44,
            "zr_pointer_x": 19,
            }

    # Read joycon status once to instantiate Controller object
    status = joycon.get_status()
    controller = Controller(status, midimap_dict, midi_chan)

    logger.info("Battery level: {}".format(status["battery"]["level"]))
    pbar = tqdm.tqdm(desc="loop")

    # Check value range by printing extrema
    check_extrema = False
    if check_extrema:
        val = status["accel"]["z"]
        extrema = Extrema(val)
        while 1:
            val = status["accel"]["z"]
            extrema.get_min_max(val)
            print(val)

    # Loop: read joycon status and dispatch MIDI messages
    while 1:
        status = joycon.get_status()
        controller.update_and_send(status)
        pbar.update(1)
        time.sleep(0.01)
    pbar.close()
