"""test_analyzer.py — ported from ritajs/test/analyzer-tests.js"""
import pytest
from rita.analyzer import Analyzer

a = Analyzer()
a.SILENCE_LTS = True   # suppress LTS log noise during tests


def setup_module():
    pass  # shared Analyzer instance above


# ── analyze-inline / analyzeWord ─────────────────────────────────────────────

def test_analyze_inline():
    data = a.analyze("abandon")
    assert data['phones']    == "ah-b-ae-n-d-ah-n"
    assert data['stresses']  == "0/1/0"
    assert data['syllables'] == "ah/b-ae-n/d-ah-n"


def test_analyze_word():
    data = a.analyze_word("abandon")
    assert data['phones']    == "ah-b-ae-n-d-ah-n"
    assert data['stresses']  == "0/1/0"
    assert data['syllables'] == "ah/b-ae-n/d-ah-n"

    data = a.analyze_word("z")
    assert data['phones']    == "z"
    assert data['stresses']  == "0"
    assert data['syllables'] == "z"

    data = a.analyze_word("cloze")
    assert data['phones']    == "k-l-ow-z"
    assert data['stresses']  == "1"
    assert data['syllables'] == "k-l-ow-z"


# ── analyze ──────────────────────────────────────────────────────────────────

def test_analyze_empty():
    assert a.analyze('') == {'tokens': '', 'pos': '', 'stresses': '',
                              'phones': '', 'syllables': ''}


def test_analyze():
    data = a.analyze("clothes")
    assert data['pos']       == "nns"
    assert data['tokens']    == "clothes"
    assert data['syllables'] == "k-l-ow-dh-z"

    data = a.analyze("abandon")
    assert data['pos']       == "vb"
    assert data['phones']    == "ah-b-ae-n-d-ah-n"
    assert data['tokens']    == "abandon"
    assert data['stresses']  == "0/1/0"
    assert data['syllables'] == "ah/b-ae-n/d-ah-n"

    data = a.analyze("bit")
    assert data['pos']       == "vbd"
    assert data['syllables'] == "b-ih-t"

    data = a.analyze("It bit me.")
    assert data['pos']       == "prp vbd prp ."

    data = a.analyze("Give the duck a bit of bread.")
    assert data['pos']       == "vb dt nn dt nn in nn ."

    data = a.analyze("broke")
    assert data['pos']       == "vbd"
    assert data['syllables'] == "b-r-ow-k"

    data = a.analyze("I broke my leg.")
    assert data['pos']       == "prp vbd prp$ nn ."

    data = a.analyze("The show has ended.")
    assert data['pos']       == "dt nn vbz vbn ."

    data = a.analyze("She oversaw it.")
    assert data['pos']       == "prp vbd prp ."

    data = a.analyze("She remade this video.")
    assert data['pos']       == "prp vbd dt nn ."

    data = a.analyze("She becomes a companion to a foreigner.")
    assert data['pos']       == "prp vbz dt nn to dt nn ."

    data = a.analyze("the clothes")
    assert data['pos']       == "dt nns"
    assert data['tokens']    == "the clothes"
    assert data['syllables'] == "dh-ah k-l-ow-dh-z"

    data = a.analyze("yoyo")
    assert data['pos']       == "nn"
    assert data['tokens']    == "yoyo"
    assert data['syllables'] == "y-ow/y-ow"


# ── phones_to_stress ─────────────────────────────────────────────────────────

def test_phones_to_stress():
    assert a.phones_to_stress(None) is None
    assert a.phones_to_stress(" ") == ""
    assert a.phones_to_stress("ah b-ae1-n d-ah-n") == "0/1/0"


# ── phones ───────────────────────────────────────────────────────────────────

