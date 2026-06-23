"""
test_util.py - Tests for util module (ported from ritajs)

Tests ported from:
- ritajs/test/analyzer-tests.js (syllable/phone tests)
- ritajs/test/rita-tests.js (utility function tests)
"""

import pytest
from util import Util, RE, Phones, Numbers


class TestRE:
    """Test regular expression pattern class"""
    
    def test_applies(self):
        rule = RE(r'.*s$', 1, 'es')
        assert rule.applies('cats')
        assert rule.applies('dogs')
        assert not rule.applies('dog')
        assert not rule.applies('cat')
    
    def test_fire_with_offset(self):
        rule = RE(r'.*s$', 1, 'es')
        assert rule.fire('cats') == 'cates'
        assert rule.fire('dogs') == 'doges'
    
    def test_fire_no_offset(self):
        rule = RE(r'.*', 0, 's')
        assert rule.fire('cat') == 'cats'
        assert rule.fire('dog') == 'dogs'
    
    def test_truncate(self):
        rule = RE(r'.*y$', 1, 'ies')
        assert rule.truncate('happy') == 'happ'
        assert rule.truncate('funny') == 'funn'
        
    def test_truncate_multiple_chars(self):
        rule = RE(r'.*', 3, 'ing')
        assert rule.truncate('running') == 'runn'
        
    def test_no_truncate(self):
        rule_no_offset = RE(r'.*', 0, 's')
        assert rule_no_offset.truncate('cat') == 'cat'


class TestUtilBasics:
    """Test basic utility functions"""
    
    def test_is_num(self):
        # Integers
        assert Util.is_num(42)
        assert Util.is_num(0)
        assert Util.is_num(-5)
        
        # Floats
        assert Util.is_num(3.14)
        assert Util.is_num(-2.5)
        assert Util.is_num(0.0)
        
        # String numbers
        assert Util.is_num('123')
        assert Util.is_num('3.14')
        assert Util.is_num('-42')
        
        # Non-numbers
        assert not Util.is_num('abc')
        assert not Util.is_num('12x')
        assert not Util.is_num(None)
        assert not Util.is_num('')
        assert not Util.is_num([])
        assert not Util.is_num({})
    
    def test_num_opt(self):
        opts = {'temp': 0.5, 'count': 10, 'zero': 0, 'invalid': 'foo'}
        
        assert Util.num_opt(opts, 'temp') == 0.5
        assert Util.num_opt(opts, 'count') == 10
        assert Util.num_opt(opts, 'zero') == 0  # zero is valid
        assert Util.num_opt(opts, 'invalid', 42) == 42
        assert Util.num_opt(opts, 'missing', 99) == 99
        assert Util.num_opt(None, 'any', 7) == 7


class TestSyllables:
    """Test syllable/phoneme operations (from analyzer-tests.js)"""
    
    def test_syllables_to_phones_simple(self):
        """Test single syllable conversion"""
        # "cat" = k-ae1-t
        syllables = [
            [['1'], ['k'], ['ae'], ['t']]
        ]
        result = Util.syllables_to_phones(syllables)
        assert result == 'k-ae1-t'
    
    def test_syllables_to_phones_no_stress(self):
        """Test syllable without stress marker"""
        syllables = [
            [[None], ['k'], ['ae'], ['t']]
        ]
        result = Util.syllables_to_phones(syllables)
        assert result == 'k-ae-t'
    
    def test_syllables_to_phones_multi(self):
        """Test multiple syllables"""
        # Two syllables: "began" = bih-gan
        syllables = [
            [[None], ['b'], ['ih'], []],
            [['1'], ['g'], ['ae'], ['n']]
        ]
        result = Util.syllables_to_phones(syllables)
        assert result == 'b-ih g-ae1-n'
    
    def test_syllables_to_phones_complex_onset(self):
        """Test complex onset (multiple consonants)"""
        # "strong" = s-t-r-ao1-ng
        syllables = [
            [['1'], ['s', 't', 'r'], ['ao'], ['ng']]
        ]
        result = Util.syllables_to_phones(syllables)
        assert result == 's-t-r-ao1-ng'
    
    def test_syllables_to_phones_abandon(self):
        """Test from analyzer-tests.js: 'abandon'"""
        # ah/b-ae-n/d-ah-n
        syllables = [
            [[None], [], ['ah'], []],
            [['1'], ['b'], ['ae'], ['n']],
            [[None], ['d'], ['ah'], ['n']]
        ]
        result = Util.syllables_to_phones(syllables)
        assert result == 'ah b-ae1-n d-ah-n'
    
    def test_syllables_from_phones_simple(self):
        """Test syllabification of simple word"""
        # Single syllable with CVC pattern
        result = Util.syllables_from_phones('k-ae1-t')
        assert 'ae1' in result
        assert 'k' in result
        assert 't' in result
    
    def test_syllables_from_phones_multi_syllable(self):
        """Test syllabification preserves syllable boundaries"""
        # Input already has syllable breaks (spaces)
        result = Util.syllables_from_phones('k-ae1 t-ih-ng')
        syllables = result.split(' ')
        assert len(syllables) == 2
    
    def test_syllables_from_phones_cloze(self):
        """Test from analyzer-tests.js: 'cloze' = k-l-ow-z"""
        result = Util.syllables_from_phones('k-l-ow1-z')
        # Should be single syllable
        assert ' ' not in result or result.count(' ') == 0
        assert 'ow1' in result
    
    def test_syllables_from_phones_clothes(self):
        """Test from analyzer-tests.js: 'clothes' = k-l-ow-dh-z"""
        result = Util.syllables_from_phones('k-l-ow-dh-z')
        # Single syllable
        assert ' ' not in result or result.count(' ') == 0
    
    def test_syllables_from_phones_empty(self):
        """Test empty input"""
        assert Util.syllables_from_phones('') == ''
        assert Util.syllables_from_phones(None) == ''
    
    def test_syllables_from_phones_invalid(self):
        """Test invalid phoneme rejection"""
        with pytest.raises(ValueError, match='Invalid phoneme'):
            Util.syllables_from_phones('k-xx-t')
        
        with pytest.raises(ValueError, match='Invalid phoneme'):
            Util.syllables_from_phones('foo')
    
    def test_syllables_roundtrip(self):
        """Test syllables_to_phones -> syllables_from_phones roundtrip"""
        original_syllables = [
            [['1'], ['k'], ['ae'], ['t']]
        ]
        phones_str = Util.syllables_to_phones(original_syllables)
        reconstructed = Util.syllables_from_phones(phones_str)
        
        # Should contain same phonemes
        assert 'k' in reconstructed
        assert 'ae1' in reconstructed
        assert 't' in reconstructed


