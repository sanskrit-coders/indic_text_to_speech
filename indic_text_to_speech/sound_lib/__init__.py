import logging
import os

from pydub import AudioSegment

from indic_text_to_speech.sound_lib import recorder


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(lineno)d %(message)s"
)


class Library(object):
    def __init__(self, path):
        self.path = path

    def get_path(self, syllable):
        return os.path.join(self.path, "syllable_sounds", syllable[0], syllable + ".wav")
    
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
            logging.info("We're going to record sounds for the following syllables into the sound library: %s", syllables)
            for syllable in uncovered_syllables:
                file_path = self.get_path(syllable=syllable)
                recorder.KeyPressTriggeredRecorder().record(fname=file_path)
                audio_segment = AudioSegment.from_wav(file_path)
    
    def get_syllable_files(self, syllables):
        self.expand_to_cover(syllables=syllables)
        return [self.get_path(syllable=syllable) for syllable in syllables]
    
    def get_syllable_audio_segments(self, syllables):
        syllable_files = self.get_syllable_files(syllables=syllables)
        audio_segments = []
        import pydub.effects
        for syllable_file in syllable_files:
            audio_segment = AudioSegment.from_wav(syllable_file)
            # Careful with the below let you end up removing vyanjana-s and even some svara-s!
            audio_segment = pydub.effects.strip_silence(audio_segment, silence_len=300, silence_thresh=-32, padding=200)
            audio_segments.append(audio_segment)
        return audio_segments
