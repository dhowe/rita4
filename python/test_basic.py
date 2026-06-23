"""Basic smoke tests for the Python RiScript implementation."""
from riscript import RiScript

rs = RiScript()
passed = failed = 0

def check(desc, result, expected):
    global passed, failed
    if isinstance(expected, list):
        ok = result in expected
    else:
        ok = result == expected
    if ok:
        passed += 1
    else:
        failed += 1
        print(f'  FAIL  {desc!r}')
        print(f'        got:      {result!r}')
        print(f'        expected: {expected!r}')

def ev(script, ctx=None, **opts):
    return rs.evaluate(script, ctx or {}, **opts)

print('── Basics ─────────────────────────────────────────────────────────────')
check('empty',            ev(''),            '')
check('literal',          ev('hello'),       'hello')
check('space',            ev('hello world'), 'hello world')

print('── Choices ────────────────────────────────────────────────────────────')
check('single',           ev('[a]'),         'a')
check('two opts',         ev('[a|a]'),       'a')
check('empty opt',        ev('[|]'),         ['', ''])
check('trim spaces',      ev('[a | a]'),     'a')

print('── Symbols ────────────────────────────────────────────────────────────')
check('dynamic lookup',   ev('$a', {'a':'hello'}),   'hello')
check('dynamic assign',   ev('$a=hello\n$a'),         'hello')
check('static assign',    ev('#a=hello\n$a'),          'hello')
check('bare $',           ev('$'),                    '')

print('── Transforms ─────────────────────────────────────────────────────────')
check('ucf on choice',    ev('[hello].capitalize()'), 'Hello')
check('uc on choice',     ev('[hello].toUpperCase()'), 'HELLO')
check('lc on choice',     ev('[HELLO].toLowerCase()'), 'hello')
check('transform chain',  ev('[hello].toUpperCase().toLowerCase()'), 'hello')
check('articlize a',      ev('[ant].articlize()'),    'an ant')
check('articlize b',      ev('[boy].articlize()'),    'a boy')
check('pluralize',        ev('[dog].pluralize()'),    'dogs')
check('quotify',          ev('[hi].quotify()'),       '\u201chi\u201d')
check('transform on sym', ev('$a.toUpperCase()', {'a': 'hello'}), 'HELLO')
check('bare $.quotify()', ev('$.quotify()'),          '\u201c\u201d')

print('── Object properties ───────────────────────────────────────────────────')
dog = {'name': 'Spot', 'legs': 4}
check('obj.prop',         ev('$dog.name', {'dog': dog}), 'Spot')

print('── Silent blocks ───────────────────────────────────────────────────────')
check('silent assign',    ev('{$a=hello}$a'),         'hello')
check('silent static',    ev('{#a=hello}$a'),         'hello')

print('── Statics ─────────────────────────────────────────────────────────────')
check('static once',      ev('[#a=x|#a=y]:$a')[1],    ev('[#a=x|#a=y]:$a')[1])

print('── Multi-pass ──────────────────────────────────────────────────────────')
check('deferred sym',     ev('$a.toUpperCase()\n$a=hello'), 'HELLO')
check('sym-choice',       ev('$[a|a]', {'a': 'Lucy'}),      'Lucy')
check('sym-choice.prop',  ev('$[a|a].name', {'a': {'name': 'Lucy'}}), 'Lucy')

print()
total = passed + failed
print(f'Results: {passed}/{total} passed', '✓' if not failed else f'({failed} failed)')
