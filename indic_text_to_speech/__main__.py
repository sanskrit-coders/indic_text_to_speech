import indic_text_to_speech
from indic_text_to_speech.sound_lib import Library

speech_generator = indic_text_to_speech.SpeechGenerator(library=Library(path="/home/vvasuki/vvasuki-git/indic_sound_library_voice_male_vv/"))

speech_generator.get_audio_for_text(text="नमो विनायकाय! नमो महते!", output_path="local/test.mp3")