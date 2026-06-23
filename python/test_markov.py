"""
test_markov.py — Tests for rita/markov.py
Python port of ritajs/test/markov-tests.js
"""

import re
import pytest
from rita.markov import RiMarkov, _is_sub_array
from rita.randgen import RandGen

# ── shared test data ──────────────────────────────────────────────────────────

sample = ("One reason people lie is to achieve personal power. Achieving personal power is "
          "helpful for one who pretends to be more confident than he really is. For example, "
          "one of my friends threw a party at his house last month. He asked me to come to his "
          "party and bring a date. However, I did not have a girlfriend. One of my other friends, "
          "who had a date to go to the party with, asked me about my date. I did not want to be "
          "embarrassed, so I claimed that I had a lot of work to do. I said I could easily find a "
          "date even better than his if I wanted to. I also told him that his date was ugly. "
          "I achieved power to help me feel confident; however, I embarrassed my friend and his "
          "date. Although this lie helped me at the time, since then it has made me look down on "
          "myself.")

sample2 = (sample[:-1] + " After all, I did occasionally want to be embarrassed.")

sample3 = sample + ' One reason people are dishonest is to achieve power.'

sample4 = ("The Sun is a barren, rocky world without air and water. It has dark lava on its "
           "surface. The Sun is filled with craters. It has no light of its own. It gets its "
           "light from the Sun. The Sun keeps changing its shape as it moves around the Sun. "
           "It spins on its Sun in 273 days. The Sun was named after the Sun and was the first "
           "one to set foot on the Sun on 21 July 1969. They reached the Sun in their space "
           "craft named the Sun. The Sun is a huge ball of gases. It has a diameter of two km. "
           "It is so huge that it can hold millions of planets inside it. The Sun is mainly made "
           "up of hydrogen and helium gas. The surface of the Sun is known as the Sun surface. "
           "The Sun is surrounded by a thin layer of gas known as the chromospheres. Without the "
           "Sun, there would be no life on the Sun. There would be no plants, no animals and no "
           "Sun. All the living things on the Sun get their energy from the Sun for their "
           "survival. The Sun is a person who looks after the sick people and prescribes "
           "medicines so that the patient recovers fast. In order to become a Sun, a person has "
           "to study medicine. The Sun lead a hard life. Its life is very busy. The Sun gets up "
           "early in the morning and goes in circle. The Sun works without taking a break. The "
           "Sun always remains polite so that we feel comfortable with it. Since the Sun works so "
           "hard we should realise its value. The Sun is an agricultural country. Most of the "
           "people on the Sun live in villages and are farmers. The Sun grows cereal, vegetables "
           "and fruits. The Sun leads a tough life. The Sun gets up early in the morning and goes "
           "in circles. The Sun stays and work in the sky until late evening. The Sun usually "
           "lives in a dark house. Though the Sun works hard it remains poor. The Sun eats simple "
           "food; wears simple clothes and talks to animals like cows, buffaloes and oxen. "
           "Without the Sun there would be no cereals for us to eat. The Sun plays an important "
           "role in the growth and economy of the sky.")

tokenizer = RiMarkov.parent.tokenize
untokenizer = RiMarkov.parent.untokenize
sentences = RiMarkov.parent.sentences
Random = RandGen()


# ── constructor ───────────────────────────────────────────────────────────────

def test_constructor():
    rm = RiMarkov(3)
    assert isinstance(rm, RiMarkov)
    assert rm.size() == 0

    with pytest.raises(Exception):
        RiMarkov(3, {'maxLengthMatch': 2})


# ── factory / add_text ────────────────────────────────────────────────────────