class TestPhones:
    """Test phone data structures"""
    
    def test_consonants_coverage(self):
        """Test consonant list has expected phones"""
        consonants = Phones['consonants']
        
        # Common consonants
        assert 'k' in consonants
        assert 't' in consonants
        assert 'p' in consonants
        assert 'b' in consonants
        assert 'd' in consonants
        assert 'g' in consonants
        
        # Fricatives
        assert 'f' in consonants
        assert 'v' in consonants
        assert 's' in consonants
        assert 'z' in consonants
        assert 'sh' in consonants
        assert 'th' in consonants
        assert 'dh' in consonants
        
        # Other
        assert 'm' in consonants
        assert 'n' in consonants
        assert 'ng' in consonants
        assert 'l' in consonants
        assert 'r' in consonants
        
        # Vowels should NOT be in consonants
        assert 'ae' not in consonants
        assert 'iy' not in consonants
    
    def test_vowels_coverage(self):
        """Test vowel list has expected phones"""
        vowels = Phones['vowels']
        
        # Common vowels
        assert 'aa' in vowels
        assert 'ae' in vowels
        assert 'ah' in vowels
        assert 'ao' in vowels
        assert 'eh' in vowels
        assert 'ih' in vowels
        assert 'iy' in vowels
        assert 'ow' in vowels
        assert 'uh' in vowels
        assert 'uw' in vowels
        
        # Diphthongs
        assert 'ay' in vowels
        assert 'aw' in vowels
        assert 'ey' in vowels
        assert 'oy' in vowels
        
        # Consonants should NOT be in vowels
        assert 'k' not in vowels
        assert 't' not in vowels
    
    def test_onsets_simple(self):
        """Test simple onsets"""
        onsets = Phones['onsets']
        
        # Single consonants
        assert 'k' in onsets
        assert 't' in onsets
        assert 'p' in onsets
        assert 'b' in onsets
        
        # Empty onset
        assert '' in onsets
    
    def test_onsets_clusters(self):
        """Test consonant cluster onsets"""
        onsets = Phones['onsets']
        
        # Common clusters
        assert 'k r' in onsets  # "cry"
        assert 's t' in onsets  # "stay"
        assert 's p' in onsets  # "spy"
        assert 'p l' in onsets  # "play"
        assert 's t r' in onsets  # "street"
        assert 's k r' in onsets  # "scream"


class TestNumbers:
    """Test number/word mappings"""
    
    def test_from_words_basics(self):
        """Test word to number conversion"""
        nums = Numbers['fromWords']
        
        assert nums['zero'] == 0
        assert nums['one'] == 1
        assert nums['two'] == 2
        assert nums['three'] == 3
        assert nums['ten'] == 10
        assert nums['twenty'] == 20
        assert nums['ninety'] == 90
    
    def test_from_words_teens(self):
        """Test teen number mappings"""
        nums = Numbers['fromWords']
        
        assert nums['eleven'] == 11
        assert nums['twelve'] == 12
        assert nums['thirteen'] == 13
        assert nums['nineteen'] == 19
    
    def test_to_words_basics(self):
        """Test number to word conversion"""
        words = Numbers['toWords']
        
        assert words[0] == 'zero'
        assert words[1] == 'one'
        assert words[2] == 'two'
        assert words[10] == 'ten'
        assert words[20] == 'twenty'
        assert words[90] == 'ninety'
    
    def test_roundtrip(self):
        """Test fromWords and toWords are consistent"""
        from_words = Numbers['fromWords']
        to_words = Numbers['toWords']
        
        # Test all single-word numbers
        test_words = ['zero', 'one', 'two', 'ten', 'twenty', 'thirty', 
                      'eleven', 'twelve', 'fifteen']
        
        for word in test_words:
            num = from_words[word]
            assert to_words[num] == word
