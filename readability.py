import re
import nltk
from nltk.tokenize import sent_tokenize


def count(word):
    """
    Simple syllable counting
    """

    word = word if type(word) is str else str(word)

    word = word.lower()

    if len(word) <= 3:
        return 1

    word = re.sub('(?:[^laeiouy]es|[^laeiouy]e)$', '', word) # removed ed|
    word = re.sub('^y', '', word)
    matches = re.findall('[aeiouy]{1,2}', word)
    return len(matches)


class AnalyzerStatistics:
    def __init__(self, stats):
        self.stats = stats

    @property
    def num_poly_syllable_words(self):
        return self.stats['num_poly_syllable_words']

    @property
    def num_syllables(self):
        return self.stats['num_syllables']

    @property
    def num_letters(self):
        return self.stats['num_letters']

    @property
    def num_words(self):
        return self.stats['num_words']

    @property
    def num_sentences(self):
        return self.stats['num_sentences']

    @property
    def num_gunning_complex(self):
        return self.stats['num_gunning_complex']


    @property
    def avg_words_per_sentence(self):
        return self.num_words / self.num_sentences

    @property
    def avg_syllables_per_word(self):
        return self.num_syllables / self.num_words

    def __str__(self):
        return str(self.stats) + \
            ", avg_words_per_sentence " + str(self.avg_words_per_sentence) + \
            ", avg_syllables_per_word " + str(self.avg_syllables_per_word)


class Analyzer:
	
    def __init__(self):
        pass

    def analyze(self, text):
        stats = self._statistics(text)
        self.sentences = stats['sentences']  
        return AnalyzerStatistics(stats)

    def _tokenize_sentences(self, text):
        return sent_tokenize(text)

    def _tokenize(self, text):
        return re.compile(r"\b\S+\b").findall(text)

    def _is_punctuation(self, token):
        match = re.match('^[.,\/#!$%\'\^&\*;:{}=\-_`~()]$', token)
        return match is not None

    def _statistics(self, text):
        tokens = self._tokenize(text)
        syllable_count = 0
        poly_syllable_count = 0
        word_count = 0
        letters_count = 0
        gunning_complex_count = 0
        

        def is_gunning_complex(t, syllable_count):
            return syllable_count >= 3 and \
                not (self._is_proper_noun(t) or
                     self._is_compound_word(t))


        for t in tokens:

            if not self._is_punctuation(t):
                word_count += 1
                word_syllable_count = count(t)
                syllable_count += word_syllable_count
                letters_count += len(t)
                poly_syllable_count += 1 if word_syllable_count >= 3 else 0
                gunning_complex_count += \
                    1 if is_gunning_complex(t, word_syllable_count) \
                    else 0
               

        sentences = self._tokenize_sentences(text)
        sentence_count = len(sentences)

        return {
            'num_syllables': syllable_count,
            'num_poly_syllable_words': poly_syllable_count,
            'num_words': word_count,
            'num_sentences': sentence_count,
            'num_letters': letters_count,
            'num_gunning_complex': gunning_complex_count,
            'sentences': sentences,
        }

    def _is_proper_noun(self, token):
        # pos = pos_tag(token)[0][1]
        # return pos == 'NNP'
        return token[0].isupper()

    def _is_compound_word(self, token):
        return re.match('.*[-].*', token) is not None



class Result:
    def __init__(self, score, grade_level):
        self.score = score
        self.grade_level = grade_level

    def __str__(self):
        return "score: {}, grade_level: '{}'". \
            format(self.score, self.grade_level)

class Readability:

    def __init__(self, text):
        self._analyzer = Analyzer()
        self._statistics = self._analyzer.analyze(text)

    
    def flesch(self):
        """Calculate Flesch Reading Ease score."""
        return Flesch(self._statistics).score()

    def flesch_kincaid(self):
        """Calculate Flesch-Kincaid Grade Level."""
        return FleschKincaid(self._statistics).score()

    def gunning_fog(self):
        """Calculate Gunning Fog score."""
        return GunningFog_50(self._statistics).score()



    def statistics(self):
        return {
            'num_letters': self._statistics.num_letters,
            'num_words': self._statistics.num_words,
            'num_sentences': self._statistics.num_sentences,
            'num_polysyllabic_words': self._statistics.num_poly_syllable_words,
            'avg_words_per_sentence': self._statistics.avg_words_per_sentence,
            'avg_syllables_per_word': self._statistics.avg_syllables_per_word,
        }
		
class GunningFog_50:
    def __init__(self, stats):
        self._stats = stats
        if stats.num_words < 50:
            raise ValueError('50 words required.')

    def score(self):
        score = self._score()
        return Result(
            score=score,
            grade_level=self._grade_level(score)
        )

    def _score(self):
        s = self._stats
        word_per_sent = s.num_words / s.num_sentences
        poly_syllables_per_word = s.num_gunning_complex / s.num_words
        return 0.4 * (word_per_sent + 100 * poly_syllables_per_word)

    def _grade_level(self, score):
        rounded = round(score)
        if rounded < 6:
            return 'na'
        elif rounded >= 6 and rounded <= 12:
            return str(rounded)
        elif rounded >= 13 and rounded <= 16:
            return 'college'
        else:
            return 'college_graduate'

