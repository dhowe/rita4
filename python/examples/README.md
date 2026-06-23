# Examples

This folder contains example programs.

## Example: simple_example.py

Example demonstrating RiScript features:

- **Basic Choices**: `['option1' | 'option2']` - Random selection from options
- **Transforms**: `.pluralize()`, `.lower()`, `.articlize()` - Word transformations
- **Dynamic Statements**: `$variable=value` - Runtime variable assignment
- **Static Statements**: `#variable=value` - Compile-time substitution
- **Gate Logic**: `[ {@condition: value} yes || no ]` - Conditional evaluation
- **Context Variables**: User-provided values for dynamic substitution
- **Multi-pass Evaluation**: Nested expressions resolved over multiple passes

## Running Examples

From the `rita-py` directory:

```bash
python3 examples/riscript_examples.py
```

## Quick Usage

```python
from riscript import RiScript

rs = RiScript()

# Basic evaluation
result = rs.evaluate('[The quic[k] fox | A slow cat].lower()')
print(result)  # "the quic fox" or "a slow cat"

# With context
result = rs.evaluate('Hello $name', {'name': 'Alice'})
print(result)  # "Hello Alice"

# Gate logic
result = rs.evaluate('[ @{$age:18} adult || child ]', {'age': 20})
print(result)  # "adult"
```

## Features Demonstrated

- ✅ Choice selection with weighted probabilities
- ✅ Symbolic transformations (pluralize, lowercase, uppercase, article)
- ✅ Dynamic and static variable assignments
- ✅ Conditional logic with gate operators
- ✅ Multi-pass evaluation
- ✅ Custom context variables
- ✅ Expression evaluation

See `simple_example.py` for complete, commented code.
