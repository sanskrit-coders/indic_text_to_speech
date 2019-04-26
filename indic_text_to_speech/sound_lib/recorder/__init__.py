# Inspirations: https://stackoverflow.com/questions/44894796/pyaudio-and-pynput-recording-while-a-key-is-being-pressed-held-down, https://gist.github.com/sloria/5693955
import logging
import wave

import pyaudio
from pynput import keyboard


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(lineno)d %(message)s"
)

class KeyPressTriggeredRecorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, fname, trigger_key=keyboard.Key.space, channels=1, rate=44100, frames_per_buffer=1024):
        self.trigger_key = trigger_key
        self.key_pressed = False
        self.recording_started = False
        self.recording_stopped = False
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.recording_file = RecordingFile(
            fname=fname, mode='wb', channels=self.channels, rate=self.rate,
            frames_per_buffer=self.frames_per_buffer)
        self.key_listener = keyboard.Listener(self.on_press, self.on_release)

    def on_press(self, key):
        logging.info(key)
        if key == self.trigger_key:
            self.key_pressed = True
        return True

    def on_release(self, key):
        logging.info(key)
        if key == self.trigger_key:
            self.key_pressed = False
            # Close listener
            return False
        return True

    def record(self):
        logging.info("Waiting for key")
        self.key_listener.start()
        import threading
        def keychek_loop():
            if self.key_pressed and not self.recording_started:
                logging.info("Starting recording")
                self.recording_file.start_recording()
                self.recording_started = True
            elif not self.key_pressed and self.recording_started:
                self.recording_file.stop_recording()
                self.recording_stopped = True
            if not self.recording_stopped:
                threading.Timer(.1, keychek_loop).start()
        logging.info("Press the key")
        keychek_loop()


class RecordingFile(object):
    def __init__(self, fname, mode, channels,
                 rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.chosen_device_index = -1
        for x in range(0,self._pa.get_device_count()):
            info = self._pa.get_device_info_by_index(x)
            logging.info(self._pa.get_device_info_by_index(x))
            if info["name"] == "pulse":
                self.chosen_device_index = info["index"]
                logging.info("Chosen index: %d", self.chosen_device_index)        
        
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input_device_index=self.chosen_device_index,
                                     input=True,
                                     frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        logging.info("Starting recording")
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.frames_per_buffer,
                                     stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile



