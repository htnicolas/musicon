"""
Sample status:
{
 "battery": {
  "charging": 0,
  "level": 4
 },
 "buttons": {
  "right": {
   "y": 0,
   "x": 0,
   "b": 0,
   "a": 0,
   "sr": 0,
   "sl": 0,
   "r": 0,
   "zr": 0
  },
  "shared": {
   "minus": 0,
   "plus": 0,
   "r-stick": 0,
   "l-stick": 0,
   "home": 0,
   "capture": 0,
   "charging-grip": 0
  },
  "left": {
   "down": 0,
   "up": 0,
   "right": 0,
   "left": 0,
   "sr": 0,
   "sl": 0,
   "l": 0,
   "zl": 0
  }
 },
 "analog-sticks": {
  "left": {
   "horizontal": 0,
   "vertical": 0
  },
  "right": {
   "horizontal": 903,
   "vertical": 2089
  }
 },
 "accel": {
  "x": 647,
  "y": -123,
  "z": -4062
 },
 "gyro": {
  "x": 25,
  "y": -15,
  "z": 23
 }
}

"""

from MidiCom import MidiCom
import pdb

def map_range(val, min_in, max_in, min_out=0, max_out=127):
    val = max(min(max_in, val), min_in)
    in_range = float(max_in - min_in)
    out_range = max_out - min_out
    val_scaled = (val - min_in) / in_range
    val_out = min_out + val_scaled * out_range
    return int(val_out)

