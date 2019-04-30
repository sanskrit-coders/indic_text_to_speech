import logging

from chandas import syllabize
from pydub import AudioSegment


class SpeechGenerator(object):
    def __init__(self, library, unit_silence_length_ms=1000):
        self.library = library
        self.unit_silence_length_ms = unit_silence_length_ms
    
    def get_audio_for_sentence(self, sentence_text):
        syllables = syllabize.get_syllables(in_string=sentence_text)
        self.library.expand_to_cover(syllables=syllables)
        logging.debug(syllables)
        audio_segments = self.library.get_syllable_audio_segments(syllables=syllables)
        return sum(audio_segments)

    def get_audio_for_sentences(self, sentences, output_path, output_format="mp3"):
        sentence_syllables = [syllabize.get_syllables(in_string=sentence) for sentence in sentences]
        all_syllables = [item for sublist in sentence_syllables for item in sublist]
        self.library.expand_to_cover(syllables=all_syllables)
        sounds = [self.get_audio_for_sentence(sentence) + AudioSegment.silent(duration=self.unit_silence_length_ms) for sentence in sentences]
        combined_sound = sum(sounds)
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined_sound.export(output_path, format=output_format)

