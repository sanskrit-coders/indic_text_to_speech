import indic_text_to_speech
from indic_text_to_speech import reader
from indic_text_to_speech.sound_lib import Library

speech_generator = indic_text_to_speech.SpeechGenerator(library=Library(path="/home/vvasuki/vvasuki-git/indic_sound_library_voice_male_vv/"))

sentences = reader.from_markdown_file(file_path="/home/vvasuki/vvasuki-git/kAvya/content/TIkA/padya/purANa/rAmAyaNa/1_bAla/01-kathAmukha/001_sanxepa.md")
speech_generator.get_audio_for_sentences(sentences=sentences, output_path="local/test.mp3")