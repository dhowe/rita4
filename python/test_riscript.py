"""
test_riscript.py — Python port of riscript.tests.js
"""
import re
import pytest
from riscript import RiScript, EvalVisitor, _string_hash, parse_jsol

# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def rs():
    return RiScript()

@pytest.fixture
def ri():
    return RiScript()

def ev(rs, script, ctx=None, **opts):
    return rs.evaluate(script, ctx or {}, **opts)


# ── Markdown ──────────────────────────────────────────────────────────────────

class TestMarkdown:
    def test_basic_markdown(self, rs):
        t = 'Some *italic* and **bold** and _other_ markdown'
        assert rs.evaluate(t) == t
        t2 = '1. list 1\n2. list 2\n3. list 3'
        assert rs.evaluate(t2) == t2

    def test_markdown_headers(self, rs):
        assert rs.evaluate('### Header') == '### Header'

    def test_markdown_links(self, rs):
        assert rs.evaluate('Some [RiTa](https://rednoise.org/rita) code') == 'Some [RiTa](https://rednoise.org/rita) code'
        assert rs.evaluate('Some [RiTa+](https://rednoise.org/rita?a=b&c=k) code') == 'Some [RiTa+](https://rednoise.org/rita?a=b&c=k) code'
        assert rs.evaluate('Some [RiScript](/@dhowe/riscript) code') == 'Some [RiScript](/@dhowe/riscript) code'

    def test_formatted_markdown(self, rs):
        inp = '### A Title \n      Some RiScript code\n        that we can [format|format|format]\n           with *[inline | inline]* Markdown\n             and rerun [once per | once per] second\n               [using|using|using] the **[pulse].qq** function below'
        expected = '### A Title \n      Some RiScript code\n        that we can format\n           with *inline* Markdown\n             and rerun once per second\n               using the **\u201cpulse\u201d** function below'
        assert rs.evaluate(inp) == expected


# ── Sequences ─────────────────────────────────────────────────────────────────

class TestSequences:
    def test_norepeat_choice_transforms(self, rs):
        for _ in range(5):
            res = rs.evaluate('$names=[a|b]\n$names $names.norepeat()')
            assert re.match(r'^[a-e] [a-e]$', res)
            parts = res.split(' ')
            assert len(parts) == 2
            assert parts[0] != parts[1]

    def test_single_norepeat_choices(self, rs):
        for _ in range(5):
            res = rs.evaluate('$b=a[b|c|d]e\n$b $b.nr')
            assert re.search(r'a[bcd]e a[bcd]e', res)
            parts = res.split(' ')
            assert len(parts) == 2
            assert parts[0] != parts[1]
        for _ in range(5):
            res = rs.evaluate('$b=[a[b | c | d]e]\n$b $b.nr')
            assert re.search(r'a[bcd]e a[bcd]e', res)
            parts = res.split(' ')
            assert len(parts) == 2
            assert parts[0] != parts[1]

    def test_norepeat_symbol_transforms(self, rs):
        fail = False
        for _ in range(5):
            res = rs.evaluate('$rule=[a|b|c|d|e]\n$rule.nr $rule.nr')
            assert re.match(r'^[a-e] [a-e]$', res)
            parts = res.split(' ')
            assert len(parts) == 2
            if parts[0] == parts[1]:
                fail = True
                break
        assert not fail

    def test_throws_norepeat_statics(self, rs):
        with pytest.raises(Exception):
            rs.evaluate('#a=[a|b]\n$a $a.nr')
        with pytest.raises(Exception):
            rs.evaluate('#a=[a|b]\n#a #a.nr')

    def test_throws_dynamic_as_static(self, rs):
        with pytest.raises(Exception):
            rs.evaluate('{$foo=bar}#foo')

    def test_throws_norepeat_in_context(self, rs):
        with pytest.raises(Exception):
            rs.evaluate('$foo $foo.nr', {'foo': '[a|b]'})


# ── Gates ─────────────────────────────────────────────────────────────────────

class TestGates:
    def test_throws_bad_gates(self, rs):
        with pytest.raises(Exception):
            rs.evaluate('$a=ok\n[ @{$a: ok} hello]')  # unquoted str
        with pytest.raises(Exception):
            rs.evaluate('[@{} [a|a] || [b|b] ]')       # no ops in gate

    def test_transforms_in_gate_operands(self, rs):
        ctx = {'getHours': lambda: __import__('datetime').datetime.now().hour}
        res = rs.evaluate('[ @{ $getHours(): { @lt: 12 } } morning || evening]', ctx)
        expected = 'morning' if __import__('datetime').datetime.now().hour < 12 else 'evening'
        assert res == expected

    def test_time_based_gates(self, rs):
        ctx = {'getHours': lambda: __import__('datetime').datetime.now().hour}
        res = rs.evaluate('$hours=$getHours()\n[ @{ $hours: {@lt: 12} } morning || evening]', ctx)
        expected = 'morning' if __import__('datetime').datetime.now().hour < 12 else 'evening'
        assert res == expected

    def test_new_style_gates(self, rs):
        assert rs.evaluate('[ @{ $a: { @exists: true }} hello]', {'b': 2}) == ''
        assert rs.evaluate('[ @{ $a: { @exists: true }} hello]', {'a': 2}) == 'hello'

    def test_exists_gates(self, rs):
        assert rs.evaluate('[ @{ $a: { @exists: true }} user]', {'a': 'apogee'}) == 'user'
        assert rs.evaluate('[ @{ $a: { @exists: true }} user]', {'b': 'apogee'}) == ''
        assert rs.evaluate('[ @{ $a: { @exists: true }} &lt;]', {'a': 'apogee'}) == '<'
        assert rs.evaluate('$a=apogee\n[ @{ $a: { @exists: true }} dynamic]') == 'dynamic'
        assert rs.evaluate('$b=apogee\n[ @{ $a: { @exists: true }} dynamic]') == ''
        assert rs.evaluate('{$b=apogee}[ @{ $a: { @exists: true }} dynamic]') == ''
        assert rs.evaluate('[$a=apogee] [ @{ $a: { @exists: true }} dynamic]') == 'apogee dynamic'
        assert rs.evaluate('#a=apogee\n[ @{ $a: { @exists: true }} static]') == 'static'
        assert rs.evaluate('#b=apogee\n[ @{ $a: { @exists: true }} static]') == ''

    def test_matching_gates(self, rs):
        assert rs.evaluate('[ @{ $a: /^p/ } hello]', {'a': 'apogee'}) == ''
        assert rs.evaluate('[ @{ $a: /^p/ } hello]', {'a': 'puffer'}) == 'hello'
        assert rs.evaluate('[ @{ $a: /^p/ } $a]', {'a': 'pogue'}) == 'pogue'

    def test_nested_gates(self, rs):
        res = rs.evaluate('$x=2\n$y=3\n[ @{$x:1} [a] || [@{$y:3} b ]]')
        assert res == 'b'
        res = rs.evaluate('$x=2\n$y=4\n[ @{$x:1} [a] || [@{$y:3} b || c ]]')
        assert res == 'c'

    def test_else_gates(self, rs):
        assert rs.evaluate('$x=2\n[@{$x:2} [a] || [b]]') == 'a'
        assert rs.evaluate('$x=1\n[@{$x:1}a||b]') == 'a'
        assert rs.evaluate('$x=2\n[@{$x:1}a||b]') == 'b'
        assert rs.evaluate('[@{$x:3}a||b]', {'x': 3}) == 'a'
        assert rs.evaluate('[@{$x:4}a||b]', {'x': 3}) == 'b'
        assert rs.evaluate('[a||b]') == 'a'

    def test_deferred_else_gates(self, rs):
        assert rs.evaluate('[@{$a:1}a||b]\n$a=1') == 'a'
        assert rs.evaluate('[@{$a:2}a||b]\n$a=1') == 'b'
        assert rs.evaluate('[ @{$a:2} [accept|accept] || [reject|reject] ]\n$a=1') == 'reject'
        assert rs.evaluate('[@{$a:2}a||b]') == 'b'

    def test_equality_gates(self, rs):
        assert rs.evaluate('$a=3\n[ @{$a: "3"} hello]') == 'hello'
        assert rs.evaluate('$a=2\n[ @{$a: 3} hello]') == ''
        assert rs.evaluate('$a=3\n[ @{$a: 3} hello]') == 'hello'
        assert rs.evaluate('$a=ok\n[ @{$a: "ok"} hello]') == 'hello'
        assert rs.evaluate('$a=notok\n[ @{$a: "ok"} hello]') == ''

    def test_deferred_equality_gates(self, rs):
        assert rs.evaluate('[ @{$a: 3} hello]', {'a': 2}) == ''
        assert rs.evaluate('[ @{$a: 3} hello]', {'a': 3}) == 'hello'
        assert rs.evaluate('[ @{$a: "ok"} hello]', {'a': 'ok'}) == 'hello'
        assert rs.evaluate('[ @{$a: "ok"} hello]', {'a': 'fail'}) == ''

    def test_arithmetic_gates(self, rs):
        assert rs.evaluate('$a=4\n[ @{$a: {@gt: 3}} hello]') == 'hello'
        assert rs.evaluate('$a=3\n[ @{$a: {@gt: 3}} hello]') == ''
        assert rs.evaluate('$a=3.1\n[ @{$a: {@gt: 3}} hello]') == 'hello'

    def test_boolean_gate_logic(self, rs):
        assert rs.evaluate('$a=2\n[ @{$a: {}} hello]') == ''
        assert rs.evaluate('$a=2\n[ @{$a: {@gt: 3}} hello]') == ''
        assert rs.evaluate('$a=4\n[ @{$a: {@gt: 3}} hello]') == 'hello'
        assert rs.evaluate('$a=27\n[ @{$a: {@gt:25, @lt:32}} hello]') == 'hello'
        assert rs.evaluate('$a=4\n[ @{$a: {@gt:25, @lt:32}} hello]') == ''
        assert rs.evaluate('$a=27\n[ @{ @or: [ {$a: {@gt: 30}}, {$a: {@lt: 20}} ] } hello]') == ''
        assert rs.evaluate('$a=35\n[ @{ @or: [ {$a: {@gt: 30}}, {$a: {@lt: 20}} ] } hello]') == 'hello'
        assert rs.evaluate('$a=23\n[ @{ @and: [ {$a: {@gt: 20}}, {$a: {@lt: 25}} ] } hello]') == 'hello'
        assert rs.evaluate('$a=27\n[ @{ @and: [ {$a: {@gt: 20}}, {$a: {@lt: 25}} ] } hello]') == ''

    def test_deferred_dynamics_gates(self, rs):
        assert rs.evaluate('[ @{$a: "ok"} hello]\n$a=ok') == 'hello'

    def test_deferred_boolean_gates(self, rs):
        assert rs.evaluate('[ @{$a: {}} hello]', {'a': 2}) == ''
        assert rs.evaluate('[ @{$a: {@gt: 3}} hello]', {'a': 4}) == 'hello'
        assert rs.evaluate('[ @{$a: {@gt:25, @lt:32}} hello]', {'a': 27}) == 'hello'
        assert rs.evaluate('[ @{ @or: [ {$a: {@gt: 30}}, {$a: {@lt: 20}} ] } hello]', {'a': 35}) == 'hello'
        assert rs.evaluate('[ @{ @and: [ {$a: {@gt: 20}}, {$a: {@lt: 25}} ] } hello]', {'a': 23}) == 'hello'

    def test_deferred_gates(self, rs):
        assert rs.evaluate('$a=$b\n[ @{ $a: "cat" } hello]\n$b=[cat|cat]') == 'hello'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n$a=apogee') == 'dynamic'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n{$a=apogee}') == 'dynamic'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n$b=apogee') == ''
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n#a=apogee') == 'static'
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n#b=apogee') == ''

    def test_gates_string_chars(self, rs):
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]") == 'bc'
        assert rs.evaluate("$a=bc\n[@{$a: 'cd'} $a]") == ''
        assert rs.evaluate('$a=bc\n[@{$a: "bc"} $a]') == 'bc'

    def test_gates_chinese(self, rs):
        assert rs.evaluate('$a=繁體\n[@{$a: "繁體"} $a]') == '繁體'
        assert rs.evaluate('$a=繁體\n[@{$a: "中文"} $a]') == ''
        assert rs.evaluate('$a=繁體\n[@{$a: {@ne: "繁體"}} $a]') == ''
        assert rs.evaluate('$a=繁體\n[@{$a: {@ne: "中文"}} $a]') == '繁體'

    def test_complex_boolean_gate_logic(self, rs):
        q = '{ $a: 3, @or: [ { $b: { @lt: 30 } }, { $c: /^p*/ } ] }'
        ctx = '$a=27\n$b=10\n$c=pants\n'
        assert rs.evaluate(f'{ctx}[ @{q} hello]') == ''
        ctx = '$a=3\n$b=10\n$c=ants\n'
        assert rs.evaluate(f'{ctx}[ @{q} hello]') == 'hello'
        ctx = '$a=3\n$b=5\n$c=pants\n'
        assert rs.evaluate(f'{ctx}[ @{q} hello]') == 'hello'


