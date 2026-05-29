# -----------------------------------
# WEEK 4 - MINI-TUTOR v1  (FULLY FIXED)
# CORE AGENT  —  GROQ API
# -----------------------------------
#
# Fixed in this version:
#   1. Removed timeout_s from tool schema — Groq was generating broken JSON
#      when it tried to pass two separate args {code}{timeout_s}
#   2. input() calls are mocked before execution — no more hangs
#   3. Handles dict / JSON / plain-text input gracefully
#   4. SDK object → plain dict conversion (400 error fix)
#   5. GROQ_MODEL variable name (was GROK_MODEL typo)
#   6. 300-line limit, 15s timeout, 80+ doc topics
#   7. Auto-installs missing pip packages
#
# Requires:  pip install openai python-dotenv ruff
#            GROQ_API_KEY in .env
# -----------------------------------

import subprocess
import tempfile
import os
import sys
import json
import re

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# CONSTANTS
# -----------------------------------

MAX_TOOL_CALLS  = 8
MAX_CODE_LINES  = 300
TIMEOUT_SECONDS = 15
GROQ_MODEL      = "llama-3.3-70b-versatile"

# -----------------------------------
# STDLIB SET  (never pip-install these)
# -----------------------------------

STDLIB_MODULES = {
    "os", "sys", "re", "json", "math", "time", "datetime", "random",
    "string", "io", "pathlib", "collections", "itertools", "functools",
    "operator", "copy", "pprint", "types", "typing", "abc", "dataclasses",
    "enum", "struct", "array", "queue", "heapq", "bisect", "weakref",
    "gc", "inspect", "ast", "dis", "traceback", "warnings", "contextlib",
    "threading", "multiprocessing", "subprocess", "socket", "ssl",
    "http", "urllib", "email", "html", "xml", "csv", "sqlite3",
    "hashlib", "hmac", "secrets", "base64", "uuid", "tempfile",
    "shutil", "glob", "fnmatch", "stat", "logging", "unittest",
    "doctest", "argparse", "configparser", "pickle", "shelve",
    "zlib", "gzip", "zipfile", "tarfile", "platform", "signal",
    "atexit", "builtins", "keyword", "token", "tokenize",
    "textwrap", "difflib", "decimal", "fractions", "statistics",
    "cmath", "numbers", "concurrent", "asyncio", "selectors",
}


# -----------------------------------
# HELPER: detect input type
# -----------------------------------

def _classify_input(text: str) -> str:
    """
    Classify what the user submitted:
      'python'   — Python source code
      'dict'     — a Python dict literal  { "key": value, ... }
      'json'     — a JSON string
      'question' — a plain English question
    """
    stripped = text.strip()

    # JSON object / array
    if (stripped.startswith("{") and stripped.endswith("}")) or \
       (stripped.startswith("[") and stripped.endswith("]")):
        try:
            json.loads(stripped)
            return "json"
        except json.JSONDecodeError:
            pass
        # Might be a Python dict / list literal
        try:
            import ast
            ast.literal_eval(stripped)
            return "dict"
        except Exception:
            pass

    # Python dict literal with unquoted keys
    if re.match(r'^\s*\{', stripped) and ":" in stripped:
        return "dict"

    # Has Python keywords / def / class / import
    python_signals = [
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+',
        r'\bimport\s+\w+',
        r'\bfor\s+\w+\s+in\b',
        r'\bwhile\s+.+:',
        r'\bif\s+.+:',
        r'\bprint\s*\(',
        r'\breturn\b',
        r'=\s*\[',
        r'=\s*\{',
    ]
    if any(re.search(p, stripped) for p in python_signals):
        return "python"

    return "question"


# -----------------------------------
# HELPER: auto-install missing packages
# -----------------------------------

def _install_missing_packages(code: str) -> list:
    pattern = re.compile(
        r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        re.MULTILINE
    )
    found    = set(re.findall(pattern, code))
    external = [p for p in found if p not in STDLIB_MODULES]

    installed = []
    for pkg in external:
        try:
            __import__(pkg)
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg, "-q"],
                    capture_output=True,
                    timeout=30
                )
                installed.append(pkg)
            except Exception:
                pass
    return installed


# -----------------------------------
# HELPER: mock input() calls
# -----------------------------------

