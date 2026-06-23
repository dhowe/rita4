"""
test_lexicon.py — Tests for rita/lexicon.py
Python port of ritajs/test/lexicon-tests.js
"""
import pytest
import re
from rita.lexicon import Lexicon

lex = Lexicon()


# ── hasWord ───────────────────────────────────────────────────────────────────

def test_has_word():
    for _ in range(10):
        assert lex.has_word(lex.random_word()) is True
    assert lex.has_word("random") is True
    assert lex.has_word("dog") is True
    assert lex.has_word("men") is True
    assert lex.has_word("happily") is True
    assert lex.has_word("play") is True
    assert lex.has_word("plays") is True
    assert lex.has_word("played") is True
    assert lex.has_word("written") is True
    assert lex.has_word("dogs") is True
    assert lex.has_word("oxen") is True
    assert lex.has_word("mice") is True

    assert lex.has_word("dogs", {'noDerivations': True}) is False
    assert lex.has_word("played", {'noDerivations': True}) is False
    assert lex.has_word("cats", {'noDerivations': True}) is False

    # https://github.com/dhowe/rita/issues/139
    assert lex.has_word("bunning") is False
    assert lex.has_word("coyes") is False
    assert lex.has_word("soes") is False
    assert lex.has_word("knews") is False
    assert lex.has_word("fastering") is False
    assert lex.has_word("loosering") is False

    assert lex.has_word("barkness") is False
    assert lex.has_word("horne") is False
    assert lex.has_word("haye") is False

    # https://github.com/dhowe/rita/issues/177
    assert lex.has_word("bites") is True
    assert lex.has_word("bit") is True
    assert lex.has_word("bitted") is False

    assert lex.has_word("breaks") is True
    assert lex.has_word("broke") is True
    assert lex.has_word("brokes") is False
    assert lex.has_word("broked") is False

    assert lex.has_word("concerned") is True
    assert lex.has_word("concerneded") is False
    assert lex.has_word("concerneds") is False

    assert lex.has_word("outpaced") is True
    assert lex.has_word("outpaceded") is False
    assert lex.has_word("outpaceds") is False

    assert lex.has_word("reported") is True
    assert lex.has_word("reporteds") is False
    assert lex.has_word("reporteded") is False

    assert lex.has_word("build") is True
    assert lex.has_word("built") is True

    assert lex.has_word("called") is True
    assert lex.has_word("calleds") is False
    assert lex.has_word("calleded") is False

    assert lex.has_word("commits") is True
    assert lex.has_word("committed") is True
    assert lex.has_word("committeds") is False
    assert lex.has_word("committeded") is False

    assert lex.has_word("computerized") is True
    assert lex.has_word("computerizeds") is False
    assert lex.has_word("computerizeded") is False

    assert lex.has_word("gets") is True
    assert lex.has_word("got") is True
    assert lex.has_word("gots") is False
    assert lex.has_word("gotten") is True

    assert lex.has_word("leads") is True
    assert lex.has_word("led") is True
    assert lex.has_word("leds") is False

    assert lex.has_word("oversaw") is True
    assert lex.has_word("overseen") is True
    assert lex.has_word("oversaws") is False
    assert lex.has_word("overseened") is False

    assert lex.has_word("remakes") is True
    assert lex.has_word("remade") is True
    assert lex.has_word("remaded") is False

    assert lex.has_word("discriminates") is True
    assert lex.has_word("discriminated") is True
    assert lex.has_word("discriminateds") is False

    assert lex.has_word("launched") is True
    assert lex.has_word("launcheds") is False
    assert lex.has_word("launcheded") is False

    assert lex.has_word("starts") is True
    assert lex.has_word("started") is True
    assert lex.has_word("starteds") is False


# ── randomWord ────────────────────────────────────────────────────────────────

def test_random_word():
    result = lex.random_word()
    assert len(result) > 0
    assert result != lex.random_word(), f"randomWord returned same result '{result}'"

    result = lex.random_word({'numSyllables': 3})
    assert len(result) > 0, f"3 syllables: {result}"

    result = lex.random_word({'numSyllables': 5})
    assert len(result) > 0, f"5 syllables: {result}"


def test_random_word_regex():
    result = lex.random_word('^a')
    assert re.match(r'^a', result)
    assert len(result) > 3

    result = lex.random_word("^apple$")
    assert result == "apple"

    result = lex.random_word("le")
    assert "le" in result

    results = [lex.random_word("^a") for _ in range(10)]
    assert len(results) == 10
    assert len(set(results)) > 1  # not all same

    result = lex.random_word(re.compile(r'^a'))
    assert re.match(r'^a', result)
    assert len(result) > 3

    result = lex.random_word(re.compile(r'^apple$'))
    assert result == "apple"

    result = lex.random_word(re.compile(r'le'))
    assert "le" in result


def test_random_word_stress_regex():
    result = lex.random_word("0/1/0", {'type': 'stresses'})
    assert len(result) > 3
    assert "0/1/0" in lex._get_analyzer().analyze(result)['stresses']

    result = lex.random_word("^0/1/0$", {'type': 'stresses'})
    assert lex._get_analyzer().analyze(result)['stresses'] == "0/1/0"

    result = lex.random_word("010", {'type': 'stresses'})
    assert "0/1/0" in lex._get_analyzer().analyze(result)['stresses']

    result = lex.random_word("^010$", {'type': 'stresses'})
    assert lex._get_analyzer().analyze(result)['stresses'] == "0/1/0"

    result = lex.random_word(re.compile(r'0/1/0'), {'type': 'stresses'})
    assert "0/1/0" in lex._get_analyzer().analyze(result)['stresses']

    result = lex.random_word(re.compile(r'^0/1/0/0$'), {'type': 'stresses'})
    assert lex._get_analyzer().analyze(result)['stresses'] == "0/1/0/0"


def test_random_word_phones_regex():
    result = lex.random_word("^th", {'type': 'phones'})
    assert len(result) > 3
    assert re.match(r'^th', lex._get_analyzer().analyze(result)['phones'])

    result = lex.random_word("v$", {'type': 'phones'})
    assert re.search(r'v$', lex._get_analyzer().analyze(result)['phones'])

    result = lex.random_word("^b-ih-l-iy-v$", {'type': 'phones'})
    assert result == "believe"

    result = lex.random_word("ae", {'type': 'phones'})
    assert "ae" in lex._get_analyzer().analyze(result)['phones']

    result = lex.random_word(re.compile(r'^th'), {'type': 'phones'})
    assert len(result) > 3
    assert re.match(r'^th', lex._get_analyzer().analyze(result)['phones'])

    result = lex.random_word(re.compile(r'v$'), {'type': 'phones'})
    assert re.search(r'v$', lex._get_analyzer().analyze(result)['phones'])

    result = lex.random_word(re.compile(r'^b-ih-l-iy-v$'), {'type': 'phones'})
    assert result == "believe"

    result = lex.random_word(re.compile(r'ae'), {'type': 'phones'})
    assert "ae" in lex._get_analyzer().analyze(result)['phones']


def test_random_word_opts_regex():
    result = lex.random_word({'regex': '^a'})
    assert re.match(r'^a', result)
    assert len(result) > 3

    result = lex.random_word({'regex': re.compile(r'^a')})
    assert re.match(r'^a', result)
    assert len(result) > 3

    result = lex.random_word({'regex': "0/1/0", 'type': 'stresses'})
    assert len(result) > 3
    assert "0/1/0" in lex._get_analyzer().analyze(result)['stresses']

    result = lex.random_word({'regex': re.compile(r'0/1/0'), 'type': 'stresses'})
    assert "0/1/0" in lex._get_analyzer().analyze(result)['stresses']

    result = lex.random_word({'regex': "^th", 'type': 'phones'})
    assert len(result) > 3
    assert re.match(r'^th', lex._get_analyzer().analyze(result)['phones'])

    result = lex.random_word({'regex': re.compile(r'^th'), 'type': 'phones'})
    assert len(result) > 3
    assert re.match(r'^th', lex._get_analyzer().analyze(result)['phones'])


def test_augmented_lexicon():
    to_add = {
        'deg': ['d-eh1-g', 'nn'],
        'wadly': ['w-ae1-d l-iy', 'rb'],
    }
    orig_data = lex._data
    for w, v in to_add.items():
        lex._get_dict()[w] = v

    assert lex.has_word("run")
    assert lex.has_word("walk")
    assert lex.has_word("deg")
    assert lex.has_word("wadly")
    assert lex.is_alliteration("wadly", "welcome")

    for w in to_add:
        del lex._get_dict()[w]


def test_custom_lexicon():
    custom = {
        'dog':     ['d-ao1-g', 'nn'],
        'cat':     ['k-ae1-t', 'nn'],
        'happily': ['hh-ae1 p-ah l-iy', 'rb'],
        'walk':    ['w-ao1-k', 'vb vbp nn'],
        'welcome': ['w-eh1-l k-ah-m', 'jj nn vb vbp'],
        'sadly':   ['s-ae1-d l-iy', 'rb'],
    }
    clex = Lexicon(data=custom)
    assert clex.has_word("run") is False
    assert clex.has_word("walk") is True
    assert clex.is_alliteration("walk", "welcome") is True


def test_random_word_pos():
    with pytest.raises(Exception):
        lex.random_word({'pos': 'xxx'})

    for pos in ["nn", "jj", "jjr", "wp"]:
        result = lex.random_word({'pos': pos})
        best = lex._get_tagger().all_tags(result)[0]
        assert pos == best, f"{result}: expected {pos}, got {best}"

    result = lex.random_word({'pos': 'v'})
    assert len(result) > 0

    result = lex.random_word({'pos': 'nn'})
    assert len(result) > 0

    result = lex.random_word({'pos': 'nns'})
    assert len(result) > 0

    result = lex.random_word({'pos': 'n'})
    assert len(result) > 0

    result = lex.random_word({'pos': 'rp'})
    assert len(result) > 0

    results = [lex.random_word({'pos': 'nns'}) for _ in range(10)]
    assert len(results) == 10
    assert len(set(results)) > 1


def test_random_word_syllables():
    result = lex.random_word({'numSyllables': 3})
    syllables = lex._get_analyzer().syllables(result)
    num = len(syllables.split('/'))
    assert len(result) > 0, f'failed on: {result}'
    assert num == 3, f"{result}: {syllables}"

    result = lex.random_word({'numSyllables': 5})
    syllables = lex._get_analyzer().syllables(result)
    num = len(syllables.split('/'))
    assert len(result) > 0, f'failed on: {result}'
    assert num == 5, f"{result}: {syllables}"


# ── search ────────────────────────────────────────────────────────────────────

def test_search_no_regex():
    assert len(lex.search_sync()) > 20000

    assert len(lex.search_sync({'limit': 11})) == 11

    assert lex.search_sync({'pos': 'n'}) == [
        'abalone', 'abandonment', 'abbey', 'abbot',
        'abbreviation', 'abdomen', 'abduction', 'aberration',
        'ability', 'abnormality'
    ]

    assert lex.search_sync({'numSyllables': 2}) == [
        'abashed', 'abate', 'abbey', 'abbot', 'abduct',
        'abet', 'abhor', 'abide', 'abject', 'ablaze',
    ]

    assert lex.search_sync({'numSyllables': 2, 'pos': 'n'}) == [
        'abbey', 'abbot', 'abode', 'abscess',
        'absence', 'abstract', 'abuse', 'abyss',
        'accent', 'access'
    ]

    assert lex.search_sync({'numSyllables': 1, 'pos': 'n'}) == [
        'ace', 'ache', 'act', 'age',
        'aid', 'aide', 'aim', 'air',
        'aisle', 'ale'
    ]

    search = lex.search_sync({'pos': 'vb', 'limit': -1})
    assert 'concerned' not in search
    assert 'committed' not in search
    assert 'called' not in search
    assert 'computerized' not in search

    search = lex.search_sync({'pos': 'vbd', 'limit': -1})
    assert 'concerned' in search
    assert 'committed' in search
    assert 'called' in search
    assert 'computerized' in search

    search = lex.search_sync({'pos': 'vbn', 'limit': -1})
    assert 'concerned' in search
    assert 'committed' in search
    assert 'called' in search
    assert 'computerized' in search


def test_search_letters():
    expected = ['elephant', 'elephantine', 'phantom', 'sycophantic', 'triumphant', 'triumphantly']
    assert lex.search_sync('phant') == expected
    assert lex.search_sync(re.compile(r'phant')) == expected
    assert lex.search_sync({'regex': 'phant'}) == expected
    assert lex.search_sync({'regex': re.compile(r'phant')}) == expected


def test_search_phones_limit():
    result = lex.search_sync(re.compile(r'f-a[eh]-n-t'), {'type': 'phones', 'limit': 10})
    assert result == [
        "elephant", "elephantine", "fantasia", "fantasize", "fantastic",
        "fantastically", "fantasy", "infant", "infantile", "infantry"
    ]

    result = lex.search_sync('f-ah-n-t', {'type': 'phones', 'limit': 5})
    assert result == ['elephant', 'infant', 'infantile', 'infantry', 'oftentimes']

    result = lex.search_sync({'regex': re.compile(r'f-a[eh]-n-t'), 'type': 'phones', 'limit': 10})
    assert result == [
        "elephant", "elephantine", "fantasia", "fantasize", "fantastic",
        "fantastically", "fantasy", "infant", "infantile", "infantry"
    ]


def test_search_phones_no_limit():
    result = lex.search_sync({'regex': 'f-ah-n-t', 'type': 'phones', 'limit': -1})
    assert result == [
        'elephant', 'infant', 'infantile', 'infantry',
        'oftentimes', 'triumphant', 'triumphantly'
    ]

    result2 = lex.search_sync({'regex': 'f-ah-n-t', 'type': 'phones', 'limit': -1, 'shuffle': True})
    assert sorted(result2) == result


def test_search_pos_phones_sylls_limit():
    res = lex.search_sync('f-ah-n-t', {'type': 'phones', 'pos': 'n', 'limit': 3, 'numSyllables': 2})
    assert res == ['infant']


def test_search_pos_phones_limit():
    res = lex.search_sync('f-ah-n-t', {'type': 'phones', 'pos': 'n', 'limit': 3})
    assert res == ['elephant', 'infant', 'infantry']

    res = lex.search_sync(re.compile(r'f-a[eh]-n-t'), {'type': 'phones', 'pos': 'v', 'limit': 5})
    assert res == ['fantasize']


def test_search_pos_regex():
    res = lex.search_sync(re.compile(r'cares$'), {'pos': 'nns', 'limit': -1})
    assert res == ['cares', 'scares']

    res = lex.search_sync(re.compile(r'^rice$'), {'pos': 'nns', 'limit': -1})
    assert res == ['rice']


def test_search_pos_letters():
    res = lex.search_sync('cause', {'pos': 'nns'})
    assert res == ['causes', 'causeways']

    res = lex.search_sync('gain', {'pos': 'vbd', 'numSyllables': 1})
    assert res == ['gained']

    res = lex.search_sync('end', {'pos': 'vbd', 'minLength': 2, 'limit': -1})
    assert 'ended' in res

    res = lex.search_sync('commit', {'pos': 'vbd'})
    assert 'committed' in res

    res = lex.search_sync('involve', {'pos': 'vbd'})
    assert 'involved' in res

    res = lex.search_sync('outpace', {'pos': 'vbn'})
    assert res == ['outpaced']

    res = lex.search_sync('paid', {'pos': 'vbd'})
    assert 'prepaid' in res

    res = lex.search_sync('made', {'pos': 'vbd'})
    assert 'remade' in res

    res = lex.search_sync('re', {'pos': 'vbd', 'limit': -1})
    assert 'reopened' in res
    assert 'resold' in res


def test_search_simple_pos_phones_limit():
    assert lex.search_sync(re.compile(r'f-a[eh]-n-t'), {'type': 'phones', 'pos': 'vb', 'limit': 5}) == ['fantasize']
    assert lex.search_sync('f-ah-n-t', {'type': 'phones', 'pos': 'nns', 'limit': 3}) == ['elephants', 'infants', 'infantries']


def test_search_pos_stress_limit():
    assert lex.search_sync('010', {'type': 'stresses', 'limit': 5, 'pos': 'n'}) == [
        'abalone', 'abandonment', 'abbreviation', 'abdomen', 'abduction'
    ]
    assert lex.search_sync('010', {'type': 'stresses', 'limit': 5, 'pos': 'n', 'numSyllables': 3}) == [
        'abdomen', 'abduction', 'abortion', 'abruptness', 'absorber'
    ]
    assert lex.search_sync('010', {'type': 'stresses', 'limit': 5, 'pos': 'nns'}) == [
        'abalone', 'abandonments', 'abbreviations', 'abductions', 'abilities'
    ]
    assert lex.search_sync(re.compile(r'0/1/0'), {'type': 'stresses', 'limit': 5, 'pos': 'nns'}) == [
        'abalone', 'abandonments', 'abbreviations', 'abductions', 'abilities'
    ]
    assert lex.search_sync('010', {'type': 'stresses', 'limit': 5, 'pos': 'nns', 'numSyllables': 3}) == [
        'abductions', 'abortions', 'absorbers', 'abstentions', 'abstractions'
    ]


def test_search_stresses_limit():
    assert lex.search_sync('010000', {'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]
    assert lex.search_sync('010000', {'type': 'stresses', 'limit': 5, 'maxLength': 11}) == [
        'colonialism', 'imperialism', 'materialism'
    ]
    assert lex.search_sync('010000', {'type': 'stresses', 'limit': 5, 'minLength': 12}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'conciliatory'
    ]
    assert lex.search_sync('0/1/0/0/0/0', {'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]
    assert lex.search_sync({'regex': '010000', 'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]
    assert lex.search_sync({'regex': '010000', 'type': 'stresses', 'limit': 5, 'maxLength': 11}) == [
        'colonialism', 'imperialism', 'materialism'
    ]
    assert lex.search_sync({'regex': '010000', 'type': 'stresses', 'limit': 5, 'minLength': 12}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'conciliatory'
    ]
    assert lex.search_sync({'regex': '0/1/0/0/0/0', 'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]


def test_search_stress_regex_limit():
    assert lex.search_sync(re.compile(r'0/1/0/0/0/0'), {'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]
    assert lex.search_sync({'regex': re.compile(r'0/1/0/0/0/0'), 'type': 'stresses', 'limit': 5}) == [
        'accountability', 'anticipatory', 'appreciatively', 'authoritarianism', 'colonialism'
    ]


# ── rhymes ────────────────────────────────────────────────────────────────────

def test_rhymes_sync():
    assert lex.rhymes_sync('dog', {'limit': 1}) == ['cog']
    assert lex.rhymes_sync('dog', {'limit': 2}) == ['cog', 'log']
    assert lex.rhymes_sync('dog') == ['cog', 'log']


def test_rhymes():
    assert len(lex.rhymes('cat')) == 10
    assert 'hat' in lex.rhymes('cat')
    assert 'mellow' in lex.rhymes('yellow')
    assert 'boy' in lex.rhymes('toy')
    assert 'drab' in lex.rhymes('crab')

    assert 'house' in lex.rhymes('mouse')
    assert 'polo' not in lex.rhymes('apple')
    assert 'these' not in lex.rhymes('this')

    assert 'house' not in lex.rhymes('hose')
    assert 'mellow' not in lex.rhymes('sieve')
    assert 'grab' not in lex.rhymes('swag')

    assert 'eight' in lex.rhymes('weight', {'limit': 1000})
    assert 'weight' in lex.rhymes('eight', {'limit': 1000})
    assert 'give' in lex.rhymes('sieve', {'limit': 1000})
    assert 'more' in lex.rhymes('shore', {'limit': 1000})
    assert 'sense' in lex.rhymes('tense', {'limit': 1000})

    assert 'fog' in lex.rhymes('bog')
    assert 'log' in lex.rhymes('dog')

    assert lex.rhymes('a') == []
    assert lex.rhymes('I') == []
    assert lex.rhymes('Z') == []
    assert lex.rhymes('B') == []
    assert lex.rhymes('K') == []


def test_rhymes_pos():
    assert 'hat' not in lex.rhymes('cat', {'pos': 'v'})
    assert 'mellow' in lex.rhymes('yellow', {'pos': 'a'})
    assert 'boy' in lex.rhymes('toy', {'pos': 'n'})
    assert 'give' not in lex.rhymes('sieve', {'pos': 'n'})

    assert 'condense' in lex.rhymes('tense', {'pos': 'v'})
    assert 'drab' not in lex.rhymes('crab', {'pos': 'n'})
    assert 'more' not in lex.rhymes('shore', {'pos': 'v'})

    assert 'house' in lex.rhymes('mouse', {'pos': 'nn'})

    assert 'eight' not in lex.rhymes('weight', {'pos': 'vb'})
    assert 'weight' in lex.rhymes('eight', {'pos': 'nn', 'limit': 1000})

    assert 'polo' not in lex.rhymes('apple', {'pos': 'v'})
    assert 'these' not in lex.rhymes('this', {'pos': 'v'})

    assert 'house' not in lex.rhymes('hose', {'pos': 'v'})
    assert 'mellow' not in lex.rhymes('sieve', {'pos': 'v'})
    assert 'grab' not in lex.rhymes('swag', {'pos': 'v'})

    rhyme = lex.rhymes('spreads', {'pos': 'vbz', 'limit': 1000})
    for bad in ['discriminateds', 'endeds', 'finisheds', 'reporteds', 'proliferateds', 'outpaceds', 'liveds']:
        assert bad not in rhyme

    assert 'bit' not in lex.rhymes('hit', {'pos': 'vb'})
    assert 'bit' in lex.rhymes('hit', {'pos': 'vbd'})
    assert 'broke' not in lex.rhymes('stroke', {'pos': 'vb'})
    assert 'broke' in lex.rhymes('stroke', {'pos': 'vbd'})
    assert 'involved' not in lex.rhymes('evolved', {'pos': 'vb'})
    assert 'involved' in lex.rhymes('evolved', {'pos': 'vbd'})


def test_rhymes_pos_nid():
    rhymes = lex.rhymes('abated', {'pos': 'vbd', 'limit': 1000})
    assert 'allocated' in rhymes
    assert 'annihilated' in rhymes
    assert 'condensed' not in rhymes


def test_rhymes_num_syllables():
    assert 'hat' in lex.rhymes('cat', {'numSyllables': 1})
    assert 'hat' not in lex.rhymes('cat', {'numSyllables': 2})
    assert 'hat' not in lex.rhymes('cat', {'numSyllables': 3})

    assert 'mellow' in lex.rhymes('yellow', {'numSyllables': 2})
    assert 'mellow' not in lex.rhymes('yellow', {'numSyllables': 3})

    rhymes = lex.rhymes('abated', {'numSyllables': 3})
    assert 'elated' in rhymes
    assert 'abated' not in rhymes
    assert 'allocated' not in rhymes
    assert 'condensed' not in rhymes


def test_rhymes_wordlength():
    assert 'hat' not in lex.rhymes('cat', {'minLength': 4})
    assert 'hat' not in lex.rhymes('cat', {'maxLength': 2})

    rhymes = lex.rhymes('abated', {'pos': 'vbd', 'maxLength': 9})
    assert 'allocated' in rhymes
    assert 'annihilated' not in rhymes
    assert 'condensed' not in rhymes


# ── spellsLike ────────────────────────────────────────────────────────────────

def test_spells_like():
    assert lex.spells_like("") == []
    assert lex.spells_like("banana") == ["banal", "bonanza", "cabana", "manna"]
    assert lex.spells_like("tornado") == ["torpedo"]
    assert lex.spells_like("ice") == [
        'ace', 'dice', 'iced', 'icy', 'ire', 'lice', 'nice', 'rice', 'vice'
    ]


def test_spells_like_options():
    assert lex.spells_like("banana", {'minLength': 6, 'maxLength': 6}) == ["cabana"]

    result = lex.spells_like("banana", {'minDistance': 1})
    assert result == ["banal", "bonanza", "cabana", "manna"]

    result = lex.spells_like("ice", {'maxLength': 3})
    assert result == ['ace', 'icy', 'ire']

    result = lex.spells_like("ice", {'minDistance': 2, 'minLength': 3, 'maxLength': 3, 'limit': 1000})
    for r in result:
        assert len(r) == 3
    assert len(result) > 10

    result = lex.spells_like("ice", {'minDistance': 0, 'minLength': 3, 'maxLength': 3})
    assert result == ["ace", "icy", "ire"]

    result = lex.spells_like("ice", {'minLength': 3, 'maxLength': 3})
    for r in result:
        assert len(r) == 3
    assert result == ["ace", "icy", "ire"]

    result = lex.spells_like("ice", {'minLength': 3, 'maxLength': 3, 'pos': 'n'})
    for r in result:
        assert len(r) == 3
    assert result == ["ace", "ire"]

    result = lex.spells_like("ice", {'minLength': 4, 'maxLength': 4, 'pos': 'v', 'limit': 5})
    for r in result:
        assert len(r) == 4
    assert result == ['ache', 'bide', 'bite', 'cite', 'dine']

    result = lex.spells_like("ice", {'minLength': 4, 'maxLength': 4, 'pos': 'nns', 'limit': 5})
    for r in result:
        assert len(r) == 4
    assert result == ['dice', 'rice']

    result = lex.spells_like("ice", {'minLength': 4, 'maxLength': 4, 'pos': 'nns', 'minDistance': 3, 'limit': 5})
    for r in result:
        assert len(r) == 4
    assert result == ['axes', 'beef', 'deer', 'dibs', 'fame']

    result = lex.spells_like("abated", {'pos': 'vbd'})
    assert 'abetted' in result
    assert 'aborted' in result
    assert 'condensed' not in result

    assert 'lived' not in lex.spells_like("lined", {'pos': 'vb'})
    assert 'lived' in lex.spells_like("lined", {'pos': 'vbd'})
    assert 'led' not in lex.spells_like("let", {'pos': 'vb'})
    assert 'led' in lex.spells_like("let", {'pos': 'vbd'})
    assert 'broke' not in lex.spells_like("brake", {'pos': 'vb'})
    assert 'broke' in lex.spells_like("brake", {'pos': 'vbd'})
    assert 'oversaw' not in lex.spells_like("overseas", {'pos': 'vb'})
    assert 'oversaw' in lex.spells_like("overseas", {'pos': 'vbd'})

    rhyme = lex.spells_like("spreads", {'pos': 'vbz', 'limit': 1000})
    for bad in ['discriminateds', 'endeds', 'finisheds', 'reporteds', 'proliferateds', 'outpaceds', 'lived']:
        assert bad not in rhyme


# ── soundsLike ────────────────────────────────────────────────────────────────

def test_sounds_like():
    assert lex.sounds_like("tornado", {'type': 'sound'}) == ["torpedo"]

    result = lex.sounds_like("try", {'limit': 20})
    answer = ["cry", "dry", "fry", "pry", "rye", "tie", "tray", "tree",
              "tribe", "tried", "tripe", "trite", "true", "wry"]
    assert result == answer

    result = lex.sounds_like("try", {'minDistance': 2, 'limit': 20})
    assert len(result) > len(answer)

    result = lex.sounds_like("happy")
    assert result == ["happier", "hippie"]

    result = lex.sounds_like("happy", {'minDistance': 2})
    assert len(result) > 2  # more

    result = lex.sounds_like("cat", {'type': 'sound'})
    assert result == [
        'bat', 'cab', 'cache', 'calf', 'calve', 'can',
        "can't", 'cap', 'cash', 'cast'
    ]

    result = lex.sounds_like("cat", {'type': 'sound', 'limit': 5})
    assert result == ['bat', 'cab', 'cache', 'calf', 'calve']

    result = lex.sounds_like("cat", {'type': 'sound', 'limit': 1000, 'minLength': 2, 'maxLength': 4})
    assert result == ["at", "bat", "cab", "calf", "can", "cap", "cash", "cast",
                      "chat", "coat", "cot", "curt", "cut", "fat", "hat", "kit",
                      "kite", "mat", "matt", "pat", "rat", "sat", "that", "vat"]

    result = lex.sounds_like("cat", {'type': 'sound', 'minLength': 4, 'maxLength': 5, 'pos': 'jj'})
    assert result == ['catty', 'curt']

    result = lex.sounds_like("cat", {'minDistance': 2})
    assert len(result) > 2


def test_sounds_like_pos():
    result = lex.sounds_like("abated", {'pos': 'vbd'})
    assert 'abetted' in result
    assert 'debated' in result
    assert 'condensed' not in result

    assert 'built' not in lex.sounds_like("build", {'pos': 'vb', 'limit': 1000})
    assert 'computerized' not in lex.sounds_like("computerize", {'pos': 'vb', 'limit': 1000})
    assert 'concerned' not in lex.sounds_like("concern", {'pos': 'vb'})
    assert 'committed' not in lex.sounds_like("commit", {'pos': 'vb'})
    assert 'involved' not in lex.sounds_like("involve", {'pos': 'vb'})
    assert 'gained' not in lex.sounds_like("grained", {'pos': 'vb'})

    assert 'remade' in lex.sounds_like("premade", {'pos': 'vbd'})
    assert 'discriminated' in lex.sounds_like("incriminate", {'pos': 'vbd'})
    assert 'pinched' in lex.sounds_like("paunched", {'pos': 'vbd'})


def test_sounds_like_match_spelling():
    result = lex.sounds_like("try", {'matchSpelling': True})
    assert result == ['cry', 'dry', 'fry', 'pry', 'tray']

    result = lex.sounds_like("try", {'matchSpelling': True, 'maxLength': 3})
    assert result == ["cry", "dry", "fry", "pry", "wry"]

    result = lex.sounds_like("try", {'matchSpelling': True, 'minLength': 4})
    assert result == ["tray"]

    result = lex.sounds_like("try", {'matchSpelling': True, 'limit': 3})
    assert result == ["cry", "dry", "fry"]

    result = lex.sounds_like("daddy", {'matchSpelling': True})
    assert result == ["dandy", "paddy"]

    result = lex.sounds_like("banana", {'matchSpelling': True})
    assert result == ["bonanza"]

    result = lex.sounds_like("abated", {'pos': 'vbd', 'matchSpelling': True})
    assert len(result) == 2
    assert 'abetted' in result
    assert 'awaited' in result


# ── isRhyme ───────────────────────────────────────────────────────────────────

def test_is_rhyme():
    assert not lex.is_rhyme("apple", "polo")
    assert not lex.is_rhyme("this", "these")

    assert lex.is_rhyme("cat", "hat")
    assert lex.is_rhyme("yellow", "mellow")
    assert lex.is_rhyme("toy", "boy")

    assert lex.is_rhyme("solo", "tomorrow")
    assert lex.is_rhyme("tense", "sense")
    assert lex.is_rhyme("crab", "drab")
    assert lex.is_rhyme("shore", "more")
    assert not lex.is_rhyme("hose", "house")
    assert not lex.is_rhyme("sieve", "mellow")

    assert lex.is_rhyme("mouse", "house")

    assert lex.is_rhyme("yo", "bro")
    assert not lex.is_rhyme("swag", "grab")
    assert not lex.is_rhyme("", "")

    assert lex.is_rhyme("weight", "eight")
    assert lex.is_rhyme("eight", "weight")

    assert lex.is_rhyme("abated", "debated")


# ── isAlliteration ────────────────────────────────────────────────────────────

def test_is_alliteration():
    assert lex.is_alliteration("knife", "gnat")
    assert lex.is_alliteration("knife", "naughty")

    assert lex.is_alliteration("sally", "silly")
    assert lex.is_alliteration("sea", "seven")
    assert lex.is_alliteration("silly", "seven")
    assert lex.is_alliteration("sea", "sally")

    assert lex.is_alliteration("big", "bad")
    assert lex.is_alliteration("bad", "big")

    assert lex.is_alliteration("BIG", "bad")
    assert lex.is_alliteration("big", "BAD")
    assert lex.is_alliteration("BIG", "BAD")

    assert not lex.is_alliteration("", "")
    assert not lex.is_alliteration("wind", "withdraw")
    assert not lex.is_alliteration("solo", "tomorrow")
    assert not lex.is_alliteration("solo", "yoyo")
    assert not lex.is_alliteration("yoyo", "jojo")
    assert not lex.is_alliteration("cat", "access")

    assert lex.is_alliteration("unsung", "sine")
    assert lex.is_alliteration("job", "gene")
    assert lex.is_alliteration("jeans", "gentle")

    assert lex.is_alliteration("abet", "better")
    assert lex.is_alliteration("never", "knight")
    assert lex.is_alliteration("knight", "navel")
    assert lex.is_alliteration("cat", "kitchen")

    assert not lex.is_alliteration("octopus", "oblong")
    assert not lex.is_alliteration("omen", "open")
    assert not lex.is_alliteration("amicable", "atmosphere")

    assert lex.is_alliteration("abated", "abetted")


# ── _toPhoneArray (private) ───────────────────────────────────────────────────

def test_to_phone_array():
    raw = lex.raw_phones("tornado")
    result = lex._to_phone_array(raw)
    assert result == ["t", "ao", "r", "n", "ey", "d", "ow"]


# ── randomWord.pos.syls ───────────────────────────────────────────────────────

def test_random_word_pos_syls():
    from rita.rita import RiTa

    result = lex.random_word({'numSyllables': 3, 'pos': 'vbz'})
    assert len(result) > 0
    syllables = RiTa.syllables(result)
    assert len(syllables.split('/')) == 3, f"GOT: {result} ({syllables})"
    assert RiTa.is_verb(result), f"Expected verb, got: {result}"

    result = lex.random_word({'numSyllables': 1, 'pos': 'n'})
    assert len(result) > 0
    syllables = RiTa.syllables(result)
    assert len(syllables.split('/')) == 1, f"GOT: {result} ({syllables})"
    assert RiTa.is_noun(result), f"Expected noun, got: {result}"

    result = lex.random_word({'numSyllables': 1, 'pos': 'nns'})
    assert len(result) > 0
    syllables = RiTa.syllables(result)
    assert len(syllables.split('/')) == 1, f"GOT: {result} ({syllables})"
    assert RiTa.is_noun(result), f"Expected noun, got: {result}"

    result = lex.random_word({'numSyllables': 5, 'pos': 'nns'})
    assert len(result) > 0
    assert RiTa.is_noun(result), f"Expected noun, got: {result}"


# ── alliterations ─────────────────────────────────────────────────────────────

def test_alliterations_num_syllables():
    result = lex.alliterations_sync("cat", {'minLength': 1, 'numSyllables': 7})
    assert result == ['electrocardiogram', 'electromechanical', 'telecommunications']
    for word in result:
        assert lex.is_alliteration(word, "cat"), f"FAIL: {word}"


def test_alliterations_pos():
    result = lex.alliterations_sync("cat", {'numSyllables': 7, 'pos': 'n'})
    assert result == ['electrocardiogram', 'telecommunications']
    for word in result:
        assert lex.is_alliteration(word, "cat"), f"FAIL: {word}"

    result = lex.alliterations_sync("cat", {'minLength': 14, 'pos': 'v'})
    for word in result:
        assert len(word) >= 14
    assert result == ['counterbalance']

    result = lex.alliterations_sync("dog", {'minLength': 13, 'pos': 'rb', 'limit': 11})
    for word in result:
        assert len(word) >= 13
    assert result == [
        'coincidentally', 'conditionally', 'confidentially', 'contradictorily',
        'devastatingly', 'expeditiously', 'paradoxically', 'predominantly',
        'traditionally', 'unconditionally', 'unpredictably',
    ]

    result = lex.alliterations_sync("freedom", {'minLength': 14, 'pos': 'nns'})
    for word in result:
        assert len(word) >= 14
    assert result == [
        'featherbeddings', 'fundamentalists', 'pharmaceuticals',
        'photosyntheses', 'reconfigurations', 'sophistications',
    ]


def test_alliterations():
    result = lex.alliterations_sync("", {'silent': 1})
    assert len(result) < 1

    result = lex.alliterations_sync("#$%^&*", {'silent': 1})
    assert len(result) < 1

    result = lex.alliterations_sync("umbrella", {'silent': 1})
    assert len(result) < 1, "failed on 'umbrella'"

    result = lex.alliterations_sync("cat", {'limit': 100})
    assert len(result) == 100, f"failed on 'cat': len={len(result)}"
    assert "cat" not in result
    for word in result:
        assert lex.is_alliteration(word, "cat"), f"FAIL: {word}"

    result = lex.alliterations_sync("dog", {'limit': 100})
    assert "dog" not in result
    assert len(result) == 100, f"failed on 'dog': len={len(result)}"
    for word in result:
        assert lex.is_alliteration(word, "dog"), f"FAIL: {word}"

    result = lex.alliterations_sync("dog", {'minLength': 15})
    assert 0 < len(result) < 5, f"got length={len(result)}"
    for word in result:
        assert lex.is_alliteration(word, "dog"), f"FAIL1: {word}"

    result = lex.alliterations_sync("cat", {'minLength': 16})
    assert 0 < len(result) < 15, "failed on 'cat'"
    for word in result:
        assert lex.is_alliteration(word, "cat"), f"FAIL2: {word}"

    result = lex.alliterations_sync("khatt", {'minLength': 16})
    assert 0 < len(result) < 15, "failed on 'khatt'"
    for word in result:
        assert lex.is_alliteration(word, "cat"), f"FAIL2: {word}"

    assert lex.alliterations_sync("a") == []
    assert lex.alliterations_sync("I") == []
    assert lex.alliterations_sync("K") == []