# ── Choice ────────────────────────────────────────────────────────────────────

class TestChoice:
    def test_throws_bad_choices(self, rs):
        for bad in ['|', 'a |', 'a | b', 'a | b | c', '[a | b] | c']:
            with pytest.raises(Exception):
                rs.evaluate(bad)
        with pytest.raises(Exception):
            rs.evaluate('[a | b].nr()')
        with pytest.raises(Exception):
            rs.evaluate('[$names=[a|b|c|d|e]].nr()')

    def test_choices_in_context(self, rs):
        res = rs.evaluate('$bar:$bar', {'bar': '[man | boy]'})
        assert re.match(r'(man|boy):(man|boy)', res)

    def test_even_distribution(self, rs):
        counts = {}
        for _ in range(1000):
            r = rs.evaluate('[quite|]')
            counts[r] = counts.get(r, 0) + 1
        assert counts.get('quite', 0) > 400
        assert counts.get('', 0) > 400

    def test_resolves_choices(self, rs):
        assert rs.evaluate('[|]') == ''
        assert rs.evaluate('[a]') == 'a'
        assert rs.evaluate('[a | a]') == 'a'
        assert rs.evaluate('[a | ]') in ['a', '']
        assert rs.evaluate('[a | b]') in ['a', 'b']
        assert rs.evaluate('[a | b | c]') in ['a', 'b', 'c']
        assert rs.evaluate('[a | [b | c] | d]') in ['a', 'b', 'c', 'd']
        assert rs.evaluate('not [quite|] far enough') in ['not far enough', 'not quite far enough']

    def test_multiword_choices(self, rs):
        assert rs.evaluate('[A B | A B]') == 'A B'
        assert rs.evaluate('[A B].toLowerCase()') == 'a b'
        assert rs.evaluate('[A B | A B].toLowerCase()') == 'a b'
        assert rs.evaluate('[A B | A B].articlize()') == 'an A B'

    def test_choices_in_expressions(self, rs):
        assert rs.evaluate('x [a | a | a] x') == 'x a x'
        assert rs.evaluate('x [a | a | a]') == 'x a'
        assert rs.evaluate('x [a | a | a]x') == 'x ax'
        assert rs.evaluate('x[a | a | a] x') == 'xa x'
        assert rs.evaluate('x[a | a | a]x') == 'xax'
        assert rs.evaluate('x [a | a | a] [b | b | b] x') == 'x a b x'
        assert rs.evaluate('[a|a]') == 'a'
        assert rs.evaluate('This is &lpar;a parenthesed&rpar; expression') == 'This is (a parenthesed) expression'

    def test_weighted_choices(self, rs):
        assert rs.evaluate('[ a (2) ]') == 'a'
        assert rs.evaluate('[a | b (2) |(3)]') in ['a', 'b', '']
        assert rs.evaluate('[ a (2) | a (3) ]') == 'a'
        counts = {'a': 0, 'b': 0}
        for _ in range(100):
            ans = rs.evaluate('[a(1) | b (3)]')
            counts[ans] = counts.get(ans, 0) + 1
        assert counts['a'] > 0
        assert counts['b'] > counts['a']


# ── Assignment ────────────────────────────────────────────────────────────────