_INPUT_MOCK = """\
# ── AUTO-INJECTED BY TUTOR ──────────────────────────────────
# input() is mocked so the program runs without hanging.
# Each call returns a safe placeholder value.
import builtins as _builtins
_input_call_count = 0
_INPUT_RESPONSES = [
    "Alice", "1000", "Bob", "500", "1", "2", "3", "test", "yes", "no",
    "0", "10", "hello", "world", "quit", "exit", "6"
]
def _mock_input(prompt=""):
    global _input_call_count
    print(f"[INPUT] {prompt}", end="")
    response = _INPUT_RESPONSES[_input_call_count % len(_INPUT_RESPONSES)]
    _input_call_count += 1
    print(response)
    return response
_builtins.input = _mock_input
# ────────────────────────────────────────────────────────────

"""

def _has_input_calls(code: str) -> bool:
    # Match input( that is not inside a comment or string
    return bool(re.search(r'\binput\s*\(', code))

def _inject_input_mock(code: str) -> str:
    return _INPUT_MOCK + code


# -----------------------------------
# HELPER: handle dict / JSON input
# -----------------------------------

def _wrap_data_as_code(text: str, kind: str) -> str:
    """
    Wrap a raw dict or JSON string in runnable Python
    so run_python can analyse it.
    """
    if kind == "json":
        return (
            f"import json, pprint\n"
            f"data = json.loads({repr(text)})\n"
            f"print('Type:', type(data).__name__)\n"
            f"print('Keys:', list(data.keys()) if isinstance(data, dict) else f'Length: {{len(data)}}')\n"
            f"print('\\nContent:')\n"
            f"pprint.pprint(data)\n"
        )
    else:  # dict / list literal
        return (
            f"import pprint\n"
            f"data = {text}\n"
            f"print('Type:', type(data).__name__)\n"
            f"if isinstance(data, dict):\n"
            f"    print('Keys:', list(data.keys()))\n"
            f"    print('Items:')\n"
            f"    for k, v in data.items():\n"
            f"        print(f'  {{k}}: {{v}}')\n"
            f"elif isinstance(data, list):\n"
            f"    print('Length:', len(data))\n"
            f"    pprint.pprint(data)\n"
            f"else:\n"
            f"    pprint.pprint(data)\n"
        )


# -----------------------------------
# TOOL 1 : RUN PYTHON
# -----------------------------------

def run_python(code: str) -> dict:
    """
    Execute Python code in a subprocess sandbox.
    - Detects and mocks input() calls so interactive programs run
    - Auto-installs missing pip packages
    - Handles dict / JSON / file-content passed as code
    - Max 300 lines, 15s timeout
    """

    if not code or not code.strip():
        return {"success": False, "error": "No Python code was provided."}

    # Detect input type
    kind = _classify_input(code)

    # If user pasted a raw dict or JSON — wrap it
    if kind in ("dict", "json"):
        code = _wrap_data_as_code(code, kind)
        note = f"Input was detected as a {kind.upper()} — wrapped in Python to analyse it."
    else:
        note = None

    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return {
            "success": False,
            "error": (
                f"Code is {len(lines)} lines — the limit is {MAX_CODE_LINES}. "
                "Consider breaking it into smaller sections."
            )
        }

    # Mock input() if present
    input_mocked = False
    if _has_input_calls(code):
        code         = _inject_input_mock(code)
        input_mocked = True

    # Auto-install missing packages
    installed = _install_missing_packages(code)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
        os.remove(temp_path)

        response = {
            "success":      True,
            "stdout":       result.stdout,
            "stderr":       result.stderr,
            "returncode":   result.returncode,
            "input_mocked": input_mocked,
        }
        if note:
            response["note"] = note
        if installed:
            response["packages_installed"] = installed

        return response

    except subprocess.TimeoutExpired:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return {
            "success": False,
            "error": (
                f"Execution stopped after {TIMEOUT_SECONDS}s. "
                "This usually means an infinite loop or a very slow algorithm. "
                "Check loop conditions or add print statements to trace progress."
            )
        }

    except Exception as e:
        return {"success": False, "error": f"Execution environment error: {str(e)}"}


# -----------------------------------
# TOOL 2 : LINT CODE
# -----------------------------------

