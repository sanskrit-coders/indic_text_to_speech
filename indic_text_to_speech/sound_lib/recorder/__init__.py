# Inspirations: https://stackoverflow.com/questions/44894796/pyaudio-and-pynput-recording-while-a-key-is-being-pressed-held-down, https://gist.github.com/sloria/5693955
import logging
import os
import sched
import time
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
    '''Helps record audio during the duration of key-presses.
    Records in mono by default.
    
    Example usage:
        recorder.KeyPressTriggeredRecorder("test.wav").record()
    '''

    def __init__(self, trigger_key=keyboard.Key.space, channels=1, rate=44100, frames_per_buffer=1024):
        self.trigger_key = trigger_key
        self.key_pressed = False
        self.recording_started = False
        self.recording_stopped = False
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.key_listener = keyboard.Listener(self._on_press, self._on_release)
        self.task_scheduler = sched.scheduler(time.time, time.sleep)

    def reset(self):
        self.key_pressed = False
        self.recording_started = False
        self.recording_stopped = False

    def _on_press(self, key):
        # logging.info(key)
        if key == self.trigger_key:
            self.key_pressed = True
        return True

    def _on_release(self, key):
        # logging.info(key)
        if key == self.trigger_key:
            self.key_pressed = False
            # Close listener
            return False
        return True

    def record(self, fname):
        self.reset()
        self.key_listener.start()
        recording_file = RecordingFile(
            fname=fname, mode='wb', channels=self.channels, rate=self.rate,
            frames_per_buffer=self.frames_per_buffer)
        logging.info("Recording: %s at %s", os.path.basename(fname), fname )
        logging.info("Record while you keep pressing: %s", self.trigger_key)
        def keychek_loop():
            if self.key_pressed and not self.recording_started:
                recording_file.start_recording()
                self.recording_started = True
            elif not self.key_pressed and self.recording_started:
                recording_file.stop_recording()
                self.recording_stopped = True
            if not self.recording_stopped:
                self.task_scheduler.enter(delay=.1, priority=1, action=keychek_loop)
                self.task_scheduler.run()
        keychek_loop()


class RecordingFile(object):
    """"Type of object corresponding to a particular recording.
    
    See :py:class:KeyPressTriggeredRecorder for example usage.
    """
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
            # logging.info(self._pa.get_device_info_by_index(x))
            if info["name"] == "pulse":
                self.chosen_device_index = info["index"]
                # logging.debug("Chosen index: %d", self.chosen_device_index)     
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
        # logging.info("Starting recording")
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.frames_per_buffer,
                                     stream_callback=self._get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def _get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        import os
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile



