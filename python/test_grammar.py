"""
test_grammar.py — Python port of grammar.tests.js
"""
import re
import math
import pytest
from riscript import RiGrammar, RiScript, EvalVisitor

IfRiTa = False  # set True if RiTa NLP is available

SEQ_COUNT = 5


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def rg():
    return RiGrammar()


@pytest.fixture
def rs():
    return RiScript()


# ── helpers ───────────────────────────────────────────────────────────────────

sentences1 = {
    'start':       '$noun_phrase $verb_phrase.',
    'noun_phrase':  '$determiner $noun',
    'verb_phrase':  '($verb | $verb $noun_phrase)',
    'determiner':   '(a | the)',
    'noun':         '(woman | man)',
    'verb':         'shoots'
}

sentences2 = {
    'start':       '$noun_phrase $verb_phrase.',
    'noun_phrase':  '$determiner $noun',
    'determiner':   'a | the',
    'verb_phrase':  '$verb $noun_phrase | $verb',
    'noun':         'woman | man',
    'verb':         'shoots'
}

sentences3 = {
    'start':       '$noun_phrase $verb_phrase.',
    'noun_phrase':  '$determiner $noun',
    'verb_phrase':  '$verb | $verb $noun_phrase',
    'determiner':   'a | the',
    'noun':         'woman | man',
    'verb':         'shoots'
}

grammars = [sentences1, sentences2, sentences3]


# ── tests ─────────────────────────────────────────────────────────────────────