def lint_code(code: str) -> dict:
    """Run ruff linter on Python code."""

    if not code or not code.strip():
        return {"success": False, "error": "No code was provided for linting."}

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["ruff", "check", temp_path, "--select", "E,F,W"],
            capture_output=True,
            text=True
        )
        os.remove(temp_path)

        lint_output = result.stdout.replace(temp_path, "<your_code>")
        return {
            "success":      True,
            "issues_found": bool(lint_output.strip()),
            "lint_output":  lint_output,
        }

    except FileNotFoundError:
        return {"success": False, "error": "ruff not installed. Run: pip install ruff"}

    except Exception as e:
        return {"success": False, "error": f"Linter error: {str(e)}"}


# -----------------------------------
# TOOL 3 : DOC SEARCH  (80+ concepts)
# -----------------------------------

def doc_search(keyword: str) -> dict:
    """Search 80+ Python documentation topics with partial + fuzzy matching."""

    if not keyword or not keyword.strip():
        return {"success": False, "error": "No keyword was provided."}

    python_docs = {
        # Core data types
        "integer":      "int stores whole numbers. Arithmetic: +,-,*,/,//,%,**. Convert: int(). int('5')=5, int(3.9)=3 (truncates). Beware: 5/2=2.5 (float division), 5//2=2 (floor division).",
        "float":        "float stores decimals. Precision issue: 0.1+0.2≠0.3 exactly. Use round(x,n). For exact decimals use the 'decimal' module. Convert: float('3.14').",
        "string":       "str stores text in '' or \"\". Immutable. Methods: .strip(),.split(),.join(),.replace(),.find(),.startswith(),.endswith(),.upper(),.lower(),.format(). f-strings: f'Hello {name}'. Multiline: triple quotes.",
        "boolean":      "bool is True or False. Falsy values: 0, 0.0, '', [], {}, set(), None. Everything else is truthy. Operators: and, or, not. bool(x) converts anything.",
        "none":         "None is Python's null/empty value. Functions with no return give None. Check with 'if x is None:' — never 'if x == None:'. Useful as a default parameter sentinel.",
        "list":         "list: ordered, mutable. [], list(). Methods: .append(x),.extend(lst),.insert(i,x),.remove(x),.pop(i),.sort(),.reverse(),.index(x),.count(x). Supports slicing. Negative index: lst[-1] is last.",
        "tuple":        "tuple: ordered, immutable. (a,b) or just a,b. Can't change after creation. Unpack: x,y=(1,2). Single item: (1,). Use as dict keys (unlike lists). Named tuples from collections.namedtuple.",
        "dictionary":   "dict: key-value pairs. {}, dict(). Access: d[k] or d.get(k, default). Methods: .keys(),.values(),.items(),.update(),.pop(),.setdefault(). Dict comprehension: {k:v for k,v in items}. Keys must be hashable.",
        "set":          "set: unique unordered values. set() — not {} (that's dict). .add(),.remove(),.discard(). Operations: |union, &intersection, -difference, ^symmetric_diff. Fast membership: 'x in s' is O(1).",
        "bytes":        "bytes: immutable raw binary. b'hello' or bytes(n). Immutable. .decode('utf-8') → str. str.encode('utf-8') → bytes. Used in file I/O, networking, hashing.",
        "complex":      "complex: real+imaginary. 3+4j. .real and .imag attributes. abs(3+4j)=5.0 (magnitude). Used in signal processing, scientific computing.",
        # Variables & operators
        "variable":     "Variables store references to objects. Dynamically typed — no declaration needed. snake_case convention. UPPER_CASE for constants. Multiple assignment: a=b=c=0. Swap: a,b=b,a.",
        "operator":     "Arithmetic: +,-,*,/,//,%,**. Comparison: ==,!=,<,>,<=,>=. Logical: and,or,not. Identity: is,is not. Membership: in,not in. Bitwise: &,|,^,~,<<,>>. Augmented: +=,-=,*=,/=,//=,%=,**=.",
        "comparison":   "==checks value equality, 'is' checks identity (same object). Use 'is' only for None/True/False. Chain: 0<x<10. 'in' checks membership in list/dict/set/string.",
        "casting":      "Type conversion: int('5'), float('3.14'), str(42), bool(0), list('abc')→['a','b','c'], tuple([1,2]), set([1,1,2])→{1,2}. ValueError if impossible: int('hello').",
        # Control flow
        "if":           "if-elif-else: 'if cond: ... elif other: ... else: ...'. Ternary: x = a if cond else b. Conditions use any truthy/falsy value. No switch — use if-elif or match-case (Python 3.10+).",
        "for loop":     "for iterates any iterable. 'for item in sequence:'. range(n), range(start,stop), range(start,stop,step). enumerate() for index+value. zip() for parallel iteration. else clause runs if loop completes without break.",
        "while loop":   "'while condition:' runs until condition is False. Always ensure condition can become False or use break. else clause runs if loop completes without break. Use for unknown iteration count.",
        "loop":         "for: iterate sequences. while: condition-based. break: exit loop. continue: skip to next iteration. else on loop: runs if no break. range(), enumerate(), zip() are common loop helpers.",
        "break":        "break exits the nearest loop immediately. Used inside if to stop early. Works in for and while. Common pattern: search loop that breaks when found, else clause handles 'not found'.",
        "continue":     "continue skips rest of current iteration, jumps to next. Useful to skip invalid values. Example: for x in data: if x<0: continue; process(x).",
        "range":        "range(stop), range(start,stop), range(start,stop,step). Doesn't include stop. range(5)→0,1,2,3,4. Negative step: range(10,0,-1). list(range(n)) to materialise. Memory efficient — doesn't build a list.",
        "pass":         "pass is a no-op placeholder. Use in empty class/function/if bodies. Prevents SyntaxError from empty blocks. Replace with real code when ready.",
        # Functions
        "function":     "def name(params): ... return value. Parameters are local. Default args: def f(x=10). *args: extra positional as tuple. **kwargs: extra keyword as dict. Docstring: first string inside function.",
        "return":       "return sends value back to caller. No return → None. Return multiple: return a,b (tuple). Unpack: x,y=f(). Early return for guard clauses. return in a generator becomes StopIteration.",
        "argument":     "Positional: f(1,2). Keyword: f(x=1,y=2). *args collects extra positionals as tuple. **kwargs collects extra keywords as dict. Keyword-only args after *: def f(*,key). Positional-only before /: def f(x,/).",
        "lambda":       "lambda args: expression. Single expression only. Examples: lambda x: x*2, lambda x,y: x+y. Used with map/filter/sorted. For anything complex, use def — it's more readable.",
        "scope":        "LEGB rule: Local → Enclosing → Global → Built-in. Assignment inside function creates local var. 'global x' to modify module global. 'nonlocal x' to modify enclosing function's var.",
        "closure":      "A closure is a function that captures variables from its enclosing scope. def outer(): x=10; def inner(): return x; return inner. Useful for factory functions and decorators.",
        "decorator":    "@decorator wraps a function. def my_dec(func): def wrapper(*a,**k): ...; return func(*a,**k); return wrapper. Built-in: @staticmethod,@classmethod,@property. @functools.wraps preserves metadata.",
        "generator":    "yield makes a generator — produces values lazily. def gen(): yield 1; yield 2. Saves memory for large sequences. Generator expression: (x*2 for x in range(10)). next() gets one value.",
        "comprehension":"[expr for x in it if cond]. Dict: {k:v for ...}. Set: {expr for ...}. Generator: (expr for ...). Faster than append loop. Avoid nested comprehensions deeper than 2 levels.",
        "recursion":    "Function calling itself. MUST have base case. Python limit: 1000 (RecursionError). sys.setrecursionlimit(n) to raise. Good for: trees, fractals, divide-and-conquer. Tail recursion not optimised — use loop for deep recursion.",
        "map":          "map(func, iterable) applies func to every item lazily. list(map(str,[1,2,3]))→['1','2','3']. Multiple iterables: map(func,a,b). Often replaced by list comprehension for clarity.",
        "filter":       "filter(func, iterable) keeps items where func returns True. list(filter(lambda x:x>0,[-1,2,-3]))→[2]. None as func keeps truthy items. Often replaced by [x for x in lst if cond].",
        "zip":          "zip(a,b) pairs elements: list(zip([1,2],[3,4]))→[(1,3),(2,4)]. Stops at shortest. zip_longest from itertools fills missing. Unzip: a,b=zip(*pairs). Great for dict creation: dict(zip(keys,values)).",
        "sorted":       "sorted(it, key=func, reverse=False) → new sorted list. list.sort() sorts in place. key= for custom: sorted(words,key=len), sorted(dicts,key=lambda d:d['age']). Stable sort.",
        # OOP
        "class":        "class Name: ... def __init__(self,...): self.attr=value. Create: obj=Name(args). Methods need self. Class variables shared across instances. Instance variables per object.",
        "object":       "Everything in Python is an object with type, id, value. Variables are references. dir(obj) lists attributes/methods. hasattr/getattr/setattr/delattr for dynamic access.",
        "inheritance":  "class Child(Parent): ... super().__init__() calls parent init. Override methods by redefining. Multiple inheritance: class C(A,B). MRO (Method Resolution Order) determines which method is called.",
        "super":        "super() returns proxy of parent class. super().__init__(args) calls parent constructor. super().method() calls parent's version. Avoids hard-coding parent class name.",
        "method":       "Instance methods: first param is self. Class methods: @classmethod, first param is cls. Static methods: @staticmethod, no special param. __init__ is constructor, __str__ for print, __repr__ for repr().",
        "dunder":       "Magic methods: __init__(constructor), __str__(str()), __repr__(repr()), __len__(len()), __eq__(==), __lt__(<), __add__(+), __getitem__([]), __iter__, __next__. Define to customise built-in behaviour.",
        "property":     "@property makes method act as attribute. @name.setter for writing. @name.deleter for del. Allows validation without changing interface: obj.x = -1 can raise ValueError.",
        "abstract":     "from abc import ABC, abstractmethod. class Shape(ABC): @abstractmethod def area(self): pass. Can't instantiate ABC directly. Forces subclasses to implement abstract methods.",
        "dataclass":    "@dataclass auto-generates __init__,__repr__,__eq__ from type-annotated fields. from dataclasses import dataclass, field. frozen=True for immutable. Python 3.7+.",
        "polymorphism": "Same method name, different behaviour per class. Python uses duck typing — if it has the method, it works. isinstance() to check type when needed. Prefer duck typing over type checking.",
        "encapsulation":"_name: protected by convention. __name: name-mangled to _ClassName__name. Python doesn't enforce access control — it's convention. Use @property for controlled attribute access.",
        # Exception handling
        "exception":    "Built-in exceptions: ValueError,TypeError,KeyError,IndexError,AttributeError,NameError,ZeroDivisionError,FileNotFoundError,ImportError,RuntimeError,StopIteration,OverflowError,MemoryError.",
        "try":          "try: risky code. except ErrorType as e: handle it. Multiple excepts for different errors. else: runs if no exception. finally: always runs (cleanup). Catch specific exceptions — avoid bare 'except:'.",
        "raise":        "raise ValueError('message') throws an exception. raise re-raises current exception. Custom exceptions: class MyError(Exception): pass. raise ... from e to chain exceptions.",
        "assert":       "assert condition, 'message' raises AssertionError if False. Disabled with -O flag. Use for invariants in development. Don't use for user input validation (use if/raise instead).",
        # File I/O
        "file":         "open(path, mode) opens a file. Always use 'with open(path) as f:' — auto-closes. Modes: 'r'(read),'w'(write/overwrite),'a'(append),'x'(create new),'b'(binary),'+'(read+write).",
        "read":         "f.read() → whole file as str. f.readline() → one line. f.readlines() → list of lines. for line in f: iterates lines efficiently. f.read(n) reads n bytes/chars.",
        "write":        "f.write(str) writes string (no auto newline — add \\n). f.writelines(list). 'w' overwrites. 'a' appends. Check file exists with os.path.exists() before overwriting.",
        "csv":          "import csv. csv.reader(f) → rows as lists. csv.DictReader(f) → rows as dicts. csv.writer(f).writerow(row). csv.DictWriter(f,fieldnames).writerow(dict). Always open with newline=''.",
        "json":         "import json. json.loads(str)→obj. json.dumps(obj)→str (indent=4 for pretty). json.load(f)→obj from file. json.dump(obj,f) writes to file. Only str keys in JSON dicts. Handles: str,int,float,bool,None,list,dict.",
        "os path":      "os.path: .exists(),.isfile(),.isdir(),.join(),.basename(),.dirname(),.splitext(),.abspath(). os.listdir(). os.makedirs(path,exist_ok=True). os.remove(). os.rename(). pathlib.Path is the modern alternative.",
        # Standard library
        "import":       "'import module' or 'from module import name' or 'import module as alias'. __name__=='__main__' guards script code. Circular imports: restructure or use local imports. importlib for dynamic imports.",
        "math":         "import math. math.sqrt(),floor(),ceil(),pow(),log(),log2(),log10(). math.pi,math.e,math.inf,math.nan. math.factorial(),gcd(),lcm(). math.sin(),cos(),tan() (radians). math.degrees(),radians().",
        "random":       "import random. random.random()→[0,1). random.randint(a,b) inclusive. random.choice(seq). random.choices(seq,weights,k=n). random.shuffle(lst) in-place. random.sample(seq,k) no replacement. random.seed(n).",
        "datetime":     "from datetime import datetime,date,timedelta. datetime.now(),date.today(). timedelta(days=7). .strftime('%Y-%m-%d %H:%M'). datetime.strptime(str,'%Y-%m-%d'). .timestamp(). Arrow library for easier datetime handling.",
        "collections":  "Counter(iterable)→{item:count}. defaultdict(list) auto-creates missing keys. OrderedDict (less needed 3.7+). deque: fast O(1) append/pop both ends. namedtuple: tuple with named fields. ChainMap merges dicts.",
        "itertools":    "chain(*iters),chain.from_iterable(). product(a,b). combinations(it,r). permutations(it,r). groupby(it,key). islice(it,n). repeat(x,n). accumulate(it). All return iterators — wrap in list() to see.",
        "functools":    "reduce(func,it,initial). lru_cache() / cache() — memoisation. partial(func,*args) fixes args. wraps(func) preserves docstring in decorators. total_ordering fills in comparison methods from __eq__+one other.",
        "re":           "import re. re.match(pat,s)→match at start. re.search(pat,s)→first match anywhere. re.findall(pat,s)→list of matches. re.sub(pat,repl,s)→replaced string. re.compile(pat) for reuse. Groups: (pattern). Flags: re.IGNORECASE.",
        "sys":          "sys.argv[0]=script name, [1:]=CLI args. sys.exit(0)=success,non-zero=error. sys.path=module search list. sys.stdin/stdout/stderr. sys.version. sys.getrecursionlimit()/setrecursionlimit(n).",
        "os":           "os.getcwd(),os.chdir(path). os.listdir(dir). os.makedirs(path,exist_ok=True). os.remove(file). os.rename(src,dst). os.environ['KEY'] or os.getenv('KEY','default'). os.path for path operations.",
        "typing":       "from typing import List,Dict,Tuple,Set,Optional,Union,Any,Callable,TypeVar. Optional[str]=str|None. Union[int,str]. Type hints not enforced at runtime — use mypy to check. Python 3.10+: use list[int] directly.",
        # Memory & performance
        "mutable":      "Mutable: list,dict,set,bytearray — can change after creation. Immutable: int,float,str,tuple,frozenset,bytes. Gotcha: def f(x=[]): shares same list across calls. Use def f(x=None): if x is None: x=[].",
        "reference":    "Variables are references to objects. a=b makes both point to same object. Integers and short strings may be interned (same object). For lists/dicts: copy() or [:] for shallow copy.",
        "shallow copy": "list[:], list.copy(), dict.copy(), copy.copy() — new container, same inner objects. Nested list modification affects both copies. Use deepcopy for full independence.",
        "deep copy":    "import copy; copy.deepcopy(obj) — fully independent copy including nested objects. Slower. Use when modifying nested structures. Handles circular references.",
        "complexity":   "list: O(1) append, O(n) insert/search. dict/set: O(1) lookup. Sorting: O(n log n). Nested loops: O(n²). Use set/dict for fast lookup. Use deque for queue. Use heapq for priority queue.",
        # Intermediate topics
        "enumerate":    "enumerate(it,start=0) → (index,value) pairs. for i,val in enumerate(lst): replaces for i in range(len(lst)):. Cleaner and more Pythonic. start=1 for 1-based indexing.",
        "unpacking":    "a,b=[1,2]. Extended: first,*rest=[1,2,3,4]. Swap: a,b=b,a. Ignore: _,useful=pair. Function args: func(*list), func(**dict). Nested: (a,b),c = (1,2),3.",
        "slice":        "lst[start:stop:step]. Omit for defaults. lst[::-1] reverses. lst[::2] every other. Slices make shallow copies. slice() object for named slices. Strings and tuples support slicing too.",
        "context manager":"'with' statement: with open(f) as h: auto-calls __exit__ even on exception. Create with __enter__/__exit__ methods or @contextmanager from contextlib. Use for files, locks, DB connections, temp dirs.",
        "walrus":       "Walrus := assigns and returns: if (n:=len(lst))>10: print(n). While: while chunk:=f.read(8192): process(chunk). Python 3.8+. Avoids computing same value twice.",
        "f-string":     "f'{expr}' embeds any expression. Format: f'{pi:.2f}', f'{n:>10}', f'{x:,}'. Debug: f'{x=}' prints 'x=value'. Multiline: use \\ or parentheses. Faster than .format() and %.",
        "global":       "'global x' lets function read+write module-level x. Without it, assigning x in function creates new local x (even if global x exists). Avoid globals — pass as parameters instead.",
        "nonlocal":     "'nonlocal x' lets nested function modify enclosing function's x. Without it, assignment creates new local x. Used in closures and decorators.",
        "match":        "match value: case 1: ... case str() as s: ... case {'key':v}: ... case [first,*rest]: ... case _: (default). Python 3.10+. Structural pattern matching — more powerful than if-elif.",
        "async":        "async def defines coroutine. await pauses until result ready. asyncio.run(main()) starts event loop. async for, async with. Use for I/O-bound concurrency. For CPU-bound: multiprocessing.",
        "thread":       "import threading. Thread(target=func,args=(a,)). .start(),.join(). Lock() prevents race conditions. Use for I/O-bound tasks. GIL limits CPU parallelism — use multiprocessing for CPU.",
        "process":      "import multiprocessing. Process(target=func). Pool.map(func,items) parallelises. Queue/Pipe for communication. Bypasses GIL for CPU-bound tasks. More overhead than threads.",
        "input":        "input(prompt) reads a line from stdin as a STRING. Always convert if needed: int(input()), float(input()). Wrap in try-except for invalid input. In non-interactive code, mock with sys.stdin or patch.",
        "format":       "str.format(): 'Hello {}'.format(name). f-strings: f'Hello {name}'. Old style: 'Hello %s' % name. Format spec: {:.2f} decimals, {:>10} right-align, {:,} thousands separator, {:b} binary.",
        "error":        "Common errors: SyntaxError(bad syntax), IndentationError(bad indent), NameError(undefined var), TypeError(wrong type op), ValueError(right type wrong value), IndexError(bad index), KeyError(missing dict key), AttributeError(missing attr).",
        "debug":        "Debugging: print() statements, Python debugger pdb (import pdb;pdb.set_trace()), breakpoint() (Python 3.7+). VS Code/PyCharm have visual debuggers. Read the traceback bottom-up — last line is the actual error.",
    }

    kw = keyword.lower().strip()

    # Pass 1: topic contains keyword or keyword contains topic
    matches = [
        {"topic": t, "explanation": e}
        for t, e in python_docs.items()
        if kw in t or t in kw
    ]

    # Pass 2: any meaningful word in topic appears in keyword
    if not matches:
        matches = [
            {"topic": t, "explanation": e}
            for t, e in python_docs.items()
            if any(w in kw for w in t.split() if len(w) > 2)
        ]

    # Pass 3: keyword appears inside explanation text
    if not matches:
        matches = [
            {"topic": t, "explanation": e}
            for t, e in python_docs.items()
            if kw in e.lower()
        ]

    if not matches:
        return {
            "success": True,
            "results": [],
            "message": (
                f"No documentation found for '{keyword}'. "
                f"Available topics: {', '.join(sorted(python_docs.keys()))}"
            )
        }

    return {"success": True, "results": matches}


