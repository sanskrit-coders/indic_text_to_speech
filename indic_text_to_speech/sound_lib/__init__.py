import logging
import os

from pydub import AudioSegment

from audio_utils import recorder


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(lineno)d %(message)s"
)
logging.getLogger("pydub.converter").setLevel(logging.WARNING)


class Library(object):
    def __init__(self, path):
        self.path = path

    def get_path(self, syllable):
        return os.path.join(self.path, "syllable_sounds", syllable[0], syllable + ".mp3")
    
    def get_uncovered(self, syllables):
        uncovered_syllables = []
        for syllable in syllables:
            file_path = self.get_path(syllable=syllable)
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                uncovered_syllables.append(syllable)
        return set(uncovered_syllables)

    def expand_to_cover(self, syllables):
        uncovered_syllables = self.get_uncovered(syllables=syllables)
        if len(uncovered_syllables) > 0:
            logging.info("We got a text of %d syllables, of which %d lack audio.", len(syllables), len(uncovered_syllables))
            logging.info("We're going to record sounds for the following syllables into the sound library: %d", len(uncovered_syllables))
            for syllable in uncovered_syllables:
                file_path = self.get_path(syllable=syllable)
                recorder.KeyPressTriggeredRecorder().record(fname=file_path)
    
    def get_syllable_files(self, syllables):
        self.expand_to_cover(syllables=syllables)
        return [self.get_path(syllable=syllable) for syllable in syllables]

    def get_audio_for_syllable(self, syllable):
        import pydub.effects
        audio_segment = AudioSegment.from_mp3(self.get_path(syllable=syllable))
        # Careful with the below let you end up removing vyanjana-s and even some svara-s!
        # audio_segment = pydub.effects.speedup(audio_segment, playback_speed=1)
        audio_segment = pydub.effects.strip_silence(audio_segment, silence_len=100, silence_thresh=-32, padding=100)
        return audio_segment

    def get_syllable_audio_segments(self, syllables):
        audio_segments = [self.get_audio_for_syllable(syllable=syllable) for syllable in syllables]
        return audio_segments