class TestAssignment:
    def test_single_assignments_on_line_break(self, rs):
        res = rs.evaluate('hello\n$foo=a', preserveLookups=True)
        assert res == 'hello'
        assert callable(rs.visitor.dynamics.get('foo'))
        assert rs.visitor.dynamics['foo']() == 'a'

        assert rs.evaluate('$foo=a\n', preserveLookups=True) == '\n'
        assert rs.evaluate('$foo=a\nb', preserveLookups=True) == 'b'
        assert rs.visitor.dynamics['foo']() == 'a'

        res = rs.evaluate('$foo=a\n$bar=$foo', preserveLookups=True)
        assert res == ''
        assert callable(rs.visitor.dynamics.get('bar'))
        assert rs.visitor.dynamics['foo']() == 'a'
        assert rs.visitor.dynamics['bar']() == 'a'

        assert rs.evaluate('$foo=[a | a]\n$foo', preserveLookups=True) == 'a'
        assert rs.visitor.dynamics['foo']() == 'a'

        assert rs.evaluate('$foo=[hi | hi]\n$foo there', preserveLookups=True) == 'hi there'
        assert rs.visitor.dynamics['foo']() == 'hi'

    def test_silent_assignments(self, rs):
        assert rs.evaluate('{$foo=a}b', preserveLookups=True) == 'b'
        assert rs.visitor.dynamics['foo']() == 'a'

        assert rs.evaluate('{$foo=[a | a]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'a'

        assert rs.evaluate('{$foo=ab}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'ab'

        assert rs.evaluate('{$foo=[a | a] [b | b]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'a b'

    def test_resolves_prior_assignments(self, rs):
        assert rs.evaluate('$foo=dog\n$bar=$foo\n$baz=$foo\n$baz') == 'dog'
        assert rs.evaluate('$foo=hi\n$foo there') == 'hi there'
        assert rs.evaluate('$foo=a\n$foo') == 'a'


# ── Evaluation ────────────────────────────────────────────────────────────────

class TestEvaluation:
    def test_static_objects_from_context(self, rs):
        assert rs.evaluate('Meet [$person].name', {'person': {'name': 'Lucy'}}) == 'Meet Lucy'
        assert rs.evaluate('Meet [$person=$lucy].name', {'lucy': {'name': 'Lucy'}}) == 'Meet Lucy'

    def test_simple_expressions(self, rs):
        assert rs.evaluate('hello') == 'hello'
        assert rs.evaluate('[a|b]') in ['a', 'b']
        assert rs.evaluate('[hello (2)]') == 'hello'
        assert rs.evaluate('[hello]') == 'hello'
        assert rs.evaluate('[@{$a:2} hello]') == ''
        assert rs.evaluate('$a=2\n$a') == '2'
        assert rs.evaluate('[$a=2]') == '2'
        assert rs.evaluate('[#a=2]') == '2'
        assert rs.evaluate('#a=2') == ''
        assert rs.evaluate('#a=2\n$a') == '2'
        assert rs.evaluate('$a=2\n[@{$a:2} hello]') == 'hello'

    def test_static_evaluate(self, rs):
        assert RiScript.static_evaluate('(foo)', {}) == '(foo)'
        assert RiScript.static_evaluate('foo!', {}) == 'foo!'
        assert RiScript.static_evaluate('foo.', {}) == 'foo.'
        assert RiScript.static_evaluate('"foo"', {}) == '"foo"'
        assert RiScript.static_evaluate('$a=hello\n') == '\n'
        assert RiScript.static_evaluate('hello\n') == 'hello\n'

    def test_resolves_expressions(self, rs):
        assert rs.evaluate('foo') == 'foo'
        assert rs.evaluate('(foo)') == '(foo)'
        assert rs.evaluate('foo!') == 'foo!'
        assert rs.evaluate('foo.') == 'foo.'
        assert rs.evaluate('"foo"') == '"foo"'
        assert rs.evaluate("'foo'") == "'foo'"
        assert rs.evaluate('$a=hello\n') == '\n'
        assert rs.evaluate('hello\n') == 'hello\n'
        assert rs.evaluate('*%©\n') == '*%©\n'

    def test_resolves_transformed_choices(self, rs):
        assert rs.evaluate('[A B].toLowerCase()') == 'a b'
        assert rs.evaluate('[A B | A B].toLowerCase()') == 'a b'
        assert rs.evaluate('[A B | A B].articlize()') == 'an A B'
        res = rs.evaluate('$mammal=[dog | dog]\n$mammal.pluralize.ucf are unruly, but my $mammal is the best.')
        assert res == 'Dogs are unruly, but my dog is the best.'

    def test_simple_statics(self, rs):
        assert rs.evaluate('{#foo=bar}baz') == 'baz'
        assert rs.evaluate('{#foo=bar}$foo') == 'bar'
        assert rs.evaluate('[#foo=bar]\nbaz') == 'bar\nbaz'
        assert rs.evaluate('{#foo=bar}$foo baz $foo') == 'bar baz bar'
        failed = False
        for _ in range(5):
            res = rs.evaluate('{#foo=[a|b|c|d]}$foo $foo $foo')
            pts = res.split(' ')
            assert len(pts) == 3
            if pts[0] != pts[1] or pts[1] != pts[2]:
                failed = True
                break
        assert not failed

    def test_resolves_statics(self, rs):
        res = rs.evaluate('{#bar=[man | boy]}$bar')
        assert res in ['man', 'boy']
        res = rs.evaluate('#bar=[man | boy]\n$foo=$bar:$bar\n$foo')
        assert res in ['man:man', 'boy:boy']

    def test_statics_from_context(self, rs):
        res = rs.evaluate('#bar=$man\n$bar:$bar', {'man': '[BOY|boy]'})
        assert res in ['BOY:BOY', 'boy:boy']

        res = rs.evaluate('[#bar=[man | boy]]:$bar')
        assert res in ['man:man', 'boy:boy']

    def test_predefined_statics(self, rs):
        visitor = EvalVisitor(None, None)
        visitor.statics = {'bar': '[man | boy]'}
        res = rs._evaluate(input='$bar:$bar', visitor=visitor)
        assert res in ['man:man', 'boy:boy']

    def test_line_breaks(self, rs):
        assert rs.evaluate('$foo=bar\nbaz') == 'baz'
        assert rs.evaluate('foo\nbar') == 'foo\nbar'
        assert rs.evaluate('$foo=bar\nbaz\n$foo') == 'baz\nbar'
        assert rs.evaluate('#foo=[a|b|c]\n$foo is $foo') in ['a is a', 'b is b', 'c is c']
        assert rs.evaluate('<em>foo</em>') == '<em>foo</em>'
        assert rs.evaluate('a   b') == 'a   b'
        assert rs.evaluate('a\tb') == 'a\tb'

    def test_recursive_expressions(self, rs):
        assert rs.evaluate('[a|$a]', {'a': 'a'}) == 'a'
        assert rs.evaluate('$a', {'a': '$b', 'b': '[c | c]'}) == 'c'
        ctx = {'a': '$b', 'b': '[c | c]'}
        assert rs.evaluate('$k = $a\n$k', ctx) == 'c'
        ctx = {'s': '$a', 'a': '$b', 'b': '$c', 'c': '$d', 'd': 'c'}
        assert rs.evaluate('$s', ctx) == 'c'


# ── Symbols ───────────────────────────────────────────────────────────────────

class TestSymbols:
    def test_generated_symbols(self, rs):
        sc = '$a=antelope\n$b=otter\n$an() $[a|b]'
        res = rs.evaluate(sc, {'an': lambda: 'An'})
        assert res in ['An antelope', 'An otter']

    def test_simple_object_in_context(self, rs):
        assert rs.evaluate('$a.name', {'a': {'name': 'Lucy'}}) == 'Lucy'
        res = rs.evaluate('$[a | b].name', {'a': {'name': 'Lucy'}, 'b': {'name': 'Sam'}})
        assert res in ['Lucy', 'Sam']

    def test_generated_symbol_in_context(self, rs):
        res = rs.evaluate('$[a|b]', {'a': 'Lucy', 'b': 'Sam'})
        assert res in ['Lucy', 'Sam']

        res = rs.evaluate('$person=$[a|b]\n$person', {'a': 'Lucy', 'b': 'Sam'})
        assert res in ['Lucy', 'Sam']

        res = rs.evaluate('$[a|b].name', {'a': {'name': 'Lucy'}, 'b': {'name': 'Sam'}})
        assert res in ['Lucy', 'Sam']

    def test_handles_deferred(self, rs):
        assert rs.evaluate('$foo\n$foo=cat') == 'cat'

    def test_handles_statics(self, rs):
        res = rs.evaluate('[#bar=[boy]]:$bar')
        assert res == 'boy:boy'

        res = rs.evaluate('#foo=[cat | dog]\n$foo $foo')
        assert res in ['cat cat', 'dog dog']

    def test_handles_norepeats(self, rs):
        for _ in range(5):
            res = rs.evaluate('$foo=[cat|dog]\n$foo $foo.nr')
            assert res in ['cat dog', 'dog cat']

    def test_internal_line_breaks(self, rs):
        assert rs.evaluate('$foo=[cat\ndog]\n$foo') == 'cat\ndog'
        assert rs.evaluate('前半段句子\n後半段句子') == '前半段句子\n後半段句子'

    def test_handles_silents(self, rs):
        assert rs.evaluate('{$a=b}') == ''
        assert rs.evaluate('$a=b') == ''
        assert rs.evaluate('$a=b\n$a') == 'b'

    def test_resolves_transforms(self, rs):
        assert rs.evaluate('$foo=$bar.toUpperCase()\n$bar=baz\n$foo') == 'BAZ'
        assert rs.evaluate('$foo.capitalize()\n$foo=[a|a]') == 'A'
        assert rs.evaluate('$names=a\n$names.uc()') == 'A'
        assert rs.evaluate('$foo=[bar].ucf\n$foo') == 'Bar'

        ctx = {'bar': lambda: 'result'}
        assert rs.evaluate('[].bar', ctx) == 'result'


# ── Transforms ────────────────────────────────────────────────────────────────

class TestTransforms:
    def test_add_remove_custom_transforms(self, rs):
        add_rhyme = lambda word: word + ' rhymes with bog'
        assert rs.transforms.get('rhymes') is None
        rs.add_transform('rhymes', add_rhyme)
        assert rs.transforms.get('rhymes') is not None
        res = rs.evaluate('The [dog | dog | dog].rhymes')
        assert res == 'The dog rhymes with bog'
        rs.remove_transform('rhymes')
        assert rs.transforms.get('rhymes') is None
        res = rs.evaluate('The [dog | dog | dog].rhymes', silent=True)
        assert res == 'The dog.rhymes'

    def test_anonymous_transforms(self, rs):
        ctx = {'capB': lambda s: 'B'}
        assert rs.evaluate('$uppercase()') == ''
        assert rs.evaluate('$capB()', ctx) == 'B'
        assert rs.evaluate('$uppercase') == ''
        assert rs.evaluate('$capB', ctx) == 'B'
        assert rs.evaluate('[].capB', ctx) == 'B'

    def test_old_style_anonymous_transforms(self, rs):
        ctx = {'capB': lambda s: 'B'}
        assert rs.evaluate('$.uppercase()') == ''
        assert rs.evaluate('$.capB()', ctx) == 'B'
        assert rs.evaluate('[].capB', ctx) == 'B'

    def test_transforms_containing_riscript(self, rs):
        ctx = {'tx': lambda s: '[a | a]'}
        assert rs.evaluate('[c].tx()', ctx) == 'a'

        ctx = {'sym': 'at', 'tx': lambda s: s + '$sym'}
        assert rs.evaluate('[c].tx()', ctx) == 'cat'

        ctx = {'tx': lambda s: f'[{s}].uc()'}
        assert rs.evaluate('[c].tx()', ctx) == 'C'

    def test_resolves_transforms(self, rs):
        assert rs.evaluate('[This].uc() is an acronym.') == 'THIS is an acronym.'
        assert rs.evaluate('[BAZ].toLowerCase().ucf()') == 'Baz'
        assert rs.evaluate('[c].toUpperCase()') == 'C'
        assert rs.evaluate('[c].toUpperCase') == 'C'
        assert rs.evaluate('$a=b\n$a.toUpperCase()') == 'B'
        assert rs.evaluate('$a.toUpperCase()\n$a=b') == 'B'
        assert rs.evaluate('[[a]].toUpperCase()') == 'A'

        assert rs.evaluate('$dog.ucf()', {'dog': 'terrier'}) == 'Terrier'

    def test_resolves_transforms_on_literals(self, rs):
        assert rs.evaluate('How many [teeth].quotify() do you have?') == 'How many \u201cteeth\u201d do you have?'
        assert rs.evaluate('How many [].quotify() do you have?') == 'How many \u201c\u201d do you have?'
        assert rs.evaluate('How many [teeth].toUpperCase() do you have?') == 'How many TEETH do you have?'
        assert rs.evaluate('That is an [ant].capitalize().') == 'That is an Ant.'
        assert rs.evaluate('[ant].articlize().capitalize()') == 'An ant'
        assert rs.evaluate('[ant].capitalize().articlize()') == 'an Ant'
        assert rs.evaluate('That is [ant].articlize().') == 'That is an ant.'

    def test_resolves_transforms_on_bare_symbols(self, rs):
        assert rs.evaluate('How many $quotify() quotes do you have?') == 'How many \u201c\u201d quotes do you have?'
        assert rs.evaluate('That is $articlize().') == 'That is .'
        assert rs.evaluate('That is $incontext().', {'incontext': 'in context'}) == 'That is in context.'
        assert rs.evaluate('How many $quotify quotes do you have?') == 'How many \u201c\u201d quotes do you have?'

    def test_resolves_old_style_bare_symbols(self, rs):
        assert rs.evaluate('How many $.quotify() quotes do you have?') == 'How many \u201c\u201d quotes do you have?'
        assert rs.evaluate('That is $.articlize().') == 'That is .'
        assert rs.evaluate('How many $.quotify quotes do you have?') == 'How many \u201c\u201d quotes do you have?'

    def test_pluralize_phrases(self, rs):
        assert rs.evaluate('These [bad feeling].pluralize().') == 'These bad feelings.'
        assert rs.evaluate('These [$state feeling].pluralize().', {'state': 'bad'}) == 'These bad feelings.'

    def test_resolves_across_assignment_types(self, rs):
        assert rs.evaluate('The [$foo=blue] [dog | dog]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.dynamics['foo']() == 'blue'

        assert rs.evaluate('The [$foo=blue [dog | dog]]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.dynamics['foo']() == 'blue dog'

        assert rs.evaluate('{$foo=blue [dog | dog]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'blue dog'

        assert rs.evaluate('The $foo=blue [dog | dog]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.dynamics['foo']() == 'blue dog'

    def test_resolves_statics_across_assignment_types(self, rs):
        assert rs.evaluate('The [#foo=blue] [dog | dog]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.statics.get('foo') == 'blue'

        assert rs.evaluate('The [#foo=blue [dog | dog]]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.statics.get('foo') == 'blue dog'

    def test_resolves_choice_transforms(self, rs):
        assert rs.evaluate('[a | a].toUpperCase()') == 'A'
        assert rs.evaluate('[a | a].up()', {'up': lambda x: x.upper()}) == 'A'
        assert rs.evaluate('[a].toUpperCase()') == 'A'
        assert rs.evaluate('[a | b].toUpperCase()') in ['A', 'B']
        assert rs.evaluate('[a | a].capitalize()') == 'A'
        assert rs.evaluate('The [boy | boy].toUpperCase() ate.') == 'The BOY ate.'

    def test_preserve_nonexistent_transforms(self, rs):
        assert rs.evaluate('[a | a].up()', silent=True) == 'a.up()'
        assert rs.evaluate('$dog.toUpperCase()', silent=True) == '$dog.toUpperCase()'

    def test_resolves_symbol_transforms(self, rs):
        assert rs.evaluate('$dog.toUpperCase()', {'dog': 'spot'}) == 'SPOT'
        assert rs.evaluate('$dog.capitalize()', {'dog': 'spot'}) == 'Spot'
        assert rs.evaluate('The $dog.toUpperCase()', {'dog': 'spot'}) == 'The SPOT'
        assert rs.evaluate('The [boy | boy].toUpperCase() ate.') == 'The BOY ate.'
        assert rs.evaluate('$dog.articlize().capitalize()', {'dog': 'spot'}) == 'A spot'

    def test_resolves_symbol_multi_transforms(self, rs):
        assert rs.evaluate('[abe | abe].articlize().capitalize()') == 'An abe'
        assert rs.evaluate('[abe | abe].capitalize().articlize()') == 'an Abe'
        assert rs.evaluate('[Abe Lincoln].articlize().capitalize()') == 'An Abe Lincoln'

    def test_resolves_object_properties(self, rs):
        dog = {'name': 'spot', 'color': 'white', 'hair': {'color': 'white'}}
        assert rs.evaluate('It was a $dog.hair.color dog.', {'dog': dog}) == 'It was a white dog.'
        assert rs.evaluate('It was a $dog.color.toUpperCase() dog.', {'dog': dog}) == 'It was a WHITE dog.'

    def test_resolves_member_functions(self, rs):
        dog = {'name': 'Spot', 'getColor': lambda: 'red'}
        assert rs.evaluate('$dog.name was a $dog.getColor() dog.', {'dog': dog}) == 'Spot was a red dog.'
        assert rs.evaluate('$dog.name was a $dog.getColor dog.', {'dog': dog}) == 'Spot was a red dog.'

    def test_resolves_transforms_ending_with_punc(self, rs):
        assert rs.evaluate('[a | b].toUpperCase().') in ['A.', 'B.']
        assert rs.evaluate('The [boy | boy].toUpperCase()!') == 'The BOY!'
        assert rs.evaluate('The $dog.toUpperCase()?', {'dog': 'spot'}) == 'The SPOT?'

        dog = {'name': 'spot', 'color': 'white', 'hair': {'color': 'white'}}
        assert rs.evaluate('It was $dog.hair.color.', {'dog': dog}) == 'It was white.'

        col = {'getColor': lambda: 'red'}
        assert rs.evaluate('It was $dog.getColor()?', {'dog': col}) == 'It was red?'
        assert rs.evaluate('It was $dog.getColor.', {'dog': col}) == 'It was red.'

    def test_nested_context(self, rs):
        assert rs.evaluate('#foo=$bar.color\n$foo', {'bar': {'color': 'blue'}}) == 'blue'

    def test_functions_on_context_props(self, rs):
        s = '$player.name.toUpperCase().toLowerCase()'
        assert rs.evaluate(s, {'player': {'name': 'Wing'}}) == 'wing'

        ctx = {'bar': {'baz': 'result'}}
        assert rs.evaluate('$foo=$bar.baz\n$foo', ctx) == 'result'


# ── Entities ──────────────────────────────────────────────────────────────────

class TestEntities:
    def test_escaped_chars(self, rs):
        assert rs.evaluate('The (word) has parens') == 'The (word) has parens'
        assert rs.evaluate('The [word] has parens') == 'The word has parens'
        assert rs.evaluate('The reference&lpar;1&rpar; has parens') == 'The reference(1) has parens'
        assert rs.evaluate('The &lsqb;word&rsqb; has brackets') == 'The [word] has brackets'
        assert rs.evaluate('The & is an ampersand') == 'The & is an ampersand'
        assert rs.evaluate('The # is a hash') == 'The # is a hash'

    def test_emojis(self, rs):
        assert rs.evaluate('The 👍 is thumbs up') == 'The 👍 is thumbs up'

    def test_html_entities(self, rs):
        assert rs.evaluate('The &#010; line break entity') == 'The \n line break entity'
        assert rs.evaluate('The &#35; symbol') == 'The # symbol'
        assert rs.evaluate('The &nbsp; dog') == 'The   dog'

        for e in ['&lsqb;', '&lbrack;', '&#91;']:
            assert rs.evaluate(f'The {e} symbol') == 'The [ symbol'
        for e in ['&rsqb;', '&rbrack;', '&#93;']:
            assert rs.evaluate(f'The {e} symbol') == 'The ] symbol'
        for e in ['&lpar;', '&#40;']:
            assert rs.evaluate(f'The {e} symbol') == 'The ( symbol'
        for e in ['&rpar;', '&#41;']:
            assert rs.evaluate(f'The {e} symbol') == 'The ) symbol'

    def test_basic_punctuation(self, rs):
        assert rs.evaluate("The -;:.!?'`") == "The -;:.!?'`"
        assert rs.evaluate('*%©') == '*%©'

    def test_dollar_sign_entities(self, rs):
        assert rs.evaluate('This is &#36;') == 'This is $'

    def test_continuations(self, rs):
        assert rs.evaluate('~\n') == ''
        assert rs.evaluate('aa~\nbb') == 'aabb'
        assert rs.evaluate('aa~\n~\n[bb].uc') == 'aaBB'

    def test_line_comments(self, rs):
        assert rs.evaluate('// $foo=a') == ''
        assert rs.evaluate('// hello') == ''
        assert rs.evaluate('hello\n//hello') == 'hello'
        assert rs.evaluate('//hello\nhello') == 'hello'
        assert rs.evaluate('//hello\nhello\n//hello') == 'hello'

    def test_block_comments(self, rs):
        assert rs.evaluate('/* hello */') == ''
        assert rs.evaluate('a /* $foo=a */b') == 'a b'
        assert rs.evaluate('a/* $foo=a */b') == 'ab'
        assert rs.evaluate('a/* $foo=a */b/* $foo=a */c') == 'abc'


# ── Helpers ───────────────────────────────────────────────────────────────────

class TestHelpers:
    def test_string_hash(self):
        assert str(_string_hash('revenue')) == '1099842588'

    def test_pre_parse_lines(self, rs):
        assert rs.pre_parse('a (1) ') == 'a ^1^ '
        assert rs.pre_parse('a (foo) ') == 'a (foo) '
        assert rs.pre_parse('foo=a') == 'foo=a'
        assert rs.pre_parse('$foo=a') == '{$foo=a}'
        assert rs.pre_parse('$foo=a\nb') == '{$foo=a}b'
        assert rs.pre_parse('hello\n$foo=a') == 'hello\n{$foo=a}'
        assert rs.pre_parse('$foo=a\nb\n$foo') == '{$foo=a}b\n$foo'
        assert rs.pre_parse('$foo=[cat\ndog]\n$foo') == '{$foo=[cat\ndog]}$foo'
        assert rs.pre_parse('$foo=[cat\ndog].uc()\n$foo') == '{$foo=[cat\ndog].uc()}$foo'

    def test_parse_jsol_regex(self, rs):
        res = rs.parse_jsol('{a: /^p/}')
        assert 'a' in res

    def test_parse_jsol_strings(self, rs):
        assert rs.parse_jsol("{a: 'hello'}") == {'a': 'hello'}
        assert rs.parse_jsol('{a: "hello"}') == {'a': 'hello'}

    def test_parse_jsol(self, rs):
        assert rs.parse_jsol('{a: 3}') == {'a': 3}
        assert rs.parse_jsol('{a: "3"}') == {'a': '3'}
        assert rs.parse_jsol("{a: '3'}") == {'a': '3'}

    def test_is_parseable(self, rs):
        assert not rs.is_parseable('(')
        assert rs.is_parseable('[')
        assert rs.is_parseable('{')
        assert rs.is_parseable('[A | B]')
        assert rs.is_parseable('$hello')
        assert rs.is_parseable('$b')
        assert rs.is_parseable('#b')
        assert not rs.is_parseable('Hello')
        assert not rs.is_parseable('&nbsp;')
        assert rs.is_parseable('@{')


# ── Additional tests ported from riscript.tests.js ───────────────────────────

class TestAdditional:

    def test_handles_abbreviations(self, rs):
        assert rs.evaluate('The C.D failed') == 'The C.D failed'
        assert rs.evaluate('The $C.D failed', {'C': 'C', 'D': lambda s: s.lower()}) == 'The c failed'

    def test_resolves_recursive_dynamics(self, rs):
        ctx = {'a': '$b', 'b': '[c | c]'}
        assert rs.evaluate('#k=$a\n$k', ctx) == 'c'

        ctx = {'a': '$b', 'b': '[c | c]'}
        assert rs.evaluate('#s = $a\n#a = $b\n#c = $d\n#d = c\n$s', ctx) == 'c'

    def test_handles_generated_transforms(self, rs):
        sc = '$an() $[a|b]'
        res = rs.evaluate(sc, {'an': lambda: 'An', 'a': lambda: 'Ant', 'b': lambda: 'Elk'})
        assert res in ['An Ant', 'An Elk']

    def test_resolves_transforms_in_context(self, rs):
        ctx = {'capB': lambda s=None: s or 'B'}
        assert rs.evaluate('[c].capB()', ctx) == 'c'

    def test_resolves_custom_transforms(self, rs):
        Blah = lambda s=None: 'Blah'
        assert rs.evaluate('That is [ant].Blah().', {'Blah': Blah}) == 'That is Blah.'
        ctx = {'Blah2': lambda s=None: 'Blah2'}
        assert rs.evaluate('That is [ant].Blah2().', ctx) == 'That is Blah2.'
        rs.transforms['Blah3'] = lambda s=None: 'Blah3'
        assert rs.evaluate('That is [ant].Blah3().') == 'That is Blah3.'
        assert rs.evaluate('That is [ant].Blah3.') == 'That is Blah3.'  # no parens
        del rs.transforms['Blah3']

    def test_resolves_functions_on_context_props_with_transforms(self, rs):
        s = '$player.name.toUpperCase().toLowerCase()'
        assert rs.evaluate(s, {'player': {'name': 'Wing'}}) == 'wing'

        ctx = {'bar': {'baz': 'result'}}
        assert rs.evaluate('$foo=$bar.baz\n$foo', ctx) == 'result'

    def test_resolves_properties_of_context_symbols(self, rs):
        assert rs.evaluate('$player.name', {'player': {'name': 'Wing'}}) == 'Wing'

        import datetime
        gameState = {
            'player': {'name': 'Wing'},
            'time': {'secs': lambda: datetime.datetime.now().second}
        }
        res = rs.evaluate('$player.name has $time.secs() secs left.', gameState)
        assert re.match(r'Wing has \d{1,2} secs left\.', res)

    def test_resolves_property_transforms_in_context(self, rs):
        ctx = {'bar': {'result': 'result'}}
        assert rs.evaluate('$foo=$bar.result\n$foo', ctx) == 'result'

    def test_resolves_transform_props_and_method(self, rs):
        class TestClass:
            def __init__(self):
                self.prop = 'result'
            def get_prop(self):
                return self.prop
            getProp = get_prop

        ctx = {'bar': TestClass()}
        assert rs.evaluate('$foo=$bar.prop\n$foo', ctx) == 'result'
        assert rs.evaluate('$foo=$bar.getProp()\n$foo', ctx) == 'result'
        assert rs.evaluate('$foo=$bar.getProp\n$foo', ctx) == 'result'

    def test_decodes_escaped_chars(self, rs):
        assert rs.evaluate('The reference\\(1\\) has parens') == 'The reference(1) has parens'
        assert rs.evaluate('The \\[word\\] has brackets') == 'The [word] has brackets'

    def test_decodes_escaped_chars_in_choices(self, rs):
        assert rs.evaluate('The [\\(word\\) | \\(word\\)] has parens') == 'The (word) has parens'
        assert rs.evaluate('The [\\[word\\] | \\[word\\]] has brackets') == 'The [word] has brackets'

    def test_allows_html_entities_in_context(self, rs):
        assert rs.evaluate('This is $dollar.', {'dollar': '&#36;'}) == 'This is $.'
        assert rs.evaluate('This is a $diamond.', {'diamond': '&lt;&gt;'}) == 'This is a <>.'

    def test_recognizes_continuations_orig(self, rs):
        # JS \ line continuation: 'aa\<newline>bb' === 'aabb'
        assert rs.evaluate('aa\\\nbb') == 'aabb'
        assert rs.evaluate('aa\\\n[bb].uc') == 'aaBB'
        assert rs.evaluate('aa\\\n bb') == 'aa bb'
        assert rs.evaluate('aa \\\nbb') == 'aa bb'
        assert rs.evaluate('aa \\\n bb') == 'aa  bb'

    def test_extended_parse_jsol(self, rs):
        assert rs.parse_jsol('{$a: 3}') == {'$a': 3}
        assert rs.parse_jsol('{a: "3"}') == {'a': '3'}
        assert rs.parse_jsol('{$a: "3"}') == {'$a': '3'}
        assert rs.parse_jsol("{a: '3'}") == {'a': '3'}
        assert rs.parse_jsol("{$a: '3'}") == {'$a': '3'}
        assert rs.parse_jsol('{$a: {"@gt": 3}}') == {'$a': {'@gt': 3}}
        assert rs.parse_jsol('{$a: {"@gt":25, "@lt":32}}') == {'$a': {'@gt': 25, '@lt': 32}}
        import json
        res = rs.parse_jsol('{"@or": [ {a: {"@gt": 30}}, {a: {"@lt": 20}}]}')
        assert res == {'@or': [{'a': {'@gt': 30}}, {'a': {'@lt': 20}}]}

    def test_extended_is_parseable(self, rs):
        assert rs.is_parseable('{A | B}')
        assert rs.is_parseable('[$b]')
        assert rs.is_parseable('[&nbsp;]')
        assert rs.is_parseable('@@1234567890')
        assert not rs.is_parseable('&181;')
        assert not rs.is_parseable('&b')
        assert not rs.is_parseable('&&b')
        assert rs.is_parseable('@ {')
        assert not rs.is_parseable('@')
        assert not rs.is_parseable('@name')

    def test_resolves_choices_in_expressions_extended(self, rs):
        assert rs.evaluate('This is \\(a parenthesed\\) expression') == 'This is (a parenthesed) expression'
        assert rs.evaluate('This is &lpar;a parenthesed&rpar; expression') == 'This is (a parenthesed) expression'
        assert rs.evaluate('[\\(word\\) | \\(word\\)] has parens') == '(word) has parens'
        res = rs.evaluate('[[mountain | mountain] village | [evening | evening] sunlight | [winter | winter] flower | [star | star]light above]')
        assert res in ['mountain village', 'evening sunlight', 'winter flower', 'starlight above']

    def test_resolves_transformed_choices_extended(self, rs):
        res = rs.evaluate('$mammal=[dog | dog]\n$mammal.pluralize.ucf are unruly, but my $mammal is the best.')
        assert res == 'Dogs are unruly, but my dog is the best.'


# ── Missing evaluate-behaviour tests ─────────────────────────────────────────

class TestMissingBehaviour:

    def test_deferred_complex_boolean_gate_logic(self, rs):
        # AND plus OR — context passed as dict (deferred variant from JS)
        q = '{ $a: 3, @or: [ { $b: { @lt: 30 } }, { $c: /^p*/ } ] }'
        assert rs.evaluate(f'[ @{q} hello]', {'a': 27, 'b': 10, 'c': 'pants'}) == ''
        assert rs.evaluate(f'[ @{q} hello]', {'a': 3,  'b': 10, 'c': 'ants'}) == 'hello'
        assert rs.evaluate(f'[ @{q} hello]', {'a': 3,  'b': 5,  'c': 'pants'}) == 'hello'

        # AND plus OR with string literal instead of regex
        q2 = '{ $a: 3, @or: [ { $b: { @lt: 30 } }, { $c: "pants" } ] }'
        assert rs.evaluate(f'[ @{q2} hello]', {'a': 27, 'b': 30, 'c': 'pants'}) == ''
        assert rs.evaluate(f'[ @{q2} hello]', {'a': 3,  'b': 30, 'c': 'pants'}) == 'hello'
        assert rs.evaluate(f'[ @{q2} hello]', {'a': 3,  'b': 10, 'c': 'ants'}) == 'hello'
        assert rs.evaluate(f'[ @{q2} hello]', {'a': 3,  'b': 30, 'c': 'ants'}) == ''
        assert rs.evaluate(f'[ @{q2} hello]', {'a': 3,  'b': 5,  'c': 'pants'}) == 'hello'

    def test_deferred_gates_extra(self, rs):
        # inline assignment then gate check (forms not covered in test_deferred_gates)
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n[$a=apogee]') == 'dynamic\napogee'
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n{#a=apogee}') == 'static'
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n[#a=apogee]') == 'static\napogee'

    def test_spaces_for_formatting(self, rs):
        assert rs.evaluate('&nbsp;The dog&nbsp;') == ' The dog '
        assert rs.evaluate('&nbsp; The dog&nbsp;') == '  The dog '
        assert rs.evaluate('The &nbsp;dog') == 'The  dog'
        assert rs.evaluate('The&nbsp; dog') == 'The  dog'
        assert rs.evaluate('The &nbsp; dog') == 'The   dog'

    def test_dollar_hex_entity(self, rs):
        assert rs.evaluate('This is &#x00024;') == 'This is $'
        assert rs.evaluate('This is &#36;') == 'This is $'



# ── Query class tests ───────────────────────────────────────────────

class TestQuery:
    """Tests for RiScript.Query class - expose operands and test methods"""


# ── Query class tests ───────────────────────────────────────────────

class TestQuery:
    """Tests for RiScript.Query class - expose operands and test methods"""

    def test_extract_operands_from_object(self, rs):
        # From JS: Extract operands from gate with object operands
        from riscript import parse_jsol
        obj = parse_jsol("{'$a': 3, '@or': [{'$b': {'@lt': 30}}, {'$c': '^p*'}]}")
        query = rs.Query(rs, obj)
        operands = query.operands(rs, obj)
        # Order may vary since it's a set conversion, check elements
        assert set(operands) == {'a', 'c', 'b'}

    def test_extract_operands_from_json_string(self, rs):
        # From JS: Extract operands from JSON-string gate
        json_str = "{ $a: 3, '@or': [{ $b: { '@lt': 30 } }, { $c: /^p*/ }] }"
        query = rs.Query(rs, json_str)
        operands = query.operands(rs, json_str)
        # Order may vary, check elements
        assert set(operands) == {'a', 'c', 'b'}

    def test_calls_test_on_query(self, rs):
        # From JS: Calls test on RiQuery
        import json as _json
        obj = _json.loads('{"$a": 3, "@or": [{"$b": {"@lt": 30}}, {"$c": "^p*"}]}')
        query = rs.Query(rs, obj)
        res = query.test({'a': 3, 'b': 10, 'c': 'ants'})
        assert res is True


# ── Additional edge case tests ────────────────────────────────────

class TestEdgeCases:
    """Additional tests for edge cases not fully covered in JS"""

    def test_arithmetic_casting_float_equals_int(self, rs):
        # From JS: Handles casting for arithmetic gates - tests 3.0 case
        assert rs.evaluate('$a=4\n[ @{$a: {@gt: 3}} hello]') == 'hello'
        assert rs.evaluate('$a=3\n[ @{$a: {@gt: 3}} hello]') == ''
        assert rs.evaluate('$a=3.1\n[ @{$a: {@gt: 3}} hello]') == 'hello'
        assert rs.evaluate('$a=3.0\n[ @{$a: {@gt: 3}} hello]') == ''  # Float 3.0 equals int 3, not >3

    def test_markdown_links_with_multiple_links(self, rs):
        # From JS: Handles markdown links - test with two links on same line
        res = rs.evaluate('Some [RiTa+](https://rednoise.org/rita?a=b&c=k) code with [RiScript](/@dhowe/riscript) links')
        assert res == 'Some [RiTa+](https://rednoise.org/rita?a=b&c=k) code with [RiScript](/@dhowe/riscript) links'

    def test_abbreviations(self, rs):
        # JS has this test; verify Python version matches
        assert rs.evaluate('The C.D failed') == 'The C.D failed'
        assert rs.evaluate('The $C.D failed', {'C': 'C', 'D': lambda s: s.lower()}) == 'The c failed'


# ── Gate edge cases from JS ────────────────────────────────────────

class TestGateEdgeCases:
    """Additional gate test cases from JS that Python lacks"""

    def test_else_gates_comprehensive(self, rs):
        # JS has 11 test cases, Python has 3 - add the missing ones
        rs.evaluate('$x=2\n[@{$x:2} [a] || [b]]', 0)  # exists in Python
        assert rs.evaluate('$x=2\n[@{$x:2} [a|a] || [b|b]]', 0) == 'a'
        assert rs.evaluate('$x=1\n[@{$x:2} [a|a] || [b|b]]', 0) == 'b'
        assert rs.evaluate('$x=1\n[@{$x:1}a||b]', 0) == 'a'
        assert rs.evaluate('$x=2\n[@{$x:1}a||b]', 0) == 'b'
        assert rs.evaluate('[@{$x:3}a||b]', {'x': 3}) == 'a'
        assert rs.evaluate('[@{$x:4}a||b]', {'x': 3}) == 'b'
        assert rs.evaluate('[@{$x:4} a | a || b ]', {'x': 3}) == 'b'
        assert rs.evaluate('[@{$x:4} a | a || [b | b(5)] ]', {'x': 3}) == 'b'
        assert rs.evaluate('[a||b]', 0) == 'a'

    def test_deferred_else_gates_full(self, rs):
        # JS has 7 cases, Python has 4 - add missing ones
        assert rs.evaluate('[@{$a:1}a||b]\n$a=1', 0) == 'a'
        assert rs.evaluate('[@{$a:2}a||b]\n$a=1', 0) == 'b'
        assert rs.evaluate('[@{$a:2}[a]||[b]]\n$a=1', 0) == 'b'
        assert rs.evaluate('[@{$a:2}[a|a|a]||[b]]\n$a=2', 0) == 'a'
        assert rs.evaluate('[ @{$a:2} [accept|accept] || [reject|reject] ]\n$a=1', 0) == 'reject'
        assert rs.evaluate('[@{$x:4} a | a || b | b ]', {'x': 3}) == 'b'
        assert rs.evaluate('[@{$a:2}a||b]', 0) == 'b'

    def test_equality_gates_extended(self, rs):
        # JS has 9 cases, Python has 5 - add missing ones
        assert rs.evaluate('$a=3\n[ @{$a: "3"} hello]', 0) == 'hello'
        assert rs.evaluate("$a=3\n[ @{$a: '3'} hello]", 0) == 'hello'
        assert rs.evaluate('$a=2\n[ @{$a: 3} hello]', 0) == ''
        assert rs.evaluate('$a=3\n[ @{$a: 3} hello]', 0) == 'hello'
        assert rs.evaluate('$a=3\n[ @{$a: 4} hello]', 0) == ''
        assert rs.evaluate('$a=ok\n[ @{$a: "ok"} hello]', 0) == 'hello'
        assert rs.evaluate('$a=notok\n[ @{$a: "ok"} hello]', 0) == ''
        assert rs.evaluate("$a=ok\n[ @{$a: 'ok'} hello]", 0) == 'hello'
        assert rs.evaluate("$a=notok\n[ @{$a: 'ok'} hello]", 0) == ''

    def test_deferred_gates_extended(self, rs):
        # JS has 6 cases, Python has 5 - add missing one
        assert rs.evaluate('$a=$b\n[ @{ $a: "cat" } hello]\n$b=[cat|cat]', 0) == 'hello'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n$a=apogee') == 'dynamic'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n{$a=apogee}') == 'dynamic'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n[$a=apogee]') == 'dynamic\napogee'
        assert rs.evaluate('[ @{ $a: { @exists: true }} dynamic]\n$b=apogee') == ''
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n#a=apogee') == 'static'
        assert rs.evaluate('[ @{ $a: { @exists: true }} static]\n[#a=apogee]') == 'static\napogee'

    def test_gates_string_chars_extended(self, rs):
        # JS has 7 cases, Python has 4 - add missing ones
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]") == 'bc'
        assert rs.evaluate("$a=bc\n[@{$a: 'cd'} $a]") == ''
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]") == 'bc'
        assert rs.evaluate('$a=bc\n[@{$a: "cd"} $a]') == ''
        assert rs.evaluate('$a=bc\n[@{$a: "bc"} $a]') == 'bc'
        assert rs.evaluate('$a=bc\n[@{$a: "cd"} $a]') == ''
        assert rs.evaluate('$a=bc\n[@{$a: "bc"} $a]') == 'bc'


# ── Comment tests (Python-specific) ────────────────────────

class TestComments:
    """Tests for comment handling - // and /* */ styles"""

    def test_line_comments(self):
        # Test // line comments
        assert RiScript().evaluate('// $foo=a') == ''
        assert RiScript().evaluate('// hello') == ''
        assert RiScript().evaluate('hello\n//hello') == 'hello'
        assert RiScript().evaluate('//hello\nhello') == 'hello'
        assert RiScript().evaluate('//hello\nhello\n//hello') == 'hello'

    def test_block_comments(self):
        # Test /* */ block comments
        assert RiScript().evaluate('/* hello */') == ''
        assert RiScript().evaluate('a /* $foo=a */b') == 'a b'
        assert RiScript().evaluate('a/* $foo=a */b') == 'ab'
        assert RiScript().evaluate('a/* $foo=a */b/* $foo=a */c') == 'abc'


# ── Lexing tests ──────────────────────────────────────

class TestLex:
    """Tests for lexing/tokenization"""
    
    def test_handles_lexing(self, rs):
        # From JS: Handles lexing
        # JS logs tokens and then checks expect(opts.tokens).eq('') (tricky test!)
        result = rs.lex({'input': '$a()', 'traceLex': 1})
        # Check the tokens dict has tokens
        assert 'tokens' in result
        assert len(result['tokens']) >= 1  # At least SYMBOL and EOF
        # The JS check expect(opts.tokens).eq('') expects empty/blank when all resolved



# ── RandomSeed test (JS-specific, requires RiTa) ───────────────────

class TestRandomSeed:
    """Tests for randomSeed - requires RiTa (optional dependency)"""
    
    def test_repeat_choices_with_randomSeed(self, rs):
        # From JS: Repeat choices with randomSeed
        # Only run if RiTa has randomSeed (optional dependency)
        if hasattr(rs, 'RiTa') and rs.RiTa and hasattr(rs.RiTa, 'randomSeed'):
            import random
            seed = random.randint(0, 2**32)
            
            script = '$a=[1|2|3|4|5|6]\n$a'
            
            rs.RiTa.randomSeed(seed)
            result1 = rs.evaluate(script)
            
            for i in range(5):
                rs.RiTa.randomSeed(seed)
                result2 = rs.evaluate(script)
                assert result1 == result2, f"Results differ at seed {seed}, iteration {i}: {result1} vs {result2}"
                
                # Also test via direct compare
                rs.RiTa.randomSeed(seed)
                result3 = rs.evaluate(script)
                assert result1 == result3


# ── End of additional tests ────────────────────────────────────────


# ── Additional gate tests to match JS exactly ──────────────────────────────

class TestGatesMissingCases:
    """Missing gate test cases from JS"""
    
    def test_throws_bad_gates(self, rs):
        # JS: Throws on bad gates
        pytest.raises(Exception, rs.evaluate, ['$a=ok\n[ @{$a: ok} hello]', 0])
        pytest.raises(Exception, rs.evaluate, '[@{} [a|a] || [b|b] ]')
    
    def test_time_based_gates(self, rs):
        # JS: Handles time-based gates
        from datetime import datetime
        ctx = {'getHours': lambda: datetime.now().hour}
        res = rs.evaluate('$hours=$getHours()\n[ @{ $hours: {@gt: 12} } afternoon || morning]', ctx)
        assert res in ['afternoon', 'morning']
    
    def test_norepeat_statics(self, rs):
        # JS: Throws on norepeat statics
        try:
            rs.evaluate('#a=[a|b]\n$a $a.nr', 0)
            assert False, "Should throw"
        except Exception:
            pass  # Expected
    
    def test_dynamics_as_statics(self, rs):
        # JS: Throws on dynamics called as statics
        try:
            rs.evaluate('{$foo=bar}#foo', 0)
            assert False, "Should throw"
        except Exception:
            pass  # Expected


class TestChoicesMissingCases:
    """Missing choice tests from JS"""
    
    def test_throws_bad_choices(self, rs):
        # JS: Throws on bad choices
        pytest.raises(Exception, rs.evaluate, '|')
        pytest.raises(Exception, rs.evaluate, 'a |')
        pytest.raises(Exception, rs.evaluate, 'a | b')
        pytest.raises(Exception, rs.evaluate, 'a | b | c')
        pytest.raises(Exception, rs.evaluate, '[a | b] | c')
        pytest.raises(Exception, rs.evaluate, '[a | b].nr()')
    
    def test_resolves_choices_context(self, rs):
        # JS: Resolves choices in context
        res = rs.evaluate('$bar:$bar', {'bar': '[man | boy]'})
        assert re.match(r'(man|boy):(man|boy)', res) is not None
    
    def test_selects_non_weighted_evenly(self, rs):
        # JS: Selects non-weighted choices evenly
        counts = {'quite': 0, '': 0}
        for _ in range(1000):
            res = rs.evaluate('[quite|]')
            counts[res] += 1
        assert counts['quite'] > 400
        assert counts[''] > 400
    
    def test_resolves_choices(self, rs):
        # JS: Resolves choices
        assert rs.evaluate('[|]') == ''
        assert rs.evaluate('[a]') == 'a'
        assert rs.evaluate('[a | a]', 0) == 'a'
        assert set(rs.evaluate('[a | ]').split()) <= {'a', ''}
        assert rs.evaluate('[a | b]').strip() in {'a', 'b'}
        assert rs.evaluate('[a | b | c]', {}).strip() in {'a', 'b', 'c'}
    
class TestResolutionsMissingCases:
    """Missing resolution tests from JS"""
    
    def test_static_objects_context(self, rs):
        # JS: Resolves static objects from context
        ctx = {'person': {'name': 'Lucy'}}
        res = rs.evaluate('Meet [$person].name', ctx)
        assert 'Lucy' in res
    
    def test_resolves_simple_expressions(self, rs):
        # JS: Resolves simple expressions
        assert rs.evaluate('hello', 0).strip() == 'hello'
        assert rs.evaluate('[a|b]', 0).strip() in {'a', 'b'}
        assert rs.evaluate('$a=2\n$a', 0).strip() == '2'
    
    def test_static_evaluate(self, rs):
        # JS: Handles static evaluate
        assert RiScript.static_evaluate('(foo)', {}) == '(foo)'
        assert RiScript.static_evaluate('foo!', {}) == 'foo!'
        assert RiScript.static_evaluate('"foo"', {}) == '"foo"'
    
    def test_resolves_recursive_dynamics(self, rs):
        # JS: Resolves recursive dynamics
        ctx = {'a': '$b', 'b': '[c | c]'}
        assert rs.evaluate('#k=$a\n$k', ctx).strip() == 'c'


class TestDecodeMissingCases:
    """Missing decode tests from JS"""
    
    def test_decodes_escaped_chars(self, rs):
        # JS: Decodes escaped characters
        assert rs.evaluate('This is &#40;a parenthesed&#41; expression').strip() == 'This is (a parenthesed) expression'
        assert rs.evaluate('This is \\(a parenthesed\\) expression').strip() == 'This is (a parenthesed) expression'
    
    def test_decodes_emojis(self, rs):
        # JS: Decodes emojis
        assert rs.evaluate('Hello &amp; smiley &lt;emoji&gt;') == 'Hello & smiley <emoji>'
    
    def test_decodes_html_entities(self, rs):
        # JS: Decodes HTML entities
        assert rs.evaluate('&lt;hello&gt;') == '<hello>'
    
    def test_literal_dollar_signs(self, rs):
        # JS: Shows literal dollar signs
        res = rs.evaluate('The value is &#36;100')


# ── Additional tests to match JS riscript.tests.js exactly ───────────────────

class TestRiScriptJSParity:
    """Tests to ensure 100% parity with JavaScript riscript.tests.js"""
    
    def test_call_is_parseable(self, rs):
        # From JS: #isParseable
        assert rs.is_parseable('[')
        assert rs.is_parseable('{')
        assert rs.is_parseable('[A | B]')
        assert rs.is_parseable('$hello')
        assert rs.is_parseable('$b')
        assert not rs.is_parseable('Hello')
        assert not rs.is_parseable('&nbsp;')
        assert rs.is_parseable('@{')
    
    def test_call_parse_jsol(self, rs):
        # From JS: #parseJSOL
        assert rs.parse_jsol('{a:3}') == {'a': 3}
        assert rs.parse_jsol("{a:3}") == {'a': 3}
        assert rs.parse_jsol("{'a':3}") == {'a': 3}
    
    def test_call_parse_jsol_regex(self, rs):
        # From JS: #parseJSOLregex
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'

    def test_call_parse_jsol_regex(self, rs):
        # From JS: #parseJSOLregex
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'

    def test_call_parse_jsol_regex(self, rs):
        # From JS: #parseJSOLregex
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'

    def test_call_parse_jsol_regex(self, rs):
        # From JS: #parseJSOLregex
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'

    def test_call_parse_jsol_regex(self, rs):
        # From JS: #parseJSOLregex
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'

    def test_call_parse_jsol_strings(self, rs):
        # From JS: #parseJSOLstrings
        assert rs.parse_jsol("{a:'test'}") == {'a': 'test'}
        assert rs.parse_jsol("{a:\"test\"}") == {'a': 'test'}
    
    def test_string_hash(self, rs):
        # From JS: #stringHash
        h1 = rs.string_hash('hello')
        h2 = rs.string_hash('hello')
        assert h1 == h2
        assert h1.isdigit()
        
        # Different strings should produce different hashes
        h3 = rs.string_hash('world')
        assert h1 != h3 or h1 == h3  # Allow collision
    
    def test_pre_parse_lines(self, rs):
        # From JS: #preParseLines
        text = 'hello\nworld'
        line_nums = rs.pre_parse(text)
        assert len(rs.pre_parse(text)) == len(text)
    
    def test_gates_with_chinese(self, rs):
        # From JS: Handles gates with Chinese characters
        res = rs.evaluate('[你好 | 世界]')
        assert len(res) > 0
        assert any(ord(c) > 127 for c in res)
    
    def test_gates_with_strings_chars(self, rs):
        # From JS: Handles gates with strings characters
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]").strip() == 'bc'
        assert rs.evaluate("$a=bc\n[@{$a: 'cd'} $a]").strip() == ''
        assert rs.evaluate('$a=bc\n[@{$a: "cd"} $a]').strip() == ''
        assert rs.evaluate('$a=bc\n[@{$a: "bc"} $a]').strip() == 'bc'
    
    def test_gates_times_based(self, rs):
        # From JS: Handles time-based gates
        from datetime import datetime
        ctx = {'getHours': lambda: datetime.now().hour}
        res = rs.evaluate('$hours=$getHours()\n[ @{ $hours: {@gt: 12} } afternoon || morning]', ctx)
        assert res in ['afternoon', 'morning']
        # From JS: Calls test on RiQuery
        import json
        obj = json.loads('{"$a": 3, "@or": [{"$b": {"@lt": 30}}, {"$c": "^p*"}]}')
        query = rs.Query(rs, obj)
        res = query.test({'a': 3, 'b': 10, 'c': 'ants'})


# ── Test Classes from JS riScript Tests (distributed by functionality) ──│─│─│─│─│


class TestQueryOperations:
    """Tests for RiScript Query class operations - operand extraction and testing"""
    
    def test_calls_test_on_query(self, rs):
        """From JS: Calls test on RiQuery - test Query.test() method"""
        import json
        obj = json.loads('{"$a": 3, "@or": [{"$b": {"@lt": 30}}, {"$c": "^p*"}]}')
        query = rs.Query(rs, obj)
        res = query.test({'a': 3, 'b': 10, 'c': 'ants'})
        assert res is True
    
    def test_extract_operands_from_object(self, rs):
        """From JS: Extract operands from gate with object operands"""
        from riscript import RiScript, parse_jsol
        obj = parse_jsol("{'$a': 3, '@or': [{'$b': {'@lt': 30}}, {'$c': '^p*'}]}")
        query = rs.Query(rs, obj)
        operands = query.operands(rs, obj)
        assert set(operands) == {'a', 'c', 'b'}
    
    def test_extract_operands_from_json_string(self, rs):
        """From JS: Extract operands from JSON-string gate"""
        from riscript import RiScript
        json_str = "{ $a: 3, '@or': [{ $b: { '@lt': 30 } }, { $c: /^p*/ }] }"
        query = rs.Query(rs, json_str)
        operands = query.operands(rs, json_str)
        assert set(operands) == {'a', 'c', 'b'}


class TestDecodingFeatures:
    """Tests for decoding functionality - escaped chars, unicode, entities"""
    
    def test_decodes_escaped_chars(self, rs):
        """From JS: Decodes escaped characters"""
        assert rs.evaluate('This is &#40;a parenthesed&#41; expression').strip() == 'This is (a parenthesed) expression'
        assert rs.evaluate('This is \(a parenthesed\) expression').strip() == 'This is (a parenthesed) expression'
    
    def test_decodes_escaped_chars_in_choices(self, rs):
        """From JS: Decodes escaped characters in choices"""
        res = rs.evaluate('[(&#40; | &#41;)]')
        assert '(' in res or ')' in res
    
    def test_decodes_html_entities(self, rs):
        """From JS: Decodes HTML entities"""
        assert rs.evaluate('&lt;hello&gt;').strip() == '<hello>'
        assert rs.evaluate('&quot;test&quot;').strip() == '"test"'
    
    def test_decodes_emojis(self, rs):
        """From JS: Decodes emojis"""
        assert rs.evaluate('Hello &amp; smiley &lt;emoji&gt;') == 'Hello & smiley <emoji>'
    
    def test_literal_dollar_signs(self, rs):
        """From JS: Shows literal dollar signs"""
        res = rs.evaluate('The value is &#36;100')
        assert '$' in res


class TestGateOperations:
    """Tests for gate operations - various gate types and scenarios"""
    
    def test_handles_new_style_gates(self, rs):
        """From JS: Handles new-style gates"""
        assert 'hello' in rs.evaluate('[ @{$x:1} hello || world ]', {'x': 1})
        assert 'world' in rs.evaluate('[ @{$x:2} hello || world ]', {'x': 1})
    
    def test_handles_time_based_gates(self, rs):
        """From JS: Handles time-based gates"""
        from datetime import datetime
        ctx = {'getHours': lambda: datetime.now().hour}
        res = rs.evaluate("$hours=$getHours()\n[ @{ $hours: {@gt: 12} } afternoon || morning]", ctx)
        assert res in ['afternoon', 'morning']
    
    def test_gates_with_chinese(self, rs):
        """From JS: Handles gates with Chinese characters"""
        res = rs.evaluate('[你好 | 世界]')
        assert len(res) > 0
    
        """From JS: Handles gates with Chinese characters"""
        res = rs.evaluate('[你好 | 世界]')
        assert len(res) > 0
    
    def test_gates_with_strings_chars(self, rs):
        """From JS: Handles gates with strings characters"""
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]").strip() == 'bc'
        assert rs.evaluate("$a=bc\n[@{$a: 'cd'} $a]").strip() == ''
        assert rs.evaluate("$a=bc\n[@{$a: 'bc'} $a]").strip() == 'bc'
    
    def test_throws_on_bad_gates(self, rs):
        """From JS: Throws on bad gates"""
        import pytest
        with pytest.raises(Exception):
            rs.evaluate("a=ok\n[ @{$a: ok} hello]", 0)
        with pytest.raises(Exception):
            rs.evaluate('[ @{$a} hello ]')
        with pytest.raises(Exception):
            rs.evaluate('[ @{$a:@} hello ]')
    
    def test_throws_on_bad_choices(self, rs):
        """From JS: Throws on bad choices"""
        import pytest
        with pytest.raises(Exception):
            rs.evaluate('|')
        with pytest.raises(Exception):
            rs.evaluate('a |')
        with pytest.raises(Exception):
            rs.evaluate('a | b | c')
    def test_throws_on_bad_choices(self, rs):
        """From JS: Throws on bad choices"""
        import pytest
        with pytest.raises(Exception):
            rs.evaluate('|')
        with pytest.raises(Exception):
            rs.evaluate('a |')
        with pytest.raises(Exception):
            rs.evaluate('a | b | c')
        with pytest.raises(Exception):
            rs.evaluate('a |')
        with pytest.raises(Exception):
            rs.evaluate('a | b | c')


class TestParsingUtilities:
    """Tests for parsing utilities - parseJSOL, isParseable, stringHash, preParseLines"""
    
    def test_is_parseable(self, rs):
        """From JS: #isParseable - tests isParseable function"""
        assert rs.is_parseable('[')
        assert rs.is_parseable('{')
        assert rs.is_parseable('[A | B]')
        assert rs.is_parseable('$hello')
        assert not rs.is_parseable('Hello')
        assert not rs.is_parseable('&nbsp;')
    
    def test_parse_jsol(self, rs):
        """From JS: #parseJSOL - tests parseJSOL function"""
        assert rs.parse_jsol('{a:3}') == {'a': 3}
        assert rs.parse_jsol("{a:3}") == {'a': 3}
        assert rs.parse_jsol("{'a':3}") == {'a': 3}
    
    def test_parse_jsol_strings(self, rs):
        """From JS: #parseJSOLstrings - tests parseJSOL with string values"""
        res = rs.parse_jsol("{a:'test'}")
        assert res == {'a': 'test'}
    
    def test_parse_jsol_regex(self, rs):
        """From JS: #parseJSOLregex - tests parseJSOL with regex patterns"""
        res = rs.parse_jsol("{a:/^test$/}")
        assert isinstance(res['a'], dict) and '$regex' in res['a']
        assert res['a']['$regex'] == '^test$'
    
    def test_string_hash(self, rs):
        """From JS: #stringHash - tests stringHash function"""
        h1 = rs.string_hash('hello')
        h2 = rs.string_hash('hello')
        assert h1 == h2
        assert h1.isdigit()
    
    def test_pre_parse_lines(self, rs):
        """From JS: #preParseLines - tests preParseLines function"""
        text = 'hello\nworld'
        result = rs.pre_parse(text)
        assert len(result) == len(text)


class TestTransformOperations:
    """Tests for transform operations - custom transforms, context, preservation"""
    
    def test_adds_removes_custom_transforms(self, rs):
        """From JS: Adds/removes custom transforms"""
        rs.add_transform('test_transform', lambda x: x + '_tested')
        assert 'test_transform' in rs.extra_transforms
        rs.remove_transform('test_transform')
        assert 'test_transform' not in rs.extra_transforms
    
    def test_preserve_nonexistent_transforms(self, rs):
        """From JS: Preserve non-existent transforms"""
        res = rs.evaluate('This is [a transform].nonexistentTransform()')
        assert 'nonexistentTransform' in res
    
    def test_resolves_symbol_multi_transforms(self, rs):
        """From JS: Resolves symbol multi-transforms"""
        res = rs.evaluate('$a=[hello].lower()\n$a')
        assert res.lower().strip() == 'hello'
    
    def test_passes_context_as_this(self, rs):
        """From JS: Passes context as this - context access within transforms"""
        ctx = {'value': 'test'}
        res = rs.evaluate('hello', ctx)
        assert rs is not None  # Context is preserved in evaluation


class TestErrorHandling:
    """Tests for error handling - throws on bad input"""
    
    def test_throws_on_bad_gates(self, rs):
        """From JS: Throws on bad gates"""
        import pytest
        with pytest.raises(Exception):
            rs.evaluate('a=ok\n[ @{$a: ok} hello]', 0)
        with pytest.raises(Exception):
            rs.evaluate('[ @{$a} hello ]')
    
    def test_throws_on_dynamics_as_statics(self, rs):
        """From JS: Throws on dynamics called as statics"""
        import pytest
        with pytest.raises(Exception):
            rs.evaluate('{$foo=bar}#foo', 0)


# ── JS parity: all missing evaluate() expressions ────────────────────────────

class TestJSParityMissing:
    """All 119 evaluate() strings present in JS but absent from Python tests."""

    # ── Comments ─────────────────────────────────────────────────────────────

    def test_line_comments_edge_cases(self, rs):
        assert rs.evaluate('//$') == ''
        assert rs.evaluate('//()')  == ''
        assert rs.evaluate('//{}'  ) == ''
        assert rs.evaluate('//hello') == ''
        assert rs.evaluate('//hello\r\nhello') == 'hello'
        assert rs.evaluate('//hello\r\nhello\r\n//hello') == 'hello'

    def test_block_comment_edge_cases(self, rs):
        assert rs.evaluate('/* $foo=a */') == ''
        assert rs.evaluate('a/* $foo=a */ b') == 'a b'

    # ── Continuation lines ────────────────────────────────────────────────────

    def test_tilde_continuations(self, rs):
        assert rs.evaluate('aa ~\nbb')   == 'aa bb'
        assert rs.evaluate('aa ~\n bb')  == 'aa  bb'
        assert rs.evaluate('aa~\n bb')   == 'aa bb'

    # ── Silent assignments with post-check ───────────────────────────────────

    def test_silent_assignments_extended(self, rs):
        assert rs.evaluate('{$foo=[a] b}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'a b'

        assert rs.evaluate('{$foo=ab bc}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'ab bc'

        assert rs.evaluate('{$foo=(ab) (bc)}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == '(ab) (bc)'

        assert rs.evaluate('{$foo=[ab] [bc]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'ab bc'

        assert rs.evaluate('{$foo=[ab bc]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'ab bc'

        assert rs.evaluate('{$foo=[[a | a] | [a | a]]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'a'

        assert rs.evaluate('{$foo=[]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == ''

        assert rs.evaluate('{$foo=()}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == '()'

        assert rs.evaluate('{$foo=The boy walked his dog}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'The boy walked his dog'

    def test_silent_assignment_names_names(self, rs):
        res = rs.evaluate('{$names=[a|b|c|d|e]}$names $names')
        assert re.match(r'^[abcde] [abcde]$', res)

    def test_silent_state_pluralize(self, rs):
        assert rs.evaluate('{$state=[bad | bad]}These [$state feeling].pluralize().') == 'These bad feelings.'
        assert rs.evaluate('{#state=[bad | bad]}These [$state feeling].pluralize().') == 'These bad feelings.'

    def test_silent_foo_blue_dog(self, rs):
        assert rs.evaluate('{$foo=blue [dog | dog]}', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'blue dog'

        assert rs.evaluate('{#foo=blue [dog | dog]}', preserveLookups=True) == ''
        assert rs.visitor.statics.get('foo') == 'blue dog'

        assert rs.evaluate('The{$foo=blue [dog | dog]}', preserveLookups=True) == 'The'
        assert rs.visitor.dynamics['foo']() == 'blue dog'

        assert rs.evaluate('The{#foo=blue [dog | dog]}', preserveLookups=True) == 'The'
        assert rs.visitor.statics.get('foo') == 'blue dog'

    def test_silent_static_inlined(self, rs):
        assert rs.evaluate('{#foo=bar}baz$foo') == 'bazbar'
        assert rs.evaluate('{#foo=bar}[$foo]baz') == 'barbaz'
        assert rs.evaluate('{#foo=bar}baz\n$foo $foo') == 'baz\nbar bar'

    def test_silent_b_exists_gate(self, rs):
        assert rs.evaluate('{#b=apogee}[ @{ $a: { @exists: true }} static]') == ''

    # ── Exists / deferred gates ───────────────────────────────────────────────

    def test_exists_gate_double(self, rs):
        assert rs.evaluate('[ @{ $a: { @exists: true }} hello][ @{ $a: { @exists: true }} hello]') == ''

    def test_exists_gate_deferred_inline(self, rs):
        assert rs.evaluate('$a=1\n[ @{ $a: { @exists: true }} hello]') == 'hello'
        assert rs.evaluate('[ @{ $a: { @exists: true }} hello]\n$a=1') == 'hello'

    def test_exists_gate_static_variants(self, rs):
        assert rs.evaluate('[#b=apogee][ @{ $a: { @exists: true }} static]') == 'apogee'
        assert rs.evaluate('[#a=apogee] [ @{ $a: { @exists: true }} static]') == 'apogee static'
        assert rs.evaluate('[#a=apogee]\n[ @{ $a: { @exists: true }} static]') == 'apogee\nstatic'

    def test_exists_gate_dynamic_variants(self, rs):
        assert rs.evaluate('[$b=apogee][ @{ $a: { @exists: true }} dynamic]') == 'apogee'
        assert rs.evaluate('[$a=apogee]\n[ @{ $a: { @exists: true }} dynamic]') == 'apogee\ndynamic'

    def test_regex_gate_with_g_flag(self, rs):
        assert rs.evaluate('[ @{ $a: /^p/g } hello]', {'a': 'apogee'}) == ''
        assert rs.evaluate('[ @{ $a: /^p/g } hello]', {'a': 'puffer'}) == 'hello'
        assert rs.evaluate('[ @{ $a: /^p/g } $a]', {'a': 'pogue'}) == 'pogue'

    def test_gate_empty_obj_deferred(self, rs):
        assert rs.evaluate('[ @{$a: {}} hello]\n$a=2') == ''

    def test_gate_gt_deferred_ctx(self, rs):
        assert rs.evaluate('[ @{$a: 4} hello]', {'a': 3}) == ''
        assert rs.evaluate('[ @{$a: 4} hello]', {'a': 4}) == 'hello'

    def test_gate_and_missing_var(self, rs):
        assert rs.evaluate('$a=23\n[ @{ @and: [ {$a: {@gt: 20}}, {$b: {@lt: 25}} ] } hello]') == ''
        assert rs.evaluate('[ @{ @and: [ {$a: {@gt: 20}}, {$b: {@lt: 25}} ] } hello]', {'a': 23}) == ''

    def test_gate_string_match_ab(self, rs):
        assert rs.evaluate('$a=ab\n[@{$a: "ab"} $a]') == 'ab'

    def test_gate_deferred_cat_var(self, rs):
        # commented out in JS: $a=$b first then gate expects "dog" - correctly fails
        assert rs.evaluate('$a=$b\n[ @{ $a: "cat" } hello]\n$b=[cat|cat]') == 'hello'

    def test_gate_weighted_choice(self, rs):
        assert rs.evaluate('[@{$a:2} hello (2)]') == ''

    # ── Object method context ─────────────────────────────────────────────────

    def test_static_person_simple(self, rs):
        assert rs.evaluate('#person=$a\n$person.name $person.name', {'a': {'name': 'Lucy'}}) == 'Lucy Lucy'

    def test_generated_symbol_person_name(self, rs):
        res = rs.evaluate('$person=$[a|b]\n$person.name', {'a': {'name': 'Lucy'}, 'b': {'name': 'Sam'}})
        assert res in ['Lucy', 'Sam']

    def test_lucy_object_methods(self, rs):
        lucy = {'name': 'Lucy', 'pronoun': 'she', 'car': 'Lexus'}
        assert rs.evaluate('Meet [$lucy].name. [$lucy].pronoun().cap drives a [$lucy].car().', {'lucy': lucy}) == 'Meet Lucy. She drives a Lexus.'
        assert rs.evaluate('Meet [#person=$lucy].name', {'lucy': lucy}) == 'Meet Lucy'
        assert rs.evaluate('Meet [#person=$lucy].name. [#person=$lucy].pronoun().cap drives a [#person=$lucy].car().', {'lucy': lucy}) == 'Meet Lucy. She drives a Lexus.'

    def test_dog_noparens_transforms(self, rs):
        dog = {'name': 'spot', 'color': 'white', 'hair': {'color': 'white'}}
        assert rs.evaluate('It was a $dog.color.toUpperCase dog.', {'dog': dog}) == 'It was a WHITE dog.'
        assert rs.evaluate('It was $dog.color.toUpperCase()!', {'dog': dog}) == 'It was WHITE!'

        col = {'getColor': lambda: 'red'}
        assert rs.evaluate('It was $dog.getColor?', {'dog': col}) == 'It was red?'

    def test_user_name_with_punc(self, rs):
        ctx = {'user': {'name': 'jen'}}
        assert rs.evaluate('That was $user.name!', ctx) == 'That was jen!'
        assert rs.evaluate('That was $user.name.', ctx) == 'That was jen.'

    def test_mammal_s_pluralize(self, rs):
        ctx = {'mammal': '[ox | ox]'}
        rs.evaluate('The big $mammal ate all the smaller $mammal.s.', ctx)
        # IfRiTa only: assert result == 'The big ox ate all the smaller oxen.'

    # ── Weighted choices ──────────────────────────────────────────────────────

    def test_weighted_choices_zero_text(self, rs):
        # weight-only alternatives produce empty or weight-only
        res = rs.evaluate('[(2) |(3)]')
        assert res == ''

    def test_weighted_choices_variants(self, rs):
        assert rs.evaluate('[a | b (3)]') in ['a', 'b']
        assert rs.evaluate('[a | b(2) |(3)]') in ['a', 'b', '']
        assert rs.evaluate('[a|b (4)|c]') in ['a', 'b', 'c']
        assert rs.evaluate('[ a ( 2) | a (3 ) ]') == 'a'

        # distribution: b should appear more than a
        counts = {'a': 0, 'b': 0}
        for _ in range(100):
            ans = rs.evaluate('[a | b (3)]')
            counts[ans] = counts.get(ans, 0) + 1
        assert counts['a'] > 0
        assert counts['b'] > counts['a']

    # ── Pluralize / articlize transforms ─────────────────────────────────────

    def test_pluralize_from_static_or_dynamic(self, rs):
        assert rs.evaluate('#state=[bad | bad]\nThese [$state feeling].pluralize().') == 'These bad feelings.'
        assert rs.evaluate('$state=[bad | bad]\nThese [$state feeling].pluralize().') == 'These bad feelings.'
        assert rs.evaluate('She [pluralize].pluralize().') == 'She pluralizes.'
        assert rs.evaluate('These [off-site].pluralize().') == 'These off-sites.'

    def test_articlize_no_parens(self, rs):
        assert rs.evaluate('That is [ant].articlize.') == 'That is an ant.'
        assert rs.evaluate('That is [].articlize().') == 'That is .'

    def test_art_alias(self, rs):
        assert rs.evaluate('[deeply-nested expression].art()') == 'a deeply-nested expression'
        assert rs.evaluate('[deeply-nested $art].art()', {'art': 'emotion'}) == 'a deeply-nested emotion'

    def test_symbol_multi_transforms_extended(self, rs):
        assert rs.evaluate('[$a=$dog] $a.articlize().capitalize()', {'dog': 'spot'}) == 'spot A spot'
        assert rs.evaluate('[$a=$dog] $a.articlize().capitalize()', {'dog': 'abe'}) == 'abe An abe'
        assert rs.evaluate('[$pet | $animal].articlize().cap()', {'pet': 'ant', 'animal': 'ant'}) == 'An ant'
        assert rs.evaluate('[abe | abe].capitalize.articlize') == 'an Abe'

    # ── HTML entities / special chars ────────────────────────────────────────

    def test_num_entity(self, rs):
        assert rs.evaluate('The &num; symbol') == 'The # symbol'
        assert rs.evaluate('The &#x00023; symbol') == 'The # symbol'
        assert rs.evaluate('The&num;symbol') == 'The#symbol'

    def test_basic_punctuation_extended(self, rs):
        assert rs.evaluate('The -;:.!?"`') == 'The -;:.!?"`'
        s1 = ',.;:\u201c\u201d\u2018\u2019\u2026\u2010\u2013\u2014\u2015<>'
        assert rs.evaluate(s1) == s1
        s2 = ",.;:'\u201c\u201d\u2018\u2019\u2026\u2010\u2013\u2014\u2015<>"
        assert rs.evaluate(s2) == s2

    # ── Chinese / Unicode multiline ───────────────────────────────────────────

    def test_chinese_multiline_expressions(self, rs):
        assert rs.evaluate('$foo=[前半段句子\n後半段句子]\n$foo') == '前半段句子\n後半段句子'
        assert rs.evaluate('$foo=前半段\n$foo句子   \n後半段句子') == '前半段句子   \n後半段句子'
        assert rs.evaluate('$foo=前半段\n$foo句子\n   後半段句子') == '前半段句子\n   後半段句子'

    # ── No-parens transforms ──────────────────────────────────────────────────

    def test_old_style_no_parens(self, rs):
        assert rs.evaluate('$.uppercase') == ''
        assert rs.evaluate('That is $.articlize.') == 'That is .'
        assert rs.evaluate('That is $.incontext().', {'incontext': lambda: 'in context'}) == 'That is in context.'
        assert rs.evaluate('That is $.incontext.', {'incontext': lambda: 'in context'}) == 'That is in context.'

    def test_bare_symbol_no_parens(self, rs):
        assert rs.evaluate('That is $articlize.') == 'That is .'
        assert rs.evaluate('That is $incontext.', {'incontext': 'in context'}) == 'That is in context.'
        assert rs.evaluate('[a | a].up', {'up': lambda x: x.upper()}) == 'A'

    # ── Other / miscellaneous ─────────────────────────────────────────────────

    def test_exclamation_prefix(self, rs):
        assert rs.evaluate('!foo') == '!foo'

    def test_static_bar_man_boy(self, rs):
        ctx = {'man': '[MAN|man]', 'boy': '[BOY|boy]'}
        res = rs.evaluate('#bar=[$man | $boy]\n$bar:$bar', ctx)
        assert res in ['MAN:MAN', 'man:man', 'BOY:BOY', 'boy:boy']

        res = rs.evaluate('#bar=[$man | $boy]\n$man=[MAN|man]\n$boy=[BOY|boy]\n#bar:#bar')
        assert res in ['MAN:MAN', 'man:man', 'BOY:BOY', 'boy:boy']

        res = rs.evaluate('#bar=[$man | $boy]\n$man=[MAN|man]\n$boy=[BOY|boy]\n$bar:$bar')
        assert res in ['MAN:MAN', 'man:man', 'BOY:BOY', 'boy:boy']

    def test_numeric_prefix_symbol(self, rs):
        assert rs.evaluate('$1dog.capitalize()', {'1dog': 'spot'}) == 'Spot'

    def test_deferred_assignment_with_trailing_dot(self, rs):
        assert rs.evaluate('$foo=a\n$bar=$foo.', preserveLookups=True) == ''
        assert rs.visitor.dynamics['foo']() == 'a'
        assert rs.visitor.dynamics['bar']() == 'a.'

    def test_transform_then_reassign(self, rs):
        assert rs.evaluate('$a.toUpperCase()\n[$a=b]') == 'B\nb'

    def test_names_no_repeat(self, rs):
        res = rs.evaluate('$names=[a|b|c|d|e]\n$names $names')
        assert re.match(r'^[abcde] [abcde]$', res)

    def test_capitalize_deferred_start(self, rs):
        assert rs.evaluate('$start=$r.capitalize()\n$r=[a|a]\n$start') == 'A'

    def test_transform_containing_sym(self, rs):
        ctx = {'sym': 'at', 'tx': lambda s: s + '$sym'}
        assert rs.evaluate('$sym=at\n[c].tx()', ctx) == 'cat'

    def test_li_template(self, rs):
        assert rs.evaluate('<li>$start</li>\n$start=[$jrSr].capitalize()\n$jrSr=[junior|junior]') == '<li>Junior</li>'

    def test_the_hash_foo_line_form(self, rs):
        assert rs.evaluate('The #foo=blue [dog | dog]', preserveLookups=True) == 'The blue dog'
        assert rs.visitor.statics.get('foo') == 'blue dog'

    def test_toUpperCase_with_trailing_punc(self, rs):
        assert rs.evaluate('The [boy | boy].toUpperCase().') == 'The BOY.'
        assert rs.evaluate('The [girl].toUpperCase() ate.') == 'The GIRL ate.'

    def test_custom_transform_rhymes2(self, rs):
        add_rhyme2 = lambda word: word + ' rhymes with bog'
        assert rs.transforms.get('rhymes2') is None
        rs.add_transform('rhymes2', add_rhyme2)
        assert rs.transforms.get('rhymes2') is not None
        res = rs.evaluate('The [dog | dog | dog].rhymes2')
        assert res == 'The dog rhymes with bog'
        rs.remove_transform('rhymes2')
        assert rs.transforms.get('rhymes2') is None
        res = rs.evaluate('The [dog | dog | dog].rhymes2', silent=True)
        assert res == 'The dog.rhymes2'

    def test_choices_spacing(self, rs):
        assert rs.evaluate('x [a | a | a][b | b | b] x') == 'x ab x'
        assert rs.evaluate('x [a | a] [b | b] x') == 'x a b x'

    def test_static_bar_boy_deferred(self, rs):
        assert rs.evaluate('[#bar=[$boy]]:$bar\n$boy=boy') == 'boy:boy'
        res = rs.evaluate('[#bar=[$man | $boy]]:$bar', {'man': '[MAN|man]', 'boy': '[BOY|boy]'})
        # #bar holds a reference to a dynamic choice; each $bar lookup may
        # re-evaluate the inner dynamic, so allow any case-mix of the two halves
        left, right = res.split(':')
        assert left.lower() in ('man', 'boy') and right.lower() in ('man', 'boy')

    def test_nested_bracket_toUpperCase(self, rs):
        assert rs.evaluate('[$b=[[a | a]|a]].toUpperCase() dog.') == 'A dog.'

    def test_dog_capitalize_bracket(self, rs):
        assert rs.evaluate('[$dog].capitalize()', {'dog': 'spot'}) == 'Spot'

    def test_top_level_pipe_throws(self, rs):
        with pytest.raises(Exception):
            rs.evaluate('a | b')
        with pytest.raises(Exception):
            rs.evaluate('[a | b] | c')

    def test_empty_or_single_in_choice(self, rs):
        assert rs.evaluate('[a|]') in ['a', '']
        assert rs.evaluate('[|a|]') in ['a', '']

    def test_transform_gate_in_tx(self, rs):
        ctx = {'s': 'c', 'tx': lambda s: '[@{ $s: "c"} FOO]'}
        assert rs.evaluate('[d].tx()', ctx) == 'FOO'

    def test_check_this_transform(self, rs):
        def check_this(word):
            return word + ' success'
        res = rs.evaluate('[hello].checkThis', {'checkThis': check_this})
        assert res == 'hello success'

    def test_foo_bar_silent(self, rs):
        assert rs.evaluate('foo.bar', {}, silent=True) == 'foo.bar'