def test_phones():
    assert a.phones("") == ""
    assert a.phones("b") == "b"
    assert a.phones("B") == "b"
    assert a.phones("The") == "dh-ah"
    assert a.phones("The.") == "dh-ah ."
    assert a.phones("flowers") == "f-l-aw-er-z"
    assert a.phones("mice") == "m-ay-s"
    assert a.phones("ant") == "ae-n-t"

    result = a.phones("The boy jumped over the wild dog.")
    assert result == "dh-ah b-oy jh-ah-m-p-t ow-v-er dh-ah w-ay-l-d d-ao-g ."

    result = a.phones("The boy ran to the store.")
    assert result == "dh-ah b-oy r-ae-n t-uw dh-ah s-t-ao-r ."

    assert a.phones("quiche")    == "k-iy-sh"
    assert a.phones("said")      == "s-eh-d"
    assert a.phones("chevrolet") == "sh-eh-v-r-ow-l-ey"
    assert a.phones("women")     == "w-ih-m-eh-n"
    assert a.phones("genuine")   == "jh-eh-n-y-uw-w-ah-n"

    assert a.phones("deforestations") == 'd-ih-f-ao-r-ih-s-t-ey-sh-ah-n-z'
    assert a.phones("schizophrenias") == 's-k-ih-t-s-ah-f-r-iy-n-iy-ah-z'


# ── syllables ────────────────────────────────────────────────────────────────

def test_syllables():
    assert a.syllables('') == ''
    assert a.syllables('clothes') == 'k-l-ow-dh-z'

    for i, word in enumerate(['zero','one','two','three','four','five','six','seven','eight','nine']):
        assert a.syllables(str(i)) == a.syllables(word), f"syllables({i}) vs syllables({word})"

    assert a.syllables('deforestations') == 'd-ih/f-ao/r-ih/s-t-ey/sh-ah-n-z'
    assert a.syllables("chevrolet")      == "sh-eh-v/r-ow/l-ey"
    assert a.syllables("women")          == "w-ih/m-eh-n"
    assert a.syllables("genuine")        == "jh-eh-n/y-uw/w-ah-n"

    inp = 'The emperor had no clothes on.'
    assert a.syllables(inp) == 'dh-ah eh-m/p-er/er hh-ae-d n-ow k-l-ow-dh-z aa-n .'

    inp = 'The dog ran faster than the other dog. But the other dog was prettier.'
    expected = 'dh-ah d-ao-g r-ae-n f-ae/s-t-er dh-ae-n dh-ah ah/dh-er d-ao-g . b-ah-t dh-ah ah/dh-er d-ao-g w-aa-z p-r-ih/t-iy/er .'
    assert a.syllables(inp) == expected


# ── stresses ─────────────────────────────────────────────────────────────────

def test_stresses():
    assert a.stresses("") == ""
    assert a.stresses("women") == "1/0"

    assert a.stresses("The emperor had no clothes on")  == "0 1/0/0 1 1 1 1"
    assert a.stresses("The emperor had no clothes on.") == "0 1/0/0 1 1 1 1 ."

    inp = "The emperor had no clothes on. The King is fat."
    assert a.stresses(inp) == "0 1/0/0 1 1 1 1 . 0 1 1 1 ."

    inp = "The dog ran faster than the other dog.  But the other dog was prettier."
    expected = "0 1 1 1/0 1 0 1/0 1 . 1 0 1/0 1 1 1/0/0 ."
    assert a.stresses(inp) == expected

    # stress-shifted homophones
    assert a.stresses("to present, to export, to decide, to begin") == "1 1/0 , 1 1/0 , 1 0/1 , 1 0/1"
    assert a.stresses("to preSENT, to exPORT, to deCIDE, to beGIN")  == "1 1/0 , 1 1/0 , 1 0/1 , 1 0/1"
    assert a.stresses("chevrolet") == "0/0/1"
    assert a.stresses("genuine")   == "1/0/0"


# ── hyphenated words (single token) ─────────────────────────────────────────

