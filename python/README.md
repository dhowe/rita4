# rita-py

Python port of [RiTa](https://github.com/dhowe/ritajs)

## Status

| Component | Status | Tests |
|-----------|--------|-------|
| RiScript interpreter | ✅ Complete | 723 passing |
| RiGrammar | ✅ Complete | 143 passing |
| `rita` package structure | ✅ Complete | — |
| `rita_dict.json` (21,987 entries) | ✅ Complete | — |
| `rita_lts.py` (Letter-to-Sound) | ✅ Complete | — |
| `rita/util.py` + `rita/randgen.py` | ✅ Complete | 227 passing |
| `rita/tokenizer.py` | ✅ Complete | 151 passing |
| `rita/inflector.py` | ✅ Complete | 763 passing |
| `rita/conjugator.py` | ✅ Complete | 279 passing |
| `rita/stemmer.py` | ✅ Complete | 6,387 passing |
| `rita/tagger.py` | ✅ Complete | 318 passing |
| `rita/analyzer.py` | ✅ Complete | 105 passing |
| `rita/lexicon.py` | ✅ Complete | 370 passing |
| `rita/markov.py` | ✅ Complete | 150 passing |
| `rita/concorder.py` | ✅ Complete | — |
| `rita/rita.py` | ✅ Complete | 200 passing |

**9,816 assertions passing** as of April 2026.

## Features

- **RiScript Interpreter**: Parser with support for choices, gates, statics, dynamics, and transforms
- **Tokenizer**: Full-featured tokenizer and untokenizer with HTML tag preservation, contraction splitting, compound-word handling, URL/email detection, and sentence splitting

## Examples

Run the included example to see RiScript in action:

```bash
PYTHONPATH=. python3 examples/riscript_examples.py
```

See [examples/riscript_examples.py](examples/riscript_examples.py) for code demonstrating:
- Choice selection
- Word transformations
- Dynamic and static assignments
- Gate logic
- Context variables
- Multi-pass evaluation

## Installation

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/dhowe/rita-py.git
cd rita-py
python3 -m venv .venv
source .venv/bin/activate
```

## Quick Start

```python
from riscript import RiScript

rs = RiScript()

# Basic evaluation
result = rs.evaluate('The [ox | ox ].pluralize run')
print(result)  # Output: "The oxen run"

# Using dynamic values
result = rs.evaluate('$name.cap() went to the store.', {'name': 'john'})
print(result)  # Output: "John went to the store."

# Gate logic
result = rs.evaluate('[ @{$age: {@gte: 18}} adult || child ]', {'age': 20})
print(result)  # Output: "adult"

# Multi-pass evaluation
result = rs.evaluate('$name=John\n$name.cap() went home.')
print(result)  # Output: "John went home."
```

```python
from rita.tokenizer import Tokenizer

t = Tokenizer()

# Tokenize
t.tokenize('The dog ran.')         # ['The', 'dog', 'ran', '.']
t.tokenize('snow-capped peaks')    # ['snow-capped', 'peaks']
t.tokenize('dog, e.g. the cat.')   # ['dog', ',', 'e.g.', 'the', 'cat', '.']
t.tokenize('We\'ve found it.')     # ["We've", 'found', 'it', '.']

# Split contractions
t.tokenize("We've found it.", {'splitContractions': True})
# ['We', 'have', 'found', 'it', '.']

# Untokenize
t.untokenize(['The', 'dog', ',', 'ran', '.'])  # 'The dog, ran.'

# Sentence splitting
t.sentences('Mr. Smith went home. He was tired.')
# ['Mr. Smith went home.', 'He was tired.']

# Word tokens (no punctuation, lowercased)
t.tokens('The Quick Brown Fox.')  # ['the', 'quick', 'brown', 'fox']
```

## Running Tests

Activate a virtual environment (`source .venv/bin/activate`), then:

### Run tests

```bash
pytest
```

### Run specific test files

```bash
pytest test_riscript.py
pytest test_grammar.py
pytest test_rita.py
pytest test_util.py
pytest test_randgen.py
```

### Run specific test classes

```bash
pytest test_riscript.py::TestGates
pytest test_riscript.py::TestChoices
pytest test_riscript.py::TestTransforms
```

### Run specific test methods

```bash
pytest test_riscript.py::TestGates::test_else_gates
pytest test_riscript.py::TestChoices::test_multiword_choice
```
## Core Concepts

### RiScript Statements

- **Dynamic statements** (`$foo=bar`) - Runtime assignments
- **Static statements** (`#foo=[a|b]`) - Compile-time replacements
- **Silent blocks** (`{$foo=bar}`) - Silent evaluation

### Choices

```
[option1 | option2 | option3]
```

Randomly selects one option (weights optional).

### Gates

```
[ @{$value: {@gt: 10} } condition || alternative ]
```

Conditional logic using Mingo-style queries.

### Transforms

```
$word.lower() | $word.upper() | $word.pluralize()
```

Built-in transforms: articlize, lower, uc, pluralize, cap, etc.

## Test Coverage

- **RiScript / RiGrammar**:
  - Gate evaluation (boolean, equality, comparison, existence, regex, deferred)
  - Choice selection (weighted, multi-word, transforms, spacing variants)
  - Transform system (custom, static, context-based, no-parens, old-style `$.fn`)
  - Statement handling (dynamic, static, silent `{$foo=...}`, line-break form)
  - Assignment types (inline `[$foo=...]`, line `$foo=...`, silent `{$foo=...}`, static `#foo=...`)
  - Object method/property access from context
  - Comment stripping, continuation lines, HTML entities, Unicode/emoji
  - Full JavaScript (riscript.tests.js + grammar.tests.js) parity

- **Tokenizer** (151 assertions, full JS parity):
  - `tokenize()` / `untokenize()` round-trips
  - Compound words, abbreviations, contractions (split on/off)
  - HTML tag preservation through tokenize → untokenize
  - Decimal numbers, numbers with commas, dashes (em/en/double-hyphen)
  - URLs and email addresses as single tokens
  - Underscore-to-space (French/Spanish phrases)
  - `sentences()` with abbreviation awareness
  - `tokens()` with `sort`, `caseSensitive`, `ignoreStopWords`, `includePunct`, `splitContractions`

## Project Structure

```
rita-py/
├── riscript.py          # Core RiScript interpreter
├── randgen.py           # Shim → rita/randgen.py
├── util.py              # Shim → rita/util.py
├── rita/
│   ├── __init__.py      # Package entry point
│   ├── tokenizer.py     # Tokenizer / untokenizer / sentences
│   ├── util.py          # Util + RE classes
│   ├── randgen.py       # Seeded Mersenne Twister PRNG
│   ├── rita_dict.json   # CMU pronunciation dictionary (21,987 entries)
│   └── rita_lts.py      # Letter-to-Sound fallback rules
├── examples/
│   ├── riscript_examples.py  # Demo program
│   └── README.md
├── test_*.py            # Test suites
└── README.md            # This file
```

## License

GNU General Public License v3.0 (GPL-3.0)
