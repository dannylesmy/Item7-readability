# based on py-readabilty-metrics package https://github.com/cdimascio/py-readability-metrics

import re
import nltk
import math
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
   

    def flesch_kincaid(self):
        """Calculate Flesch-Kincaid Grade Level."""
        return FleschKincaid(self._statistics).score()

    def gunning_fog(self):
        """Calculate Gunning Fog score."""
        return GunningFog_50(self._statistics).score()
        
    def ari(self):
        """Calculate Automated Readability Index (ARI)."""
        return ARI(self._statistics).score()

    def coleman_liau(self):
        """Calculate Coleman Liau Index."""
        return ColemanLiau(self._statistics).score()
        
    def linsear_write(self):
        """Calculate Linsear Write."""
        return LinsearWrite(self._statistics).score()
        
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

class FleschKincaid:
    def __init__(self, stats, min_words=50):
        self._stats = stats
        if stats.num_words < min_words:
            raise ValueError('50 words required.')

    def score(self):
        score = self._score()
        return Result(
            score=score,
            grade_level=self._grade_level(score)
        )

    def _score(self):
        stats = self._stats
        return (0.38 * stats.avg_words_per_sentence +
                11.8 * stats.avg_syllables_per_word) - 15.59

    def _grade_level(self, score):
        return str(round(score))
        
class LinsearWrite:
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
        num_easy_words = s.num_words - s.num_poly_syllable_words
        num_hard_words = s.num_poly_syllable_words
        inter_score = (num_easy_words + (num_hard_words * 3)) / s.num_sentences
        if inter_score > 20:
            return inter_score / 2
        return (inter_score - 2) / 2

    def _grade_level(self, score):
        return str(round(score))
        
        
class ColemanLiau:
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
        scalar = s.num_words / 100
        letters_per_100_words = s.num_letters / scalar
        sentences_per_100_words = s.num_sentences / scalar
        return 0.0588 * letters_per_100_words - \
            0.296 * sentences_per_100_words - 15.8

    def _grade_level(self, score):
        return str(round(score))
        
class ARI:
    def __init__(self, stats):
        self._stats = stats
        if stats.num_words < 50:
            raise ValueError('50 words required.')

    def score(self):
        score = self._score()
        return Result(
            score=score,
            grade_level=", ".join(self._grade_level(score))),
            #ages=self._ages(score))

    def _score(self):
        s = self._stats
        letters_per_word = s.num_letters / s.num_words
        words_per_sent = s.num_words / s.num_sentences
        return 4.71 * letters_per_word + 0.5 * words_per_sent - 21.43

    def _grade_level(self, score):
        score = math.ceil(score)
        if score <= 1:
            return ['K']
        elif score <= 2:
            return ['1', '2']
        elif score <= 3:
            return ['3']
        elif score <= 4:
            return ['4']
        elif score <= 5:
            return ['5']
        elif score <= 6:
            return ['6']
        elif score <= 7:
            return ['7']
        elif score <= 8:
            return ['8']
        elif score <= 9:
            return ['9']
        elif score <= 10:
            return ['10']
        elif score <= 11:
            return ['11']
        elif score <= 12:
            return ['12']
        elif score <= 13:
            return ['college']
        else:
            return ['college_graduate']

    