def test_hyphenated_words():
    pool1 = [
        'mother-in-law', 'father-in-law', 'sister-in-law', 'brother-in-law',
        'off-site', 'up-to-date', 'state-of-the-art', 'self-esteem',
        'merry-go-round', 'man-eating', 'twenty-one', 'twenty-first',
        'thirty-second', 'happy-go-lucky', 'editor-in-chief', 'over-the-counter',
        'long-term', 'high-speed', 'in-depth', 'full-length', 'part-time',
        'sun-dried', 'well-off', 'well-known', 'gift-wrap', 'follow-up',
        'well-being', 'good-looking', 'knee-length', 'runner-up', 'tip-off',
        'blush-on', 'sugar-free', 'ice-cold', 'far-flung', 'high-rise',
        'life-size', 'king-size', 'next-door', 'full-time', 'forty-acre',
        'on-campus', 'family-run', 'low-grade', 'round-trip',
    ]
    feats1 = [
        {'pos': 'nn',  'phones': 'm-ah-dh-er-ih-n-l-ao',           'stresses': '1/0-0-1',   'syllables': 'm-ah/dh-er/ih-n/l-ao'},
        {'pos': 'nn',  'phones': 'f-aa-dh-er-ih-n-l-ao',           'stresses': '1/0-0-1',   'syllables': 'f-aa/dh-er/ih-n/l-ao'},
        {'pos': 'nn',  'phones': 's-ih-s-t-er-ih-n-l-ao',          'stresses': '1/0-0-1',   'syllables': 's-ih/s-t-er/ih-n/l-ao'},
        {'pos': 'nn',  'phones': 'b-r-ah-dh-er-ih-n-l-ao',         'stresses': '1/0-0-1',   'syllables': 'b-r-ah/dh-er/ih-n/l-ao'},
        {'pos': 'jj',  'phones': 'ao-f-s-ay-t',                    'stresses': '1-1',        'syllables': 'ao-f/s-ay-t'},
        {'pos': 'jj',  'phones': 'ah-p-t-uw-d-ey-t',               'stresses': '1-1-1',      'syllables': 'ah-p/t-uw/d-ey-t'},
        {'pos': 'nn',  'phones': 's-t-ey-t-ah-v-dh-ah-aa-r-t',     'stresses': '1-1-0-1',   'syllables': 's-t-ey-t/ah-v/dh-ah/aa-r-t'},
        {'pos': 'nn',  'phones': 's-eh-l-f-ah-s-t-iy-m',           'stresses': '1-0/1',      'syllables': 's-eh-l-f/ah/s-t-iy-m'},
        {'pos': 'nn',  'phones': 'm-eh-r-iy-g-ow-r-aw-n-d',        'stresses': '1/0-1-1',   'syllables': 'm-eh/r-iy/g-ow/r-aw-n-d'},
        {'pos': 'jj',  'phones': 'm-ae-n-iy-t-ih-ng',              'stresses': '1-1/0',      'syllables': 'm-ae-n/iy/t-ih-ng'},
        {'pos': 'cd',  'phones': 't-w-eh-n-t-iy-w-ah-n',           'stresses': '1/0-1',      'syllables': 't-w-eh-n/t-iy/w-ah-n'},
        {'pos': 'jj',  'phones': 't-w-eh-n-t-iy-f-er-s-t',         'stresses': '1/0-1',      'syllables': 't-w-eh-n/t-iy/f-er-s-t'},
        {'pos': 'jj',  'phones': 'th-er-t-iy-s-eh-k-ah-n-d',       'stresses': '1/0-1/0',   'syllables': 'th-er/t-iy/s-eh/k-ah-n-d'},
        {'pos': 'jj',  'phones': 'hh-ae-p-iy-g-ow-l-ah-k-iy',      'stresses': '1/0-1-1/0', 'syllables': 'hh-ae/p-iy/g-ow/l-ah/k-iy'},
        {'pos': 'nn',  'phones': 'eh-d-ah-t-er-ih-n-ch-iy-f',      'stresses': '1/0/0-0-1', 'syllables': 'eh/d-ah/t-er/ih-n/ch-iy-f'},
        {'pos': 'jj',  'phones': 'ow-v-er-dh-ah-k-aw-n-t-er',      'stresses': '1/0-0-1/0', 'syllables': 'ow/v-er/dh-ah/k-aw-n/t-er'},
        {'pos': 'jj',  'phones': 'l-ao-ng-t-er-m',                 'stresses': '1-1',        'syllables': 'l-ao-ng/t-er-m'},
        {'pos': 'jj',  'phones': 'hh-ay-s-p-iy-d',                 'stresses': '1-1',        'syllables': 'hh-ay/s-p-iy-d'},
        {'pos': 'jj',  'phones': 'ih-n-d-eh-p-th',                 'stresses': '0-1',        'syllables': 'ih-n/d-eh-p-th'},
        {'pos': 'jj',  'phones': 'f-uh-l-l-eh-ng-k-th',            'stresses': '1-1',        'syllables': 'f-uh-l/l-eh-ng-k-th'},
        {'pos': 'jj',  'phones': 'p-aa-r-t-t-ay-m',                'stresses': '1-1',        'syllables': 'p-aa-r-t/t-ay-m'},
        {'pos': 'jj',  'phones': 's-ah-n-d-r-ay-d',                'stresses': '1-1',        'syllables': 's-ah-n/d-r-ay-d'},
        {'pos': 'jj',  'phones': 'w-eh-l-ao-f',                    'stresses': '1-1',        'syllables': 'w-eh-l/ao-f'},
        {'pos': 'jj',  'phones': 'w-eh-l-n-ow-n',                  'stresses': '1-1',        'syllables': 'w-eh-l/n-ow-n'},
        {'pos': 'nn',  'phones': 'g-ih-f-t-r-ae-p',                'stresses': '1-1',        'syllables': 'g-ih-f-t/r-ae-p'},
        {'pos': 'nn',  'phones': 'f-aa-l-ow-ah-p',                 'stresses': '1/0-1',      'syllables': 'f-aa/l-ow/ah-p'},
        {'pos': 'nn',  'phones': 'w-eh-l-b-iy-ih-ng',              'stresses': '1-1/0',      'syllables': 'w-eh-l/b-iy/ih-ng'},
        {'pos': 'jj',  'phones': 'g-uh-d-l-uh-k-ih-ng',            'stresses': '1-1/0',      'syllables': 'g-uh-d/l-uh/k-ih-ng'},
        {'pos': 'jj',  'phones': 'n-iy-l-eh-ng-k-th',              'stresses': '1-1',        'syllables': 'n-iy/l-eh-ng-k-th'},
        {'pos': 'nn',  'phones': 'r-ah-n-er-ah-p',                 'stresses': '1/0-1',      'syllables': 'r-ah/n-er/ah-p'},
        {'pos': 'nn',  'phones': 't-ih-p-ao-f',                    'stresses': '1-1',        'syllables': 't-ih-p/ao-f'},
        {'pos': 'nn',  'phones': 'b-l-ah-sh-aa-n',                 'stresses': '1-1',        'syllables': 'b-l-ah-sh/aa-n'},
        {'pos': 'jj',  'phones': 'sh-uh-g-er-f-r-iy',              'stresses': '1/0-1',      'syllables': 'sh-uh/g-er/f-r-iy'},
        {'pos': 'jj',  'phones': 'ay-s-k-ow-l-d',                  'stresses': '1-1',        'syllables': 'ay-s/k-ow-l-d'},
        {'pos': 'jj',  'phones': 'f-aa-r-f-l-ah-ng',               'stresses': '1-1',        'syllables': 'f-aa-r/f-l-ah-ng'},
        {'pos': 'nn',  'phones': 'hh-ay-r-ay-z',                   'stresses': '1-1',        'syllables': 'hh-ay/r-ay-z'},
        {'pos': 'jj',  'phones': 'l-ay-f-s-ay-z',                  'stresses': '1-1',        'syllables': 'l-ay-f/s-ay-z'},
        {'pos': 'jj',  'phones': 'k-ih-ng-s-ay-z',                 'stresses': '1-1',        'syllables': 'k-ih-ng/s-ay-z'},
        {'pos': 'jj',  'phones': 'n-eh-k-s-t-d-ao-r',              'stresses': '1-1',        'syllables': 'n-eh-k-s-t/d-ao-r'},
        {'pos': 'jj',  'phones': 'f-uh-l-t-ay-m',                  'stresses': '1-1',        'syllables': 'f-uh-l/t-ay-m'},
        {'pos': 'jj',  'phones': 'f-ao-r-t-iy-ey-k-er',            'stresses': '1/0-1/0',   'syllables': 'f-ao-r/t-iy/ey/k-er'},
        {'pos': 'jj',  'phones': 'aa-n-k-ae-m-p-ah-s',             'stresses': '1-1/0',      'syllables': 'aa-n/k-ae-m/p-ah-s'},
        {'pos': 'jj',  'phones': 'f-ae-m-ah-l-iy-r-ah-n',          'stresses': '1/0/0-1',   'syllables': 'f-ae/m-ah/l-iy/r-ah-n'},
        {'pos': 'jj',  'phones': 'l-ow-g-r-ey-d',                  'stresses': '1-1',        'syllables': 'l-ow/g-r-ey-d'},
        {'pos': 'jj',  'phones': 'r-aw-n-d-t-r-ih-p',              'stresses': '1-1',        'syllables': 'r-aw-n-d/t-r-ih-p'},
    ]
    from rita.tokenizer import Tokenizer
    tok = Tokenizer()
    for i, word in enumerate(pool1):
        feats = a.analyze(word)
        exp = feats1[i]
        assert feats['pos']       == exp['pos'],       f"[pos] fail at {word}: got {feats['pos']}"
        assert feats['tokens']    == word,             f"[tokens] fail at {word}"
        assert feats['phones']    == exp['phones'],    f"[phones] fail at {word}: got {feats['phones']}"
        assert feats['stresses']  == exp['stresses'],  f"[stresses] fail at {word}: got {feats['stresses']}"
        assert feats['syllables'] == exp['syllables'], f"[syllables] fail at {word}: got {feats['syllables']}"
        assert tok.tokenize(word) == feats['tokens'].split()