class Controller(object):
    def __init__(self, status, midimap_dict, midi_chan=0):
        """
        :status:            Dictionary returned by joycon.get_status(). See joycon.py
        :midimap_dict:      Dictionary mapping joycon control to midi pitch / cc num
                            e.g.: { "analog_r_horizontal": 21} to map horiz R analog to pich 21
        """
        assert len(midimap_dict) > 0

        self.config = midimap_dict
        self.midi_chan = midi_chan

        self.midicom = MidiCom(virtual_port_name = "conductor_virtual_port")

        # Min, Max for range mapping
        self.analog_r_horizontal_min = 786
        self.analog_r_horizontal_max = 3682
        self.analog_r_vertical_min = 586
        self.analog_r_vertical_max = 3007
        self.gyro_min = -8000
        self.gyro_max = 8000
        self.pointer_min = -5000
        self.pointer_max = 5000

        # Right joystick
        self.prev_analog_r_horizontal = map_range(
                status["analog-sticks"]["right"]["horizontal"],
                self.analog_r_horizontal_min,
                self.analog_r_horizontal_max)
        self.prev_analog_r_vertical = map_range(
                status["analog-sticks"]["right"]["vertical"],
                self.analog_r_vertical_min,
                self.analog_r_vertical_max)

        # Buttons:
        self.prev_btn_r_a = status["buttons"]["right"]["a"]
        self.prev_btn_r_b = status["buttons"]["right"]["b"]
        self.prev_btn_r_x = status["buttons"]["right"]["x"]
        self.prev_btn_r_y = status["buttons"]["right"]["y"]
        self.prev_btn_r_r = status["buttons"]["right"]["r"]
        self.prev_btn_r_zr = status["buttons"]["right"]["zr"]
        self.prev_btn_r_sl = status["buttons"]["right"]["sl"]
        self.prev_btn_r_sr = status["buttons"]["right"]["sr"]

        self.prev_btn_l_down = status["buttons"]["left"]["down"]

        self.prev_btn_plus = status["buttons"]["shared"]["plus"]
        self.prev_btn_home = status["buttons"]["shared"]["home"]

        # Accel
        self.prev_accel_r_x = status["accel"]["x"]
        self.prev_accel_r_y = status["accel"]["y"]
        self.prev_accel_r_z = status["accel"]["z"]

        # Accel
        self.prev_gyro_r_x = status["gyro"]["x"]
        self.prev_gyro_r_y = status["gyro"]["y"]
        self.prev_gyro_r_z = status["gyro"]["z"]

    def update_and_send(self, status):
        """
        If state changes, send corresponding midi message
        """

        # Right joystick horizontal
        if "analog_r_horizontal" in self.config:
            analog_r_horizontal = map_range(
                    status["analog-sticks"]["right"]["horizontal"],
                    self.analog_r_horizontal_min,
                    self.analog_r_horizontal_max)
            if analog_r_horizontal != self.prev_analog_r_horizontal:
                self.midicom.mid.send_control_change(cc=self.config["analog_r_horizontal"], value=analog_r_horizontal)
                self.prev_analog_r_horizontal = analog_r_horizontal

        # Right joystick vertical
        if "analog_r_vertical" in self.config:
            analog_r_vertical = map_range(
                    status["analog-sticks"]["right"]["vertical"],
                    self.analog_r_vertical_min,
                    self.analog_r_vertical_max)
            if analog_r_vertical != self.prev_analog_r_vertical:
                self.midicom.mid.send_control_change(cc=self.config["analog_r_vertical"], value=analog_r_vertical)
                self.prev_analog_r_vertical = analog_r_vertical

        # Continuous send-----------------------------------------------------------------------------
        # Gyro x - right
        if "gyro_x" in self.config:
            gyro_x = map_range(
                    status["gyro"]["x"],
                    self.gyro_min,
                    self.gyro_max)
            self.midicom.mid.send_control_change(cc=self.config["gyro_x"], value=gyro_x)

        # Gyro y - right
        if "gyro_y" in self.config:
            gyro_y = map_range(
                    status["gyro"]["y"],
                    self.gyro_min,
                    self.gyro_max)
            self.midicom.mid.send_control_change(cc=self.config["gyro_y"], value=gyro_y)

        # Gyro z - right
        if "gyro_z" in self.config:
            gyro_z = map_range(
                    status["gyro"]["z"],
                    self.gyro_min,
                    self.gyro_max)
            self.midicom.mid.send_control_change(cc=self.config["gyro_z"], value=gyro_z)

        # Pointer x - right
        if "pointer_x" in self.config:
            pointer_x = map_range(
                    status["accel"]["x"],
                    self.pointer_min,
                    self.pointer_max)
            self.midicom.mid.send_control_change(cc=self.config["pointer_x"], value=pointer_x)

        # Pointer y - right
        if "pointer_y" in self.config:
            pointer_y = map_range(
                    status["accel"]["y"],
                    self.pointer_min,
                    self.pointer_max)
            self.midicom.mid.send_control_change(cc=self.config["pointer_y"], value=pointer_y)

        # Pointer z - right
        if "pointer_z" in self.config:
            pointer_z = map_range(
                    status["accel"]["z"],
                    self.pointer_min,
                    self.pointer_max)
            self.midicom.mid.send_control_change(cc=self.config["pointer_z"], value=pointer_z)

        # Buttons ------------------------------------------------------------------------------------
        # a - right
        if "btn_r_a" in self.config:
            btn_r_a = status["buttons"]["right"]["a"]
            if btn_r_a != self.prev_btn_r_a:
                if btn_r_a == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_a"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_a"], ch=self.midi_chan)
                self.prev_btn_r_a = btn_r_a

        # b - right
        if "btn_r_b" in self.config:
            btn_r_b = status["buttons"]["right"]["b"]
            if btn_r_b != self.prev_btn_r_b:
                if btn_r_b == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_b"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_b"], ch=self.midi_chan)
                self.prev_btn_r_b = btn_r_b

        # x - right
        if "btn_r_x" in self.config:
            btn_r_x = status["buttons"]["right"]["x"]
            if btn_r_x != self.prev_btn_r_x:
                if btn_r_x == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_x"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_x"], ch=self.midi_chan)
                self.prev_btn_r_x = btn_r_x

        # y - right
        if "btn_r_y" in self.config:
            btn_r_y = status["buttons"]["right"]["y"]
            if btn_r_y != self.prev_btn_r_y:
                if btn_r_y == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_y"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_y"], ch=self.midi_chan)
                self.prev_btn_r_y = btn_r_y

        # r - right
        if "btn_r_r" in self.config:
            btn_r_r = status["buttons"]["right"]["r"]
            if btn_r_r != self.prev_btn_r_r:
                if btn_r_r == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_r"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_r"], ch=self.midi_chan)
                self.prev_btn_r_r = btn_r_r

        # zr - right
        if "btn_r_zr" in self.config:
            btn_r_zr = status["buttons"]["right"]["zr"]
            if btn_r_zr != self.prev_btn_r_zr:
                if btn_r_zr == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_zr"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_zr"], ch=self.midi_chan)
                self.prev_btn_r_zr = btn_r_zr

        # sl - right
        if "btn_r_sl" in self.config:
            btn_r_sl = status["buttons"]["right"]["sl"]
            if btn_r_sl != self.prev_btn_r_sl:
                if btn_r_sl == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_sl"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_sl"], ch=self.midi_chan)
                self.prev_btn_r_sl = btn_r_sl

        # sr - right
        if "btn_r_sr" in self.config:
            btn_r_sr = status["buttons"]["right"]["sr"]
            if btn_r_sr != self.prev_btn_r_sr:
                if btn_r_sr == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_r_sr"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_r_sr"], ch=self.midi_chan)
                self.prev_btn_r_sr = btn_r_sr

        # down - left
        if "btn_l_down" in self.config:
            btn_l_down = status["buttons"]["left"]["down"]
            if btn_l_down != self.prev_btn_l_down:
                if btn_l_down == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_l_down"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_l_down"], ch=self.midi_chan)
                self.prev_btn_l_down = btn_l_down

        # plus - shared
        if "btn_plus" in self.config:
            btn_plus = status["shared"]["plus"]
            if btn_plus != self.prev_btn_plus:
                if btn_plus == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_plus"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_plus"], ch=self.midi_chan)
                self.prev_btn_plus = btn_plus

        # home - shared
        if "btn_home" in self.config:
            btn_home = status["shared"]["plus"]
            if btn_home != self.prev_btn_home:
                if btn_home == 1:
                    self.midicom.mid.send_note_on(note=self.config["btn_home"], ch=self.midi_chan)
                else:
                    self.midicom.mid.send_note_off(note=self.config["btn_home"], ch=self.midi_chan)
                self.prev_btn_home = btn_home

        # Hold zr to enable continuous send: pitch
        if "zr_pointer_x" in self.config:
            btn_r_zr = status["buttons"]["right"]["zr"]
            if btn_r_zr:
                pointer_x = map_range(
                        status["accel"]["x"],
                        self.pointer_min,
                        self.pointer_max)
                self.midicom.mid.send_control_change(cc=self.config["zr_pointer_x"], value=pointer_x)
                # self.midicom.mid.send_pitch_bend(value=pointer_x)
                # print(pointer_x)