# -----------------------------------
# TOOL REGISTRY & SCHEMAS
# -----------------------------------

TOOL_FUNCTIONS = {
    "run_python": run_python,
    "lint_code":  lint_code,
    "doc_search": doc_search,
}

# KEY FIX: run_python schema has ONLY 'code' — no timeout_s.
# When timeout_s was in the schema, Groq generated two separate JSON
# objects that merged into broken JSON: {"code":"..."}{"timeout_s":15}
# causing the 400 tool_use_failed error every time.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute Python code in a subprocess sandbox. "
                "Automatically mocks input() calls so interactive programs run without hanging. "
                "Auto-installs missing pip packages. Handles raw dicts and JSON. "
                f"Max {MAX_CODE_LINES} lines. ALWAYS call this first when student submits code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The complete Python code to execute."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lint_code",
            "description": (
                "Run ruff linter to find style issues, undefined names, "
                "and unused variables. Use when code runs but may have quality problems."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to lint."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "doc_search",
            "description": (
                "Search 80+ Python documentation topics. Covers data types, OOP, "
                "exceptions, file I/O, standard library, functional tools, debugging, "
                "and intermediate Python. Use when student is confused about a concept."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Python concept to look up. Examples: 'list', 'decorator', 'async', 'input', 'error', 'debug'."
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


# -----------------------------------
# TOOL EXECUTOR
# -----------------------------------

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({
            "success": False,
            "error": f"Unknown tool '{tool_name}'. Available: {list(TOOL_FUNCTIONS.keys())}"
        })
    try:
        return json.dumps(TOOL_FUNCTIONS[tool_name](**tool_input))
    except TypeError as e:
        return json.dumps({"success": False, "error": f"Wrong arguments: {str(e)}"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Tool crashed: {str(e)}"})


# -----------------------------------
# SYSTEM PROMPT
# -----------------------------------

SYSTEM_PROMPT = """You are Mini-Tutor, a patient AI coding tutor for Python learners.
Your goal is to help students UNDERSTAND bugs — never to write fixes for them.

RULES:
1. When a student submits code, ALWAYS call run_python first to see actual runtime behaviour.
2. If input() calls were mocked, explain that the program ran with simulated input values and focus on the logic/bugs.
3. If the student pasted a dict or JSON, the tool analysed its structure — explain what you see.
4. NEVER reveal the corrected code. Use Socratic questions to guide the student.
5. Structure every reply EXACTLY like this:

   **Diagnosis:** (one sentence — what is wrong or what the output shows)
   **Question:** (one guiding question that nudges the student toward the issue)
   **Next Step:** (one small concrete action to try)

6. If code runs but output is wrong, ask what they expected vs what they got.
7. If the student asks for the direct answer or mentions graded work, redirect with a question.
8. Use doc_search when the student seems confused about a concept.
9. Use lint_code when code runs correctly but quality/style could be improved.
10. Tone: warm, encouraging, never condescending. Be transparent that you are an AI tutor.
11. Maximum 8 tool calls per turn."""


# -----------------------------------
# AGENT LOOP
# -----------------------------------

def run_tutor_agent(
    student_message: str,
    conversation_history: list = None
) -> tuple:

    client = OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    if conversation_history is None:
        conversation_history = []

    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": student_message}]
    )

    tool_call_count = 0
    final_reply     = ""

    while True:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=1500,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        choice  = response.choices[0]
        message = choice.message
        finish  = choice.finish_reason

        # Convert SDK object → plain dict (prevents 400 errors on subsequent turns)
        assistant_dict: dict = {
            "role":    "assistant",
            "content": message.content or ""
        }
        if message.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id":       tc.id,
                    "type":     "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        messages.append(assistant_dict)

        if finish in ("stop", "length"):
            final_reply = message.content or ""
            break

        if finish == "tool_calls" and message.tool_calls:
            for tc in message.tool_calls:
                tool_call_count += 1
                if tool_call_count > MAX_TOOL_CALLS:
                    result_content = json.dumps({
                        "success": False,
                        "error": "Tool call limit reached."
                    })
                else:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    result_content = execute_tool(tc.function.name, args)

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_content
                })
        else:
            final_reply = "I ran into an unexpected state. Please try submitting your code again."
            break

    updated_history = messages[1:]
    return final_reply, updated_history


# -----------------------------------
# CLI ENTRY POINT
# -----------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  MINI-TUTOR  —  Fully Fixed  —  CLI Mode")
    print("  Type 'quit' to exit.")
    print("=" * 55)

    history = []
    while True:
        print("\nPaste your Python code, a dict, or a question.")
        print("Press ENTER twice to submit.\n")

        lines, blank_count = [], 0
        while True:
            line = input()
            if line.lower().strip() == "quit":
                print("\nGoodbye! Keep coding.")
                exit()
            if line == "":
                blank_count += 1
            else:
                blank_count = 0
            if blank_count == 2:
                break
            lines.append(line)

        student_input = "\n".join(lines).strip()
        if not student_input:
            print("Nothing entered — try again.")
            continue

        print("\n[Tutor is thinking...]\n")
        reply, history = run_tutor_agent(student_input, history)
        print("-" * 55)
        print("TUTOR:\n")
        print(reply)
        print("-" * 55)