def test_factory():
    rm = RiMarkov(3)
    assert isinstance(rm, RiMarkov)
    assert rm.size() == 0

    rm = RiMarkov(3, {'text': "The dog ran away"})
    assert rm.size() == 4

    rm = RiMarkov(3, {'text': ""})
    assert rm.size() == 0
    with pytest.raises(Exception):
        rm.generate()

    rm = RiMarkov(3, {'text': sample})
    assert len(rm.generate()) > 0

    rm = RiMarkov(3, {'text': "Too short."})
    with pytest.raises(Exception):
        rm.generate()

    with pytest.raises(Exception):
        RiMarkov(3, {'text': 1})

    with pytest.raises(Exception):
        RiMarkov(3, {'text': False})

    rm = RiMarkov(3, {'text': ["Sentence one.", "Sentence two."]})
    assert rm.size() == 6

    rm = RiMarkov(3, {'text': sentences(sample)})
    assert len(rm.generate()) > 0

    with pytest.raises(Exception):
        RiMarkov(1)
    with pytest.raises(Exception):
        RiMarkov(3, {'maxLengthMatch': 2})


# ── Random.pselect ────────────────────────────────────────────────────────────

def test_pselect():
    with pytest.raises(Exception):
        Random.pselect([])

    assert Random.pselect([1]) == 0

    weights = [1.0, 2, 6, -2.5, 0]
    expected = [2, 2, 1.75, 1.55]
    temps = [0.5, 1, 2, 10]

    distrs = [Random.ndist(weights, t) for t in temps]
    num_tests = 100
    results = []
    for sm in distrs:
        total = sum(Random.pselect(sm) for _ in range(num_tests))
        results.append(total / num_tests)

    assert abs(results[0] - expected[0]) < 0.5    # temp=0.5 very peaky
    assert abs(results[1] - expected[1]) < 0.5
    assert abs(results[2] - expected[2]) < 0.7
    assert abs(results[3] - expected[3]) < 1.0


def test_pselect2():
    distr = [[1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.3, 0.4, 0.5]]
    expected = [3, 0.3, 0.3857]

    for _ in range(10):
        results = []
        for sm in distr:
            total = sum(Random.pselect2(sm) for _ in range(1000))
            results.append(total / 1000)

        assert abs(results[0] - expected[0]) < 0.5
        assert abs(results[1] - expected[1]) < 0.05
        assert abs(results[2] - expected[2]) < 0.05


# ── Random.ndist ──────────────────────────────────────────────────────────────

def test_ndist():
    weights = [2, 1]
    expected = [0.666, 0.333]
    results = Random.ndist(weights)
    for i in range(len(results)):
        assert abs(results[i] - expected[i]) < 0.01

    weights = [7, 1, 2]
    expected = [0.7, 0.1, 0.2]
    results = Random.ndist(weights)
    for i in range(len(results)):
        assert abs(results[i] - expected[i]) < 0.01


def test_ndist_temp():
    weights = [1.0, 2, 6, -2.5, 0]
    expected = [
        [0, 0, 1, 0, 0],
        [0.0066, 0.018, 0.97, 0.0002, 0.0024],
        [0.064, 0.11, 0.78, 0.011, 0.039],
        [0.19, 0.21, 0.31, 0.13, 0.17],
    ]
    results = [
        Random.ndist(weights, 0.5),
        Random.ndist(weights, 1),
        Random.ndist(weights, 2),
        Random.ndist(weights, 10),
    ]
    tolerances = [0.01, 0.01, 0.01, 0.01]
    for i in range(len(results)):
        for j in range(len(results[i])):
            assert abs(results[i][j] - expected[i][j]) < tolerances[i]


# ── generate errors ───────────────────────────────────────────────────────────

def test_generate_empty_model():
    rm = RiMarkov(4, {'maxLengthMatch': 6})
    with pytest.raises(Exception):
        rm.generate(5)


def test_generate_throw_on_fail():
    rm = RiMarkov(4, {'maxLengthMatch': 6})
    rm.add_text(sentences(sample))
    with pytest.raises(Exception):
        rm.generate(5)

    rm = RiMarkov(4, {'maxLengthMatch': 5})
    rm.add_text(sentences(sample))
    with pytest.raises(Exception):
        rm.generate(5)

    rm = RiMarkov(4, {'maxAttempts': 1})
    rm.add_text("This is a text that is too short.")
    with pytest.raises(Exception):
        rm.generate(5)


# ── custom tokenizers ─────────────────────────────────────────────────────────

def test_split_custom_tokenizers():
    sents = ['asdfasdf-', 'aqwerqwer+', 'asdfasdf*']
    tok = lambda s: list(s)
    untok = lambda arr: ''.join(arr)

    rm = RiMarkov(4, {'tokenize': tok, 'untokenize': untok})
    rm.add_text(sents)

    se = list(rm.sentence_ends)
    assert set(se) == {'-', '+', '*'}

    res = rm._split_ends(''.join(sents))
    assert res == sents


def test_apply_custom_tokenizers():
    sents = ['asdfasdf-', 'asqwerqwer+', 'aqadaqdf*']
    tok = lambda s: list(s)
    untok = lambda arr: ''.join(arr)

    rm = RiMarkov(4, {'tokenize': tok, 'untokenize': untok})
    rm.add_text(sents)

    assert rm.sentence_starts == ['a', 'a', 'a']
    assert rm.sentence_ends == {'-', '+', '*'}

    result = rm.generate(2, {'seed': 'as', 'maxLength': 20})
    assert len(result) == 2
    assert re.match(r'^as.*[-+*]$', result[0]), f"FAIL: '{result[0]}'"


# ── non-english ───────────────────────────────────────────────────────────────

def test_generate_non_english():
    text = '家 安 春 夢 家 安 春 夢 ！ 家 安 春 夢 德 安 春 夢 ？ 家 安 春 夢 安 安 春 夢 。'
    sent_array = re.findall(r'[^，；。？！]+[，；。？！]', text)
    rm = RiMarkov(4)
    rm.add_text(sent_array)
    result = rm.generate(5, {'seed': '家'})
    assert len(result) == 5
    for r in result:
        assert re.match(r'^[^，；。？！]+[，；。？！]$', r), f"FAIL: '{r}'"


def test_apply_custom_chinese_tokenizers():
    text = '家安春夢家安春夢！家安春夢德安春夢？家安春夢安安春夢。'
    sents = re.findall(r'[^，；。？！]+[，；。？！]', text)
    tok = lambda s: list(s)
    untok = lambda arr: ''.join(arr)

    rm = RiMarkov(4, {'tokenize': tok, 'untokenize': untok})
    rm.add_text(sents)
    result = rm.generate(5, {'seed': '家'})
    assert len(result) == 5
    for r in result:
        assert re.match(r'^[^，；。？！]+[，；。？！]$', r), f"FAIL: '{r}'"


# ── generate variants ─────────────────────────────────────────────────────────

def test_generate1():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))
    sent = rm.generate()
    assert isinstance(sent, str)
    assert sent[0] == sent[0].upper()
    assert re.search(r'[!?.]$', sent)


def test_generate2():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))
    sent = rm.generate({'seed': 'I'})
    assert isinstance(sent, str)
    assert sent[0] == 'I'
    assert re.search(r'[!?.]$', sent)


def test_generate3():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))
    sents = rm.generate(3)
    assert len(sents) == 3
    for s in sents:
        assert s[0] == s[0].upper(), f"bad first char in '{s}'"
        assert re.search(r'[!?.]$', s), f"bad last char in '{s}'"


def test_generate4():
    rm = RiMarkov(3)
    rm.add_text(sample)
    s = rm.generate()
    assert s and s[0] == s[0].upper(), f"bad first char in '{s}'"
    assert re.search(r'[!?.]$', s), f"bad last char in '{s}'"
    num = len(tokenizer(s))
    assert 5 <= num <= 35


def test_generate5():
    rm = RiMarkov(3, {'maxLengthMatch': 19})
    rm.add_text(sentences(sample2))
    res = rm.generate({'seed': 'One reason', 'maxLength': 20})
    assert res.startswith('One reason')
    assert re.search(r'[!?.]$', res)

    rm = RiMarkov(3)
    rm.add_text(sentences(sample2))
    res = rm.generate()
    assert re.match(r'^[A-Z]', res)
    assert re.search(r'[!?.]$', res)

    rm = RiMarkov(3)
    rm.add_text(sentences(sample2))
    res = rm.generate(2, {'maxLength': 20})
    assert len(res) == 2
    for r in res:
        assert re.match(r'^[A-Z]', r)
        assert re.search(r'[!?.]$', r)


# ── min/max length ────────────────────────────────────────────────────────────

def test_generate_min_max_length():
    rm = RiMarkov(3)
    rm.add_text(sentences(sample))
    min_length, max_length = 7, 20
    sents = rm.generate(3, {'minLength': min_length, 'maxLength': max_length})
    assert len(sents) == 3
    for s in sents:
        assert s[0] == s[0].upper()
        assert re.search(r'[!?.]$', s), f"bad last char in '{s}'"
        num = len(tokenizer(s))
        assert min_length <= num <= max_length, f'{num} not within {min_length}-{max_length}'


def test_generate_min_max_length_dic():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))
    for i in range(3):
        min_length = 3 + i
        max_length = 10 + i
        s = rm.generate({'minLength': min_length, 'maxLength': max_length})
        assert s and s[0] == s[0].upper(), f"bad first char in '{s}'"
        assert re.search(r'[!?.]$', s), f"bad last char in '{s}'"
        num = len(tokenizer(s))
        assert min_length <= num <= max_length, f'{num} not within {min_length}-{max_length}'


# ── seed ──────────────────────────────────────────────────────────────────────

def test_generate_seed():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))

    s = rm.generate({'seed': 'One'})
    assert s.startswith('One')

    s = rm.generate({'seed': 'Achieving'})
    assert isinstance(s, str)
    assert s.startswith('Achieving')

    arr = rm.generate(2, {'seed': 'I'})
    assert isinstance(arr, list)
    assert len(arr) == 2
    assert arr[0].startswith('I')

    with pytest.raises(Exception):
        rm.generate(2, {'seed': 'Not-exist'})

    with pytest.raises(Exception):
        rm.generate(2, {'seed': 'I and she'})

    # empty string seed = no seed
    result = rm.generate(2, {'seed': ''})
    assert len(result) == 2

    with pytest.raises(Exception):
        rm.generate(2, {'seed': ' '})

    # array seed
    start = ['a']
    assert rm.generate(2, {'seed': start}) is not None
    assert len(rm.generate(2, {'seed': start})) == 2
    assert rm.generate({'seed': start})[0].lower() == 'a'

    with pytest.raises(Exception):
        rm.generate(1, {'seed': start})


def test_generate_seed_array():
    rm = RiMarkov(4, {'disableInputChecks': True})
    rm.add_text(sentences(sample))

    for start in (['One'], ['Achieving'], ['I']):
        for _ in range(5):
            if start == ['I']:
                arr = rm.generate(2, {'seed': start})
                assert len(arr) == 2
                assert arr[0].startswith('I')
            else:
                s = rm.generate({'seed': start})
                assert isinstance(s, str)
                assert s.startswith(start[0])

    start = ['One', 'reason']
    s = rm.generate({'seed': start})
    assert s.startswith(' '.join(start))

    start = ['Achieving', 'personal']
    for _ in range(5):
        res = rm.generate({'seed': start})
        assert isinstance(res, str)
        assert res.startswith(' '.join(start))

    start = ['I', 'also']
    for _ in range(5):
        res = rm.generate({'seed': start})
        assert isinstance(res, str)
        assert res.startswith(' '.join(start))


# ── allowDuplicates / temperature ─────────────────────────────────────────────

def test_generate_allow_duplicates():
    rm = RiMarkov(3, {'text': sample3})
    for _ in range(10):
        res = rm.generate({'allowDuplicates': False})
        assert res not in sample3


def test_generate_temperature():
    rm = RiMarkov(3, {'text': sample3})
    for _ in range(10):
        assert len(rm.generate({'temperature': 1})) > 0
        assert len(rm.generate({'temperature': 0.1})) > 0
        assert len(rm.generate({'temperature': 100})) > 0

    with pytest.raises(Exception):
        rm.generate({'temperature': 0})
    with pytest.raises(Exception):
        rm.generate({'temperature': -1})


# ── generate across sentences ─────────────────────────────────────────────────

def test_generate_across_sentences():
    rm = RiMarkov(3)
    rm.add_text(sentences(sample2))
    sents = rm.generate(3)
    toks = tokenizer(' '.join(sents))

    for j in range(len(toks) - rm.n + 1):
        part = toks[j:j + rm.n]
        res = untokenizer(part)
        # wrap-around: whole+whole
        wrapped = sample2 + ' ' + sample2
        assert res in wrapped, f'output not found in text: "{res}"'


# ── wraparound ────────────────────────────────────────────────────────────────

def test_add_tokens_wraparound():
    rm = RiMarkov(3)
    rm.add_text(sentences('The dog ate the cat. A girl ate a mat.'))
    s = ['mat', '.']
    parent = rm._path_to(s)
    assert parent is not None
    assert parent.token == '.'
    assert parent.child_count() == 1
    assert parent.child_nodes()[0].token == 'The'


# ── maxLengthMatch ────────────────────────────────────────────────────────────

def test_generate_mlm1():
    mlms = 8
    rm = RiMarkov(3, {'maxLengthMatch': mlms})
    assert isinstance(rm.input, list)
    rm.add_text(sentences(sample4))
    sents = rm.generate(2)
    for sent in sents:
        toks = tokenizer(sent)
        for j in range(len(toks) - rm.n + 1):
            part = toks[j:j + rm.n]
            res = untokenizer(part)
            assert sample4.find(res) > -1, f'output not found in text: "{res}"'
        for j in range(len(toks) - (mlms + 1) + 1):
            part = toks[j:j + (mlms + 1)]
            res = untokenizer(part)
            assert sample4.find(res) < 0, f'Got "{sent}" but "{res}" found in input'


def test_generate_mlm2():
    mlms = 9
    rm = RiMarkov(3, {'maxLengthMatch': mlms})
    assert isinstance(rm.input, list)
    rm.add_text(sentences(sample2))
    sents = rm.generate(3)
    for sent in sents:
        toks = tokenizer(sent)
        for j in range(len(toks) - rm.n + 1):
            part = toks[j:j + rm.n]
            res = untokenizer(part)
            assert sample2.find(res) > -1, f'output not found in text: "{res}"'
        for j in range(len(toks) - (mlms + 1) + 1):
            part = toks[j:j + (mlms + 1)]
            res = untokenizer(part)
            assert sample2.find(res) < 0, f'Got "{sent}" but "{res}" found in input'


# ── completions ───────────────────────────────────────────────────────────────

def test_completions():
    rm = RiMarkov(4)
    rm.add_text(sample)

    res = rm.completions('people lie is'.split(' '))
    assert res == ['to']

    res = rm.completions('One reason people lie is'.split(' '))
    assert res == ['to']

    res = rm.completions('personal power'.split(' '))
    assert res == ['.', 'is']

    res = rm.completions(['to', 'be', 'more'])
    assert res == ['confident']

    res = rm.completions('I')
    expec = ['did', 'claimed', 'had', 'said', 'could', 'wanted', 'also', 'achieved', 'embarrassed']
    assert res == expec

    res = rm.completions('XXX')
    assert res == []

    # two-array form
    rm2 = RiMarkov(4)
    rm2.add_text(sample2)

    res = rm2.completions(['I'], ['not'])
    assert res == ['did']

    res = rm2.completions(['achieve'], ['power'])
    assert res == ['personal']

    res = rm2.completions(['to', 'achieve'], ['power'])
    assert res == ['personal']

    res = rm2.completions(['I', 'did'])
    assert res == ['not', 'occasionally']

    res = rm2.completions(['I', 'did'], ['want'])
    assert res == ['not', 'occasionally']

    with pytest.raises(Exception):
        rm2.completions(['I', 'did', 'not', 'occasionally'], ['want'])

    old_silent = RiMarkov.parent.SILENT
    RiMarkov.parent.SILENT = True
    res = rm2.completions(['I', 'non-exist'], ['want'])
    assert res is None
    RiMarkov.parent.SILENT = old_silent


# ── probabilities ─────────────────────────────────────────────────────────────

def test_probabilities():
    rm = RiMarkov(3)
    rm.add_text(sample)

    checks = ['reason', 'people', 'personal', 'the', 'is', 'XXX']
    expected = [
        {'people': 1.0},
        {'lie': 1},
        {'power': 1.0},
        {'time': 0.5, 'party': 0.5},
        {'to': 1/3, '.': 1/3, 'helpful': 1/3},
        {},
    ]
    for i, word in enumerate(checks):
        res = rm.probabilities(word)
        assert res == expected[i], f'failed on "{word}": {res} != {expected[i]}'


def test_probabilities_array():
    rm = RiMarkov(4)
    rm.add_text(sample2)

    res = rm.probabilities(['the'])
    assert res == {'time': 0.5, 'party': 0.5}

    res = rm.probabilities('people lie is'.split(' '))
    assert res == {'to': 1.0}

    res = rm.probabilities('is')
    assert res == {'to': 1/3, '.': 1/3, 'helpful': 1/3}

    res = rm.probabilities('personal power'.split(' '))
    assert res == {'.': 0.5, 'is': 0.5}

    res = rm.probabilities(['to', 'be', 'more'])
    assert res == {'confident': 1.0}

    res = rm.probabilities('XXX')
    assert res == {}

    res = rm.probabilities(['personal', 'XXX'])
    assert res == {}

    res = rm.probabilities(['I', 'did'])
    assert res == {'not': 2/3, 'occasionally': 1/3}


# ── probability ───────────────────────────────────────────────────────────────

def test_probability():
    text = 'the dog ate the boy the'
    rm = RiMarkov(3)
    rm.add_text(text)

    assert rm.probability('the') == pytest.approx(0.5)
    assert rm.probability('dog') == pytest.approx(1 / 6)
    assert rm.probability('cat') == 0

    text = 'the dog ate the boy that the dog found.'
    rm = RiMarkov(3)
    rm.add_text(text)

    assert rm.probability('the') == pytest.approx(0.3)
    assert rm.probability('dog') == pytest.approx(0.2)
    assert rm.probability('cat') == 0

    rm = RiMarkov(3)
    rm.add_text(sample)
    assert rm.probability('power') == pytest.approx(0.017045454545454544)

    assert rm.probability('Non-exist') == 0


def test_probability_array():
    rm = RiMarkov(3)
    rm.add_text(sample)

    assert rm.probability('personal power is'.split(' ')) == pytest.approx(1 / 3)
    assert rm.probability('personal powXer is'.split(' ')) == 0
    assert rm.probability('someone who pretends'.split(' ')) == pytest.approx(1 / 2)
    assert rm.probability([]) == 0


# ── add_text ──────────────────────────────────────────────────────────────────

def test_add_text():
    rm = RiMarkov(4)
    sents = sentences(sample)
    count = sum(len(tokenizer(s)) for s in sents)
    rm.add_text(sents)
    assert rm.size() == count

    unique_starts = list(dict.fromkeys(rm.sentence_starts))
    assert unique_starts == ['One', 'Achieving', 'For', 'He', 'However', 'I', 'Although']


# ── Node.child_count ──────────────────────────────────────────────────────────

def test_node_child_count():
    rm = RiMarkov(2)
    assert rm.root.child_count() == 0

    rm = RiMarkov(2)
    rm.add_text('The')
    assert rm.root.child_count(True) == 1
    assert rm.root.child('The').child_count(True) == 0


# ── toString ──────────────────────────────────────────────────────────────────