def test_hyphenated_words_2a():
    """Pool 2A: missing part is a transformation of a dict word."""
    pool2A = [
        'oft-cited', 'deeply-nested', 'empty-handed', 'sergeant-at-arms',
        'left-handed', 'long-haired', 'breath-taking', 'self-centered',
        'single-minded', 'short-tempered', 'one-sided', 'warm-blooded',
        'cold-blooded', 'bell-bottoms', 'corn-fed', 'able-bodied',
    ]
    feats2A = [
        {'pos': 'jj', 'phones': 'ao-f-t-s-ih-t-ah-d',           'stresses': '1-1/0',   'syllables': 'ao-f-t/s-ih/t-ah-d'},
        {'pos': 'jj', 'phones': 'd-iy-p-l-iy-n-eh-s-t-ah-d',    'stresses': '1/0-1/0', 'syllables': 'd-iy-p/l-iy/n-eh/s-t-ah-d'},
        {'pos': 'jj', 'phones': 'eh-m-p-t-iy-hh-ae-n-d-ah-d',   'stresses': '1/0-1/0', 'syllables': 'eh-m-p/t-iy/hh-ae-n/d-ah-d'},
        {'pos': 'nn', 'phones': 's-aa-r-jh-ah-n-t-ae-t-aa-r-m-z','stresses': '1/0-1-1', 'syllables': 's-aa-r/jh-ah-n-t/ae-t/aa-r-m-z'},
        {'pos': 'jj', 'phones': 'l-eh-f-t-hh-ae-n-d-ah-d',      'stresses': '1-1/0',   'syllables': 'l-eh-f-t/hh-ae-n/d-ah-d'},
        {'pos': 'jj', 'phones': 'l-ao-ng-hh-eh-r-d',             'stresses': '1-1',     'syllables': 'l-ao-ng/hh-eh-r-d'},
        {'pos': 'jj', 'phones': 'b-r-eh-th-t-ey-k-ih-ng',        'stresses': '1-1/0',   'syllables': 'b-r-eh-th/t-ey/k-ih-ng'},
        {'pos': 'jj', 'phones': 's-eh-l-f-s-eh-n-t-er-d',        'stresses': '1-1/0',   'syllables': 's-eh-l-f/s-eh-n/t-er-d'},
        {'pos': 'jj', 'phones': 's-ih-ng-g-ah-l-m-ay-n-d-ah-d',  'stresses': '1/0-1/0', 'syllables': 's-ih-ng/g-ah-l/m-ay-n/d-ah-d'},
        {'pos': 'jj', 'phones': 'sh-ao-r-t-t-eh-m-p-er-d',       'stresses': '1-1/0',   'syllables': 'sh-ao-r-t/t-eh-m/p-er-d'},
        {'pos': 'jj', 'phones': 'w-ah-n-s-ay-d-ah-d',            'stresses': '1-1/0',   'syllables': 'w-ah-n/s-ay/d-ah-d'},
        {'pos': 'jj', 'phones': 'w-ao-r-m-b-l-ah-d-ah-d',        'stresses': '1-1/0',   'syllables': 'w-ao-r-m/b-l-ah/d-ah-d'},
        {'pos': 'jj', 'phones': 'k-ow-l-d-b-l-ah-d-ah-d',        'stresses': '1-1/0',   'syllables': 'k-ow-l-d/b-l-ah/d-ah-d'},
        {'pos': 'nn', 'phones': 'b-eh-l-b-aa-t-ah-m-z',          'stresses': '1-1/0',   'syllables': 'b-eh-l/b-aa/t-ah-m-z'},
        {'pos': 'jj', 'phones': 'k-ao-r-n-f-eh-d',               'stresses': '1-1',     'syllables': 'k-ao-r-n/f-eh-d'},
        {'pos': 'jj', 'phones': 'ey-b-ah-l-b-aa-d-iy-d',         'stresses': '1/0-1/0', 'syllables': 'ey/b-ah-l/b-aa/d-iy-d'},
    ]
    from rita.tokenizer import Tokenizer
    tok = Tokenizer()
    for i, word in enumerate(pool2A):
        feats = a.analyze(word)
        exp = feats2A[i]
        assert feats['pos']       == exp['pos'],       f"[pos] fail at {word}: got {feats['pos']}"
        assert feats['tokens']    == word,             f"[tokens] fail at {word}"
        assert feats['phones']    == exp['phones'],    f"[phones] fail at {word}: got {feats['phones']}"
        assert feats['stresses']  == exp['stresses'],  f"[stresses] fail at {word}: got {feats['stresses']}"
        assert feats['syllables'] == exp['syllables'], f"[syllables] fail at {word}: got {feats['syllables']}"
        assert tok.tokenize(word) == feats['tokens'].split()


def test_hyphenated_words_2b():
    """Pool 2B: missing part has no connection to any dict word.
    LTS-related failures for de-emphasize, re-apply, u-turn, x-ray are skipped."""
    lts_skip = {"de-emphasize", "re-apply", "u-turn", "x-ray"}
    pool2B = [
        'ho-hum', 'co-manage', 'co-manager', 'neo-liberalism',
        'a-frame', 'high-tech', 'nitty-gritty',
    ]
    feats2B = {
        'ho-hum':        {'pos': 'uh', 'phones': 'hh-ow-hh-ah-m',                       'stresses': '0-1',      'syllables': 'hh-ow/hh-ah-m'},
        'co-manage':     {'pos': 'vb', 'phones': 'k-ow-m-ae-n-ah-jh',                   'stresses': '0-1/0',    'syllables': 'k-ow/m-ae/n-ah-jh'},
        'co-manager':    {'pos': 'nn', 'phones': 'k-ow-m-ae-n-ah-jh-er',                'stresses': '0-1/0/0',  'syllables': 'k-ow/m-ae/n-ah/jh-er'},
        'neo-liberalism': {'pos': 'nn', 'phones': 'n-iy-ow-l-ih-b-er-ah-l-ih-z-ah-m',   'stresses': '0/0-1/0/0/0/0', 'syllables': 'n-iy/ow/l-ih/b-er/ah/l-ih/z-ah-m'},
        'a-frame':       {'pos': 'nn', 'phones': 'ey-f-r-ey-m',                         'stresses': '1-1',      'syllables': 'ey/f-r-ey-m'},
        'high-tech':     {'pos': 'jj', 'phones': 'hh-ay-t-eh-k',                        'stresses': '1-1',      'syllables': 'hh-ay/t-eh-k'},
        'nitty-gritty':  {'pos': 'nn', 'phones': 'n-ih-t-iy-g-r-ih-t-iy',               'stresses': '1/0-1/0',  'syllables': 'n-ih/t-iy/g-r-ih/t-iy'},
    }
    from rita.tokenizer import Tokenizer
    tok = Tokenizer()
    for word in pool2B:
        feats = a.analyze(word)
        exp = feats2B[word]
        assert feats['pos']       == exp['pos'],       f"[pos] fail at {word}: got {feats['pos']}"
        assert feats['tokens']    == word,             f"[tokens] fail at {word}"
        assert feats['phones']    == exp['phones'],    f"[phones] fail at {word}: got {feats['phones']}"
        assert feats['stresses']  == exp['stresses'],  f"[stresses] fail at {word}: got {feats['stresses']}"
        assert feats['syllables'] == exp['syllables'], f"[syllables] fail at {word}: got {feats['syllables']}"
        assert tok.tokenize(word) == feats['tokens'].split()


def test_hyphenated_words_3():
    """Pool 3: all parts not in dict."""
    pool3 = ["co-op", "roly-poly", "topsy-turvy"]
    feats3 = [
        {'pos': 'nn', 'phones': 'k-ow-ah-p',         'stresses': '0-0',   'syllables': 'k-ow/ah-p'},
        {'pos': 'jj', 'phones': 'r-ow-l-iy-p-aa-l-iy', 'stresses': '1/0-1/0', 'syllables': 'r-ow/l-iy/p-aa/l-iy'},
        {'pos': 'jj', 'phones': 't-aa-p-s-iy-t-er-v-iy', 'stresses': '1/0-1/0', 'syllables': 't-aa-p/s-iy/t-er/v-iy'},
    ]
    from rita.tokenizer import Tokenizer
    tok = Tokenizer()
    for i, word in enumerate(pool3):
        feats = a.analyze(word)
        exp = feats3[i]
        assert feats['pos']       == exp['pos'],       f"[pos] fail at {word}: got {feats['pos']}"
        assert feats['tokens']    == word,             f"[tokens] fail at {word}"
        assert feats['phones']    == exp['phones'],    f"[phones] fail at {word}: got {feats['phones']}"
        assert feats['stresses']  == exp['stresses'],  f"[stresses] fail at {word}: got {feats['stresses']}"
        assert feats['syllables'] == exp['syllables'], f"[syllables] fail at {word}: got {feats['syllables']}"
        assert tok.tokenize(word) == feats['tokens'].split()


# ── handle dashes ────────────────────────────────────────────────────────────

def test_handle_dashes():
    """Port of JS 'Should handle dashes' — github.com/dhowe/rita/issues/176"""
    from rita.tokenizer import Tokenizer
    tok = Tokenizer()

    # U+2012 figure dash
    sentence = "Teaching\u2012the profession has always appealed to me."
    feats = a.analyze(sentence)
    assert feats['pos']    == "vbg \u2012 dt nn vbz rb vbd to prp ."
    assert feats['tokens'] == "Teaching \u2012 the profession has always appealed to me ."
    assert tok.tokenize(sentence) == feats['tokens'].split()

    # U+2013 en-dash
    sentence = "The teacher assigned pages 101\u2013181 for tonight's reading material. "
    feats = a.analyze(sentence)
    assert feats['pos']    == "dt nn vbn nns cd \u2013 cd in nns vbg jj ."
    assert feats['tokens'] == "The teacher assigned pages 101 \u2013 181 for tonight's reading material ."
    assert tok.tokenize(sentence.strip()) == feats['tokens'].split()

    # U+2014 em-dash (1)
    sentence = "Type two hyphens\u2014without a space before, after, or between them."
    feats = a.analyze(sentence)
    assert feats['pos']    == "nn cd nns \u2014 in dt nn in , in , cc in prp ."
    assert feats['tokens'] == "Type two hyphens \u2014 without a space before , after , or between them ."
    assert tok.tokenize(sentence) == feats['tokens'].split()

    # U+2014 em-dash (2)
    sentence = "Phones, hand-held computers, and built-in TVs\u2014each a possible distraction\u2014can lead to a dangerous situation if used while driving."
    feats = a.analyze(sentence)
    assert feats['pos']    == "nns , jj nns , cc jj nnps \u2014 dt dt jj nn \u2014 md vb to dt jj nn in vbn in vbg ."
    assert feats['tokens'] == "Phones , hand-held computers , and built-in TVs \u2014 each a possible distraction \u2014 can lead to a dangerous situation if used while driving ."
    assert tok.tokenize(sentence) == feats['tokens'].split()

    # double-hyphen "--"
    sentence = "He is afraid of two things--spiders and senior prom."
    feats = a.analyze(sentence)
    assert feats['pos']    == "prp vbz jj in cd nns -- nns cc jj nn ."
    assert feats['tokens'] == "He is afraid of two things -- spiders and senior prom ."
    assert tok.tokenize(sentence) == feats['tokens'].split()


