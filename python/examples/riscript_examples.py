#!/usr/bin/env python3
"""
Simple examples demonstrating RiScript

To run:
    PYTHONPATH=. python3 examples/riscript_examples.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from riscript import RiScript


def main():
    """Run examples showing RiScript features."""
    
    print("=" * 60)
    print("RiScript Example")
    print("=" * 60)
    print()
    
    # Initialize RiScript interpreter
    rs = RiScript()
    
    # Example 1: Basic choice selection
    print("1. Basic Choice Selection")
    print("-" * 40)
    script = '[The quick brown fox | A slow lazy cat] jumped over the dog'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    # Example 2: Word transformation (pluralize)
    print("2. Word Transformation - pluralize")
    print("-" * 40)
    script = 'The [ox | ox].pluralize were drinking.'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    # Example 3: Dynamic assignment
    print("3. Dynamic Assignment")
    print("-" * 40)
    script = '$noun=apple\nI would like to eat $noun.articlize().'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    # Example 4: Static assignment (compile-time)
    print("4. Static Assignment")
    print("-" * 40)
    script = '#color=red\nThe $color flower bloomed.'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    # Example 5: Gate logic - Age check
    print("5. Gate Logic - Age Check")
    print("-" * 40)
    script = '[ @{$age:18} adult || minor ]'
    context = {'age': 20}
    result = rs.evaluate(script, context)
    print(f"Script:  {script}")
    print(f"Context: {context}")
    print(f"Result:  {result}")
    print()
    
    # Example 6: Comparison gate
    print("6. Gate Logic - Hours Check")
    print("-" * 40)
    script = '[ @{$hours:{@lte:12}} morning || afternoon ]'
    context = {'hours': 8}
    result = rs.evaluate(script, context)
    print(f"Script:  {script}")
    print(f"Context: {context}")
    print(f"Result:  {result}")
    print()
    
    # Example 7: Transform functions
    print("7. Transform Functions - lower()")
    print("-" * 40)
    script = '[Hello World | Hi There].lower()'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    # Example 8: Context with variables
    print("8. Context with Multiple Variables")
    print("-" * 40)
    context = {'name': 'Alice', 'city': 'New York'}
    script = '$name from $city smiled.'
    result = rs.evaluate(script, context)
    print(f"Script:  {script}")
    print(f"Context: {context}")
    print(f"Result:  {result}")
    print()
    
    # Example 9: Article generation (an vs a)
    print("9. Articles, capitilisation and norepeat")
    print("-" * 40)
    script = '$noun=[elephant | ox]\n$noun.art.cap(), $noun.nr().art...'
    result = rs.evaluate(script)
    print(f"Script:  {script}")
    print(f"Result:  {result}")
    print()
    
    print("=" * 60)


if __name__ == '__main__':
    main()