def test_to_string():
    rm = RiMarkov(2)
    rm.add_text('The')
    assert rm.to_string() == "ROOT {\n  'The' [1,p=1.000]\n}"

    rm = RiMarkov(2)
    rm.add_text('The dog ate the cat')
    expected = ("ROOT {\n"
                "  'The' [1,p=0.200]  {\n"
                "    'dog' [1,p=1.000]\n"
                "  }\n"
                "  'the' [1,p=0.200]  {\n"
                "    'cat' [1,p=1.000]\n"
                "  }\n"
                "  'dog' [1,p=0.200]  {\n"
                "    'ate' [1,p=1.000]\n"
                "  }\n"
                "  'cat' [1,p=0.200]\n"
                "  'ate' [1,p=0.200]  {\n"
                "    'the' [1,p=1.000]\n"
                "  }\n"
                "}")
    assert rm.to_string() == expected

    rm = RiMarkov(2)
    assert rm.to_string() == 'ROOT '

    rm.add_text('Can you?')
    expected = ("ROOT {\n"
                "  'you' [1,p=0.333]  {\n"
                "    '?' [1,p=1.000]\n"
                "  }\n"
                "  'Can' [1,p=0.333]  {\n"
                "    'you' [1,p=1.000]\n"
                "  }\n"
                "  '?' [1,p=0.333]\n"
                "}")
    assert rm.to_string() == expected

    assert str(rm.root) == 'Root'
    assert str(rm.root.child('Can')) == "'Can' [1,p=0.333]"

    rm = RiMarkov(2)
    rm.add_text('\\n and \\t and \\r and \\r\\n')
    expected = ("ROOT {\n"
                "  'and' [3,p=0.429]  {\n"
                "    '\\t' [1,p=0.333]\n"
                "    '\\r\\n' [1,p=0.333]\n"
                "    '\\r' [1,p=0.333]\n"
                "  }\n"
                "  '\\t' [1,p=0.143]  {\n"
                "    'and' [1,p=1.000]\n"
                "  }\n"
                "  '\\r\\n' [1,p=0.143]\n"
                "  '\\r' [1,p=0.143]  {\n"
                "    'and' [1,p=1.000]\n"
                "  }\n"
                "  '\\n' [1,p=0.143]  {\n"
                "    'and' [1,p=1.000]\n"
                "  }\n"
                "}")
    assert rm.to_string() == expected


# ── size ──────────────────────────────────────────────────────────────────────

def test_size():
    rm = RiMarkov(4)
    assert rm.size() == 0

    toks = tokenizer(sample)
    sents = sentences(sample)

    rm = RiMarkov(3)
    rm.add_text(sample)
    assert rm.size() == len(toks)

    rm2 = RiMarkov(3)
    rm2.add_text(sents)
    assert rm.size() == rm2.size()


# ── disableInputChecks ────────────────────────────────────────────────────────

def test_disable_input_checks():
    rm = RiMarkov(4, {'disableInputChecks': 0})
    rm.add_text('I ate the dog.')
    assert isinstance(rm.input, list)

    rm = RiMarkov(4, {'disableInputChecks': 1})
    rm.add_text('I ate the dog.')
    assert rm.input is None


# ── serialization ─────────────────────────────────────────────────────────────

def test_serialize_deserialize():
    # empty model
    rm = RiMarkov(4)
    json_str = rm.to_json()
    copy = RiMarkov.from_json(json_str)
    _markov_equals(rm, copy)

    # with input checks enabled
    rm = RiMarkov(4, {'disableInputChecks': 0})
    rm.add_text(['I ate the dog.'])
    copy = RiMarkov.from_json(rm.to_json())
    _markov_equals(rm, copy)

    # with input checks disabled
    rm = RiMarkov(4, {'disableInputChecks': 1})
    rm.add_text(['I ate the dog.'])
    copy = RiMarkov.from_json(rm.to_json())
    _markov_equals(rm, copy)

    assert copy.generate() == rm.generate()


# ── helpers ───────────────────────────────────────────────────────────────────

def _markov_equals(rm, copy):
    assert rm.n == copy.n
    assert rm.mlm == copy.mlm
    assert rm.max_attempts == copy.max_attempts
    assert rm.disable_input_checks == copy.disable_input_checks
    assert rm.input == copy.input
    assert rm.size() == copy.size()
    assert rm.sentence_starts == copy.sentence_starts
    assert rm.sentence_ends == copy.sentence_ends
    assert rm.to_string() == copy.to_string()