# ── phones (raw) ──────────────────────────────────────────────────────────────

def test_phones_raw():
    """Port of JS 'Should call phones(raw)' — phones with rawPhones=True option."""
    opts = {'rawPhones': True}
    assert a.phones("",       opts) == ""
    assert a.phones("b",      opts) == "b"
    assert a.phones("B",      opts) == "b"
    assert a.phones("The",    opts) == "dh-ah"
    assert a.phones("flowers", opts) == "f-l-aw-er-z"
    assert a.phones("mice",   opts) == "m-ay-s"
    assert a.phones("ant",    opts) == "ae-n-t"
    assert a.phones("The.",   opts) == "dh-ah ."

    assert a.phones("The boy jumped over the wild dog.", opts) == \
        "dh-ah b-oy jh-ah-m-p-t ow-v-er dh-ah w-ay-l-d d-ao-g ."
    assert a.phones("The boy ran to the store.", opts) == \
        "dh-ah b-oy r-ae-n t-uw dh-ah s-t-ao-r ."
    assert a.phones("quiche",    opts) == "k-iy-sh"
    assert a.phones("said",      opts) == "s-eh-d"
    assert a.phones("chevrolet", opts) == "sh-eh-v-r-ow-l-ey"
    assert a.phones("women",     opts) == "w-ih-m-eh-n"
    assert a.phones("genuine",   opts) == "jh-eh-n-y-uw-w-ah-n"
    assert a.phones("deforestations", opts) == 'd-ih-f-ao-r-ih-s-t-ey-sh-ah-n-z'
    assert a.phones("schizophrenias",  opts) == 's-k-ih-t-s-ah-f-r-iy-n-iy-ah-z'


# ── compute_phones ────────────────────────────────────────────────────────────

def test_compute_phones():
    assert a.compute_phones("leo") == ["l", "iy", "ow"]
    assert a.compute_phones(None) is None
    assert a.compute_phones(".") is None
    assert a.compute_phones("") is None
    assert a.compute_phones(",") is None
    assert a.compute_phones("leo", {'silent': True}) == ["l", "iy", "ow"]
    assert a.compute_phones("student's") == ["s", "t", "uw1", "d", "eh1", "n", "t", "z"]
    assert a.compute_phones("1") == ['w', 'ah', 'n']
