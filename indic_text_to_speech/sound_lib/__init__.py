import os

class Library(object):
    def __init__(self, path):
        self.path = path

    def get_path(self, syllable):
        pass
    
    def filter_uncovered(self, syllables):
        uncovered_syllables = []
        for syllable in syllables:
            file_path = self.get_path(syllable=syllable)
            if not os.path.exists(file_path):
                uncovered_syllables.append(syllable)
        return uncovered_syllables
    
    def expand_to_cover(self, syllables):
        pass
    
    def get_syllable_files(self, syllables):
        pass