class TestGrammars:

    def test_handles_simple_grammars(self):
        script = {
            'noun':  '[ox | oxen]',
            'start': '$noun.art()'
        }
        res = RiGrammar.expand(script)
        assert re.match(r'an ox(en)?', res)

    def test_handles_character_choice_in_context(self):
        context = {'a': {'name': 'Lucy'}, 'b': {'name': 'Sam'}}
        script = {
            'start':  '$person.name',
            'person': '$[a | b]'
        }
        res = RiGrammar.expand(script, context)
        assert res in ['Lucy', 'Sam']

        context = {
            'lucy': {'name': 'Lucy', 'pronoun': 'she', 'car': 'Lexus'},
            'sam':  {'name': 'Sam',  'pronoun': 'he',  'car': 'Subaru'},
        }
        script = {
            'start':   'Meet $person.name. $person.pronoun().cap drives a $person.car().',
            '#person': '$[sam | lucy]'
        }
        res = RiGrammar.expand(script, context)
        assert res in [
            'Meet Lucy. She drives a Lexus.',
            'Meet Sam. He drives a Subaru.',
        ]

    def test_handles_simple_character_choice_in_context(self):
        context = {'a': {'name': 'Lucy'}, 'b': {'name': 'Sam'}}
        script = {
            'start':  '$person.name',
            'person': '$[a | b]'
        }
        res = RiGrammar.expand(script, context)
        assert res in ['Lucy', 'Sam']

    def test_should_reference_context_from_transforms(self):
        ctx = {'prop': 42, 'func': lambda: 42}
        rules = {'start': '$.func'}
        res = RiGrammar.expand(rules, ctx)
        assert res == '42'

        # JS: func returns this.prop.num (= 42), not the dict
        ctx = {'prop': {'num': 42}, 'func': lambda: 42}
        rules = {'start': '$.func'}
        res = RiGrammar.expand(rules, ctx)
        assert res == '42'

        ctx = {'prop': {'num': 42}, 'func': lambda: {'num': 42}}
        rules = {'start': '$.func.num'}
        res = RiGrammar.expand(rules, ctx)
        assert res == '42'

        ctx = {'char': {'name': 'bill', 'age': 42}, 'func': lambda: {'name': 'bill', 'age': 42}}
        rules = {'start': '{$chosen=$.func} $chosen.name is $chosen.age years old'}
        res = RiGrammar.expand(rules, ctx)
        assert res == 'bill is 42 years old'

        ctx = {'char': {'name': 'bill', 'age': 42}, 'func': lambda: {'name': 'bill', 'age': 42}}
        rules = {'start': '{$chosen=$.func} $chosen.name is $chosen.age years old'}
        res = RiGrammar.expand(rules, ctx)
        assert res == 'bill is 42 years old'

    def test_handles_time_based_gated_example(self):
        import datetime
        hours = datetime.datetime.now().hour
        context = {'hours': hours}
        grammar = {
            'start':    '$greeting, he said.',
            'greeting': '[ @{ hours: {$lt: 12}} $morning || $evening]',
            'morning':  'Good morning',
            'evening':  'Good evening'
        }
        res = RiGrammar.expand(grammar, context)
        assert res in ['Good morning, he said.', 'Good evening, he said.']

    def test_handles_time_based_transform_example(self):
        import datetime
        context = {'getGreeting': lambda: '$morning' if datetime.datetime.now().hour < 12 else '$evening'}
        grammar = {
            'start':    '$greeting, he said.',
            'greeting': '$.getGreeting()',
            'morning':  'Good morning',
            'evening':  'Good evening'
        }
        res = RiGrammar.expand(grammar, context)
        assert res in ['Good morning, he said.', 'Good evening, he said.']

    def test_handles_character_choice_in_grammar(self):
        script = {
            '#person': "Sam {$pronoun=He}{$car=Lexus} | Lucy {$pronoun=She}{$car=Subaru}",
            'start':   'Meet $person. $pronoun drives a $car.',
        }
        res = RiGrammar.expand(script)
        assert res in [
            'Meet Lucy. She drives a Subaru.',
            'Meet Sam. He drives a Lexus.',
        ]

        script = {
            '#person': '$sam | $lucy',
            'sam':     'Sam {$pronoun=He}{$car=Lexus}',
            'lucy':    'Lucy {$pronoun=She}{$car=Subaru}',
            'start':   'Meet $person. $pronoun drives a $car.',
        }
        res = RiGrammar.expand(script)
        assert res in [
            'Meet Lucy. She drives a Subaru.',
            'Meet Sam. He drives a Lexus.',
        ]

    def test_handles_simple_statics(self):
        script = {
            '#noun': '[a | b]',
            'start': '$noun\n$noun'
        }
        res = RiGrammar.expand(script)
        assert re.match(r'(a\na)|(b\nb)', res)

    def test_handles_simple_wrapped_statics(self):
        script = {
            '#noun': '[a | b]',
            'start': '$noun $noun'
        }
        res = RiGrammar.expand(script)
        assert re.match(r'(a a)|(b b)', res)

    def test_handles_longer_grammars(self):
        rules = {
            'start':     '$kaminoku <br> $shimonoku',
            'kaminoku':  '$five <br> $sevenFive[. | ...(3)]',
            'shimonoku': '[[$sevenB1 <br> $sevenC] | [$doubleA | $doubleB]].cap.',
            'four':      'look for water | look to the $n | pray for quiet',
            'five':      '[[the $nnnn | $nnnnn | $vp4 now] | [last | red] [mountain|wilting] flower].cap',
            'sevenFive': 'I [rise | wake] and $four <br> $vp5 | $twelve $tree',
            'sevenB1':   '[no one [need | can] understand] | [no one can forget | everyone forgets | no one misunderstands].cap',
            'sevenC':    'the [vastness|stillness] of this [garden | universe | morning]',
            'twelve':    '[[[beetle|termite] eats | ant burrows].art [silently | placidly] <br> into the] | [[spider | inchworm].art dangles <br> from the]',
            'n':         'clouds | trees | leaves',
            'nn':        'the [stars | moon | sun | sky]',
            'nnn':       'a black rose | white daisies | sakura | rosemary | cool moonlight | dark forest | tall mountain',
            'nnnn':      '[mountain | silent] village | [evening | morning] sunlight | [winter | summer] flower | [star | moon]light above',
            'nnnnn':     'the [autumn | summer | winter] moonlight',
            'tree':      '[chestnut | cedar | old [gum | tea]] tree',
            'vp4':       'drifting like [snow|clouds] | falling like [rain | leaves] ',
            'vp5':       'crying like a child | singing like a bird | drifting like the snow | falling like [the rain | a leaf]',
            'doubleA':   'not [quite|] far enough away <br> but closer than $nn',
            'doubleB':   'close enough to touch <br> but farther even than $nn',
            'a':         'sad | tall | hot | plain | grey',
            'v':         'sing | cry | rise | bloom | dance | fall'
        }
        res = RiGrammar.expand(rules)
        lines = re.split(r'\s*<br>\s*', res)
        assert len(lines) == 5

    def test_handles_gates_in_grammars(self):
        script = {
            '#noun': '[man | woman]',
            'start': '$noun[@{$noun: "man"} :boy]'
        }
        res = RiGrammar.expand(script)
        assert res == 'man:boy' or res == 'woman'

    def test_resolves_inline_grammars(self):
        script = '\n'.join([
            '$start = $nounp $verbp.',
            '$nounp = $determiner $noun',
            '$determiner = [the | the]',
            '$verbp = $verb $nounp',
            '$noun = [woman | woman]',
            '$verb = shoots',
            '$start'
        ])
        rs = RiScript()
        res = rs.evaluate(script)
        assert res == 'the woman shoots the woman.'

    def test_reevaluate_dynamics(self):
        script = {
            'noun':  '[man | woman]',
            'start': '$noun:$noun'
        }
        ok = False
        for _ in range(20):
            res = RiGrammar.expand(script)
            parts = res.split(':')
            assert len(parts) == 2
            if parts[0] != parts[1]:
                ok = True
                break
        assert ok

    def test_reuse_statics(self):
        script = {
            '#noun': '[man | woman]',
            'start': '#noun:#noun'
        }
        for _ in range(5):
            res = RiGrammar.expand(script)
            assert res in ('man:man', 'woman:woman')

    def test_handles_norepeat_in_grammars(self):
        script = {
            'noun':  '[man | woman]',
            'start': '$noun:$noun.nr'
        }
        for _ in range(5):
            res = RiGrammar.expand(script)
            assert res in ('man:woman', 'woman:man')

    def test_calls_constructor(self):
        assert RiGrammar() is not None

    def test_support_norepeat_rules(self):
        names = 'a|b|c|d|e'
        g = {'start': '$names $names.norepeat()', 'names': names}
        fail = False
        for _ in range(SEQ_COUNT):
            res = RiGrammar.expand(g)
            assert re.match(r'^[a-e] [a-e]$', res)
            parts = res.split(' ')
            assert len(parts) == 2
            if parts[0] == parts[1]:
                fail = True
                break
        assert not fail

    def test_support_norepeat_inline_rules(self):
        g = {'start': '[$names=[a|b|c|d|e]] $names.nr()'}
        fail = False
        for _ in range(SEQ_COUNT):
            res = RiGrammar.expand(g)
            assert re.match(r'^[a-e] [a-e]$', res)
            parts = res.split(' ')
            assert len(parts) == 2
            if parts[0] == parts[1]:
                fail = True
                break
        assert not fail

    def test_calls_constructor_json(self):
        import json
        json_str = json.dumps(sentences1)
        gr1 = RiGrammar(json.loads(json_str))
        assert isinstance(gr1, RiGrammar)

        gr2 = RiGrammar.from_json(json_str)
        assert isinstance(gr2, RiGrammar)
        assert gr1.toString() == gr2.toString()

        with pytest.raises(Exception):
            RiGrammar("notjson")

    def test_calls_static_expand_from(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        rg.add_rule('pet', '[$bird | $mammal]')
        rg.add_rule('bird', '[hawk | crow]')
        rg.add_rule('mammal', 'dog')
        assert rg.expand({'start': 'mammal'}) == 'dog'
        for _ in range(5):
            res = rg.expand({'start': 'bird'})
            assert res in ('hawk', 'crow')

    def test_handles_phrase_transforms(self):
        g = {
            'start': '[$x=$y b].ucf()',
            'y':     '[a | a]'
        }
        assert RiGrammar.expand(g) == 'A b'

        h = {
            'start': '[$x=$y c].ucf()',
            'y':     '[a | b]'
        }
        rg = RiGrammar(h)
        for _ in range(5):
            res = rg.expand()
            assert re.match(r'[AB] c', res)

    def test_allows_rules_starting_with_numbers(self):
        rg = RiGrammar({
            'start':  '$1line talks too much.',
            '1line':  'Dave | Jill | Pete'
        })
        rs = rg.expand()
        assert rs in [
            'Dave talks too much.',
            'Jill talks too much.',
            'Pete talks too much.'
        ]

        rg = RiGrammar({'1line': 'Dave | Jill | Pete'})
        rs = rg.expand({'start': '1line'})
        assert rs in ['Dave', 'Jill', 'Pete']

    def test_allows_static_rules_starting_with_numbers(self):
        rg = RiGrammar({
            'start':   '$1line talks too much.',
            '#1line':  'Dave | Jill | Pete'
        })
        rs = rg.expand()
        assert rs in [
            'Dave talks too much.',
            'Jill talks too much.',
            'Pete talks too much.'
        ]

        rg = RiGrammar({'#1line': 'Dave | Jill | Pete'})
        rs = rg.expand({'start': '1line'})
        assert rs in ['Dave', 'Jill', 'Pete']

    def test_calls_set_rules(self):
        rg = RiGrammar()
        assert rg.rules is not None
        assert 'start' not in rg.rules
        assert 'noun_phrase' not in rg.rules

        for g in grammars:
            rg.set_rules(g)
            assert 'start' in rg.rules
            assert 'noun_phrase' in rg.rules
            assert len(rg.expand()) > 0

        rg = RiGrammar()
        rg.set_rules('{"start":"a"}')
        assert len(rg.expand()) > 0

    def test_calls_from_json_with_string(self):
        import json
        for g in grammars:
            rg = RiGrammar.from_json(json.dumps(g))
            assert 'start' in rg.rules
            assert 'noun_phrase' in rg.rules
            assert len(rg.expand()) > 0

    def test_calls_remove_rule(self):
        for g in grammars:
            rg = RiGrammar(g)
            assert 'start' in rg.rules
            assert 'noun_phrase' in rg.rules

            rg.remove_rule('noun_phrase')
            assert 'noun_phrase' not in rg.rules

            rg.remove_rule('start')
            assert 'start' not in rg.rules

            rg.remove_rule('')
            rg.remove_rule('bad-name')
            rg.remove_rule(None)

    def test_calls_static_remove_rule(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        rg.add_rule('pet', '[$bird | $mammal]')
        rg.add_rule('bird', '[hawk | crow]')
        rg.add_rule('mammal', 'dog')

        assert 'start' in rg.rules
        assert 'pet' in rg.rules
        assert 'bird' in rg.rules

        rg.remove_rule('$pet')  # does nothing
        assert 'pet' in rg.rules

        rg.remove_rule('pet')
        assert 'pet' not in rg.rules

        rg.remove_rule('bird')
        assert 'bird' not in rg.rules

        rg.remove_rule('start')
        assert 'start' not in rg.rules

        assert 'mammal' in rg.rules

    def test_throws_on_missing_rules(self):
        rg = RiGrammar()
        with pytest.raises(Exception):
            rg.expand()

        rg = RiGrammar({'start': 'My rule'})
        with pytest.raises(Exception):
            rg.expand({'start': 'bad'})

        rg = RiGrammar({'1line': 'Dave | Jill | Pete'})
        with pytest.raises(Exception):
            rg.expand()  # no start rule

    def test_calls_expand_from(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        rg.add_rule('pet', '[$bird | $mammal]')
        rg.add_rule('bird', '[hawk | crow]')
        rg.add_rule('mammal', 'dog')
        assert rg.expand({'start': 'mammal'}) == 'dog'
        for _ in range(5):
            res = rg.expand({'start': 'bird'})
            assert res in ('hawk', 'crow')

    def test_throws_on_bad_grammars(self):
        with pytest.raises(Exception):
            RiGrammar({'': 'pet'})
        with pytest.raises(Exception):
            RiGrammar({'$start': 'pet'})
        with pytest.raises(Exception):
            RiGrammar('"{start": "pet" }')
        with pytest.raises(Exception):
            RiGrammar().add_rule('$$rule', 'pet')
        with pytest.raises(Exception):
            RiGrammar('pet')

        # these should NOT raise
        RiGrammar({'a': 'pet'})
        RiGrammar('{ "a": "pet" }')
        RiGrammar({'start': 'pet'})
        RiGrammar().add_rule('rule', 'pet')
        RiGrammar().remove_rule('rule')
        RiGrammar().remove_rule('nonexistent')

    def test_calls_to_string(self):
        rg = RiGrammar({'start': 'pet'})
        assert rg.toString() == '{\n  "start": "pet"\n}'

        rg = RiGrammar({'start': '$pet', 'pet': 'dog'})
        assert rg.toString() == '{\n  "start": "$pet",\n  "pet": "dog"\n}'

        rg = RiGrammar({'start': '$pet | $iphone', 'pet': 'dog | cat', 'iphone': 'iphoneSE | iphone12'})
        assert rg.toString() == '{\n  "start": "$pet | $iphone",\n  "pet": "dog | cat",\n  "iphone": "iphoneSE | iphone12"\n}'

        rg = RiGrammar({'start': '$pet.articlize()', 'pet': 'dog | cat'})
        assert rg.toString() == '{\n  "start": "$pet.articlize()",\n  "pet": "dog | cat"\n}'

        rg = RiGrammar({'start': '$pet.articlize()', 'pet': '[dog | cat]'})
        assert rg.toString() == '{\n  "start": "$pet.articlize()",\n  "pet": "[dog | cat]"\n}'

        rg = RiGrammar({'start': '#pet.articlize()', '#pet': '[dog | cat]'})
        assert rg.toString() == '{\n  "start": "#pet.articlize()",\n  "#pet": "[dog | cat]"\n}'

        rg = RiGrammar({'start': '$pet.articlize()', '#pet': '[dog | cat]'})
        assert rg.toString() == '{\n  "start": "$pet.articlize()",\n  "#pet": "[dog | cat]"\n}'

    def test_calls_to_string_with_arg(self):
        lb = {'linebreak': '<br/>'}
        rg = RiGrammar({'start': 'pet'})
        assert rg.toString(lb) == '{<br/>  "start": "pet"<br/>}'

        rg = RiGrammar({'start': '$pet', 'pet': 'dog'})
        assert rg.toString(lb) == '{<br/>  "start": "$pet",<br/>  "pet": "dog"<br/>}'

        rg = RiGrammar({'start': '$pet | $iphone', 'pet': 'dog | cat', 'iphone': 'iphoneSE | iphone12'})
        assert rg.toString(lb) == '{<br/>  "start": "$pet | $iphone",<br/>  "pet": "dog | cat",<br/>  "iphone": "iphoneSE | iphone12"<br/>}'

        rg = RiGrammar({'start': '$pet.articlize()', 'pet': 'dog | cat'})
        assert rg.toString(lb) == '{<br/>  "start": "$pet.articlize()",<br/>  "pet": "dog | cat"<br/>}'

        rg = RiGrammar({'start': '$pet.articlize()', '#pet': 'dog | cat'})
        assert rg.toString(lb) == '{<br/>  "start": "$pet.articlize()",<br/>  "#pet": "dog | cat"<br/>}'

    def test_calls_expand(self):
        rg = RiGrammar()
        rg.add_rule('start', 'pet')
        assert rg.expand() == 'pet'

        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        rg.add_rule('pet', 'dog')
        assert rg.expand() == 'dog'

        rg = RiGrammar()
        rg.add_rule('start', 'dog')
        rg.add_rule('pet', 'cat')
        assert rg.expand({'start': 'pet'}) == 'cat'

        # throw on bad rules
        with pytest.raises(Exception):
            rg.expand({'start': 'dog'})  # 'dog' is not a rule name
        with pytest.raises(Exception):
            rg.expand({'start': 'pets'})
        with pytest.raises(Exception):
            rg.expand({'start': 'a$pet'})

        with pytest.raises(Exception):
            RiGrammar().add_rule('pet', 'dog').expand()  # no start rule

    def test_overrides_dynamic_default(self):
        rg = RiGrammar()
        rg.add_rule('start', '$rule $rule')
        rg.add_rule('rule', '[a|b|c|d|e]')
        ok = False
        for _ in range(5):
            parts = rg.expand().split(' ')
            assert len(parts) == 2
            if parts[0] != parts[1]:
                ok = True
                break
        assert ok

        rg = RiGrammar()
        rg.add_rule('start', '$rule $rule')
        rg.add_rule('#rule', '[a|b|c|d|e]')
        for _ in range(5):
            parts = rg.expand().split(' ')
            assert len(parts) == 2
            assert parts[0] == parts[1]

    def test_calls_expand_weights(self):
        rg = RiGrammar()
        rg.add_rule('start', '$rule1')
        rg.add_rule('rule1', 'cat | dog | boy')
        found = set()
        for _ in range(100):
            res = rg.expand()
            assert res in ('cat', 'dog', 'boy')
            found.add(res)
            if len(found) == 3:
                break
        assert found == {'cat', 'dog', 'boy'}

    def test_calls_expand_from_weights(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        rg.add_rule('pet', '$bird (9) | $mammal')
        rg.add_rule('bird', 'hawk')
        rg.add_rule('mammal', 'dog')

        assert rg.expand({'start': 'mammal'}) == 'dog'

        hawks = dogs = 0
        for i in range(100):
            res = rg.expand({'start': 'pet'})
            assert res in ('hawk', 'dog')
            if res == 'dog':
                dogs += 1
            if res == 'hawk':
                hawks += 1
            if i > 10 and dogs > hawks * 2 and hawks > 0:
                break
        assert hawks > dogs * 2, f'got h={hawks}, d={dogs}'

    def test_calls_add_rule(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet')
        assert 'start' in rg.rules
        rg.add_rule('start', '$dog')
        assert 'start' in rg.rules
        rg.add_rule('start', 'a|b')
        assert 'start' in rg.rules
        with pytest.raises(Exception):
            rg.add_rule('start', None)

    def test_calls_expand_from_weights_static(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet $pet')
        rg.add_rule('#pet', '$bird (9) | $mammal')
        rg.add_rule('bird', 'hawk')
        rg.add_rule('mammal', 'dog')

        res = rg.expand({'start': 'mammal'})
        assert res == 'dog'

        hawks = dogs = 0
        for i in range(100):
            res = rg.expand({'start': 'start'})
            assert res in ('hawk hawk', 'dog dog')
            if res == 'dog dog':
                dogs += 1
            if res == 'hawk hawk':
                hawks += 1
            if i > 10 and dogs > hawks * 2 and hawks > 0:
                break
        assert hawks > dogs

    def test_handles_transforms(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet.toUpperCase()')
        rg.add_rule('pet', 'dog')
        assert rg.expand() == 'DOG'

        rg = RiGrammar()
        rg.add_rule('start', '[$pet | $animal]')
        rg.add_rule('animal', '$pet')
        rg.add_rule('pet', '[dog].toUpperCase()')
        assert rg.expand() == 'DOG'

        rg = RiGrammar()
        rg.add_rule('start', '[$pet | $animal]')
        rg.add_rule('animal', '$pet')
        rg.add_rule('pet', '[dog].uc')
        assert rg.expand() == 'DOG'

        rg = RiGrammar()
        rg.add_rule('start', '[a | a].uc()')
        assert rg.expand() == 'A'

    def test_handles_transforms_on_statics(self):
        rg = RiGrammar()
        rg.add_rule('start', '$pet.toUpperCase()')
        rg.add_rule('#pet', 'dog')
        assert rg.expand() == 'DOG'

        rg = RiGrammar()
        rg.add_rule('start', '[$pet | $animal]')
        rg.add_rule('animal', '$pet')
        rg.add_rule('#pet', '[dog].toUpperCase()')
        assert rg.expand() == 'DOG'

        rg = RiGrammar()
        rg.add_rule('start', '[a | a].uc()')
        assert rg.expand() == 'A'

        rg = RiGrammar()
        rg.add_rule('start', '[$animal $animal].ucf()')
        rg.add_rule('#animal', 'ant | eater')
        rg.add_rule('#pet', 'ant')
        for _ in range(10):
            assert rg.expand() in ['Ant ant', 'Eater eater']

    def test_allows_context_in_expand(self):
        ctx = {'randomPosition': lambda: 'job type'}

        rg = RiGrammar({'start': 'My $.randomPosition().'}, ctx)
        assert rg.expand() == 'My job type.'

        rg = RiGrammar({'start': 'My $.randomPosition.'}, ctx)
        assert rg.expand() == 'My job type.'

        rg = RiGrammar({'rule': 'My $.randomPosition().'}, ctx)
        assert rg.expand({'start': 'rule'}) == 'My job type.'

        rg = RiGrammar({'start': 'My [].randomPosition().'}, ctx)
        assert rg.expand() == 'My job type.'

        rg = RiGrammar({'start': 'My [].randomPosition.'}, ctx)
        assert rg.expand() == 'My job type.'

    def test_resolves_rules_in_context(self):
        ctx = {'rule': '[job | mob]'}
        rg = RiGrammar({'start': '$rule $rule'}, ctx)
        res = rg.expand()
        assert re.match(r'^[jm]ob [jm]ob$', res)

    def test_handles_custom_transforms(self):
        context = {'randomPosition': lambda: 'job type'}
        rg = RiGrammar({'start': 'My $.randomPosition().'}, context)
        assert rg.expand() == 'My job type.'

    def test_handles_phrases_starting_with_custom_transforms(self):
        context = {'randomPosition': lambda: 'job type'}
        rg = RiGrammar({'start': '$.randomPosition().'}, context)
        assert rg.expand() == 'job type.'

    def test_handles_custom_transforms_with_target(self):
        context = {'randomPosition': lambda z: z + ' job type'}
        rg = RiGrammar({'start': 'My [new].randomPosition().'}, context)
        assert rg.expand() == 'My new job type.'

        context['new'] = 'new'
        rg = RiGrammar({'start': 'My $new.randomPosition.'}, context)
        assert rg.expand() == 'My new job type.'

    def test_handles_paired_assignments_via_transforms(self):
        rules = {
            'start': '$name was our hero and $pronoun was fantastic.',
            'name':  '$boys {$pronoun=he} | $girls {$pronoun=she}',
            'boys':  'Jack | Jack',
            'girls': 'Jill | Jill'
        }
        result = RiGrammar.expand(rules)
        assert result in [
            'Jill was our hero and she was fantastic.',
            'Jack was our hero and he was fantastic.'
        ]

        rules = {
            'start': '$name was our hero and $name was fantastic.',
            '#name': '$boys | $girls',
            'boys':  'Jack | Jake',
            'girls': 'Joan | Jane'
        }
        result = RiGrammar.expand(rules)
        assert result in [
            'Joan was our hero and Joan was fantastic.',
            'Jane was our hero and Jane was fantastic.',
            'Jack was our hero and Jack was fantastic.',
            'Jake was our hero and Jake was fantastic.'
        ]

    def test_handles_symbol_transforms(self):
        rg = RiGrammar({
            'start': '$tmpl',
            'tmpl':  '$jrSr.capitalize()',
            'jrSr':  '[junior|junior]'
        })
        assert rg.expand() == 'Junior'

        rg = RiGrammar({
            'start': '$r.capitalize()',
            'r':     '[a|a]'
        })
        assert rg.expand() == 'A'

        rg = RiGrammar({
            'start': '$r.pluralize()',
            'r':     '[ mouse | mouse ]'
        })
        assert rg.expand() == 'mice'  # mouse -> mice

    def test_handles_symbol_transforms_on_statics(self):
        rg = RiGrammar({
            'start':  '$tmpl',
            '#tmpl':  '$jrSr.capitalize()',
            '#jrSr':  '[junior|junior]'
        })
        assert rg.expand() == 'Junior'

        rg = RiGrammar({
            'start': '$r.capitalize()',
            '#r':    '[a|a]'
        })
        assert rg.expand() == 'A'

        rg = RiGrammar({
            'start': '$r.pluralize() $r',
            '#r':    '[ mouse | ant ]'
        })
        if IfRiTa:
            assert rg.expand() in ['mice mouse', 'ants ant']
        else:
            assert rg.expand() in ['mice mouse', 'ants ant']

    def test_handles_inline_specials(self):
        rg = RiGrammar({
            'start':  '&lcub;$tmpl&rcub;',
            '#tmpl':  '$jrSr.capitalize()',
            '#jrSr':  '[junior|junior]'
        })
        assert rg.expand() == '{Junior}'

        rg = RiGrammar({
            'start':  '\\{$tmpl\\}',
            '#tmpl':  '$jrSr.capitalize()',
            '#jrSr':  '[junior|junior]'
        })
        assert rg.expand() == '{Junior}'

    def test_handles_special_characters(self):
        import json
        s = '{ "start": "hello &#124; name" }'
        rg = RiGrammar.from_json(s)
        assert rg.expand() == 'hello | name'

        s = '{ "start": "hello: name" }'
        rg = RiGrammar.from_json(s)
        assert rg.expand() == 'hello: name'

        s = '{ "start": "&lt;start&gt;" }'
        rg = RiGrammar.from_json(s)
        assert rg.expand() == '<start>'

        s = '{ "start": "I don&#96;t want it." }'
        rg = RiGrammar.from_json(s)
        assert rg.expand() == "I don`t want it."

        s = "{ \"start\": \"&#39;I really don&#39;t&#39;\" }"
        rg = RiGrammar.from_json(s)
        assert rg.expand() == "'I really don't'"

        s = '{ "start": "hello | name" }'
        rg = RiGrammar.from_json(s)
        for _ in range(5):
            res = rg.expand()
            assert res in ('hello', 'name')

    def test_calls_to_from_json(self):
        with pytest.raises(Exception):
            RiGrammar.from_json({'a': 'b'})  # not a string
        with pytest.raises(Exception):
            RiGrammar.from_json('non-JSON string')

        import json
        j = '{ "start": "$pet $iphone", "pet": "[dog | cat]", "iphone": "[iphoneSE | iphone12]" }'
        rg = RiGrammar(json.loads(j))
        gen = rg.toJSON()
        json.loads(gen)  # valid JSON
        rg2 = RiGrammar.from_json(gen)
        assert rg.toString() == rg2.toString()

    def test_correctly_pluralize_phrases(self):
        j = {
            'start': '[$state feeling].pluralize()',
            'state': '[bad | bad]'
        }
        rg = RiGrammar(j)
        assert rg.expand() == 'bad feelings'

    def test_correctly_pluralize_static_phrases(self):
        j = {
            'start':  '[$state feeling].pluralize()',
            '#state': '[bad | bad]'
        }
        rg = RiGrammar(j)
        assert rg.expand() == 'bad feelings'

    def test_should_handle_special_chars_in_grammars(self):
        start = "Meet Sam"

        entity_singles = [
            ('&amp;',    '&'),
            ('&dollar;', '$'),
            ('&vert;',   '|'),
            ('&num;',    '#'),
            ('&period;', '.'),
            ('&bsol;',   '\\'),
            ('&equals;', '='),
            ('&commat;', '@'),
            ('&lpar;',   '('),
            ('&rpar;',   ')'),
            ('&lsqb;',   '['),
            ('&rsqb;',   ']'),
            ('&lcub;',   '{'),
            ('&rcub;',   '}'),
            ('&sol;',    '/'),
            ('&quot;',   '"'),
            ('&apos;',   "'"),
            ('&lt;',     '<'),
            ('&gt;',     '>'),
            ('&#96;',    '`'),
            ('&nbsp;',   ' '),
        ]

        slash_singles = [
            ('\\$',  '$'),
            ('\\(',  '('),
            ('\\)',  ')'),
            ('\\{',  '{'),
            ('\\}',  '}'),
            ('\\[',  '['),
            ('\\]',  ']'),
            ('\\|',  '|'),
            ('\\#',  '#'),
            ('\\.', '.'),
            ('\\=',  '='),
            ('\\@',  '@'),
        ]

        entity_pairs = [
            ('&lpar;', '&rpar;', '(', ')'),
            ('&lsqb;', '&rsqb;', '[', ']'),
            ('&lcub;', '&rcub;', '{', '}'),
        ]

        slash_pairs = [
            ('\\(', '\\)', '(', ')'),
            ('\\[', '\\]', '[', ']'),
            ('\\{', '\\}', '{', '}'),
        ]

        for entity, char in entity_singles:
            rules = {'start': start + entity}
            result = RiGrammar(rules).expand()
            assert result == start + char, f'entity {entity!r}: got {result!r}'

        for slashed, char in slash_singles:
            rules = {'start': start + slashed}
            result = RiGrammar(rules).expand()
            assert result == start + char, f'slash {slashed!r}: got {result!r}'

        for el, er, cl, cr in entity_pairs:
            rules = {'start': el + start + er}
            result = RiGrammar(rules).expand()
            assert result == cl + start + cr

        for sl, sr, cl, cr in slash_pairs:
            rules = {'start': sl + start + sr}
            result = RiGrammar(rules).expand()
            assert result == cl + start + cr

    def test_handles_paired_assignments_with_adj(self):
        # variant that also assigns $adj alongside $pronoun
        rules = {
            'start': '$name was our hero and $pronoun was very $adj.',
            'name':  '$boys {$pronoun=he} {$adj=manly} | $girls {$pronoun=she} {$adj=womanly}',
            'boys':  'Jack | Jack',
            'girls': 'Jill | Jill'
        }
        result = RiGrammar.expand(rules)
        assert result in [
            'Jill was our hero and she was very womanly.',
            'Jack was our hero and he was very manly.'
        ]

    def test_handles_special_characters_with_statics(self):
        """Mirror of test_handles_special_characters but exercises the same
        entities when a static '#' rule is present alongside the start rule."""
        import json

        # &#124; → | (pipe)
        s = '{ "start": "hello &#124; name" }'
        assert RiGrammar.from_json(s).expand() == 'hello | name'

        # hello: name  (colon safe)
        s = '{ "start": "hello: name" }'
        assert RiGrammar.from_json(s).expand() == 'hello: name'

        # &lt; / &gt;
        s = '{ "start": "&lt;start&gt;" }'
        assert RiGrammar.from_json(s).expand() == '<start>'

        # backtick via &#96;
        s = '{ "start": "I don&#96;t want it." }'
        assert RiGrammar.from_json(s).expand() == "I don`t want it."

        # single-quote via &#39;
        s = '{ "start": "&#39;I really don&#39;t&#39;" }'
        assert RiGrammar.from_json(s).expand() == "'I really don't'"

        # plain pipe in JSON value → choice
        s = '{ "start": "hello | name" }'
        rg = RiGrammar.from_json(s)
        for _ in range(5):
            assert rg.expand() in ('hello', 'name')
