from chandas import syllabize
from pydub import AudioSegment


class SpeechGenerator(object):
    def __init__(self, library, unit_silence_length_ms=1000):
        self.library = library
        self.unit_silence_length_ms = unit_silence_length_ms
    
    def get_audio_for_sentence(self, sentence_text):
        syllables = syllabize.get_syllables(in_string=sentence_text)
        syllable_files = self.library.get_syllable_files(syllables=syllables)
        sounds = [AudioSegment.from_wav(syllable_file) for syllable_file in syllable_files]
        return sum(sounds)

    def get_audio_for_text(self, text, output_path, output_format="mp3", sentence_separator_pattern="[।॥!]"):
        self.library.expand_to_cover(syllables=syllabize.get_syllables(in_string=text))
        import regex
        sentences = regex.split(sentence_separator_pattern, text)
        sounds = [self.get_audio_for_sentence(sentence) + AudioSegment.silent(duration=self.unit_silence_length_ms) for sentence in sentences]
        combined_sound = sum(sounds)
        combined_sound.export(output_path, format=output_format)