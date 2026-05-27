# -----------------------------------
# WEEK 4 - MINI-TUTOR v1  (GENERALISED)
# CORE AGENT  —  GROQ API
# -----------------------------------
#
# Generalised version:
#   • No arbitrary line limit — accepts real programs up to 300 lines
#   • Auto-installs missing pip packages before running
#   • 80+ concept doc_search (covers beginner → intermediate Python)
#   • All previous bugs fixed (SDK object → dict, GROQ_MODEL name, etc.)
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

MAX_TOOL_CALLS  = 8        # raised from 6 — larger programs need more tool turns
MAX_CODE_LINES  = 300      # raised from 30 — handles real student programs
TIMEOUT_SECONDS = 15       # raised from 5 — longer programs need more time
GROQ_MODEL      = "llama-3.3-70b-versatile"


# -----------------------------------
# HELPER : auto-detect and install missing packages
# -----------------------------------

def _install_missing_packages(code: str) -> list[str]:
    """
    Scan code for import statements. Try to install any package that
    isn't already available. Returns list of packages installed.
    """
    # Match: import X, from X import Y, import X as Y
    pattern = re.compile(
        r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        re.MULTILINE
    )
    # Standard library modules — don't try to pip-install these
    stdlib = {
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
    }

    found = set(re.findall(pattern, code))
    to_install = [pkg for pkg in found if pkg not in stdlib]

    installed = []
    for pkg in to_install:
        try:
            __import__(pkg)           # already available
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg, "-q"],
                    capture_output=True,
                    timeout=30
                )
                installed.append(pkg)
            except Exception:
                pass                  # silently skip — run_python will report the error

    return installed


# -----------------------------------
# TOOL 1 : RUN PYTHON
# -----------------------------------

def run_python(code: str, timeout_s: int = TIMEOUT_SECONDS) -> dict:
    """
    Safely execute Python code in a subprocess sandbox.
    Auto-installs missing pip packages before running.
    Returns stdout, stderr, returncode, and any packages installed.
    """

    if not code or not code.strip():
        return {"success": False, "error": "No Python code was provided."}

    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return {
            "success": False,
            "error": (
                f"Code is {len(lines)} lines — that's very large for a single snippet. "
                f"Consider breaking it into smaller functions and submitting one section at a time."
            )
        }

    # Try to install missing packages first
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
            timeout=timeout_s
        )
        os.remove(temp_path)

        response = {
            "success":    True,
            "stdout":     result.stdout,
            "stderr":     result.stderr,
            "returncode": result.returncode,
        }
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
                f"Execution stopped after {timeout_s}s. "
                "This usually means an infinite loop or a very slow algorithm. "
                "Check your loop conditions or add a print statement to trace progress."
            )
        }

    except Exception as e:
        return {"success": False, "error": f"Execution environment error: {str(e)}"}


# -----------------------------------
# TOOL 2 : LINT CODE
# -----------------------------------

def lint_code(code: str) -> dict:
    """Run ruff linter on Python code and return structured feedback."""

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
        return {
            "success": False,
            "error": "ruff is not installed. Run: pip install ruff"
        }

    except Exception as e:
        return {"success": False, "error": f"Linter error: {str(e)}"}


# -----------------------------------
# TOOL 3 : DOC SEARCH  (80+ concepts)
# -----------------------------------

def doc_search(keyword: str) -> dict:
    """
    Search an expanded Python documentation library (80+ topics).
    Covers beginner through intermediate Python — data types, OOP,
    functional tools, file I/O, exceptions, standard library, and more.
    Uses partial and fuzzy matching.
    """

    if not keyword or not keyword.strip():
        return {"success": False, "error": "No keyword was provided."}

    python_docs = {

        # ── Core data types ──────────────────────────────────────────────
        "integer":      "int stores whole numbers. Arithmetic: +, -, *, /, // (floor div), % (modulo), ** (power). Convert with int(). Beware: 5/2 = 2.5 (float), 5//2 = 2 (int).",
        "float":        "float stores decimals. Precision warning: 0.1 + 0.2 ≠ 0.3 exactly. Use round(x, n) to limit places. Convert with float(). Use decimal module for exact decimal arithmetic.",
        "string":       "str stores text in '' or \"\". Immutable. Key methods: .strip(), .split(), .join(), .replace(), .find(), .startswith(), .endswith(), .upper(), .lower(), .format(). f-strings: f'Hello {name}'.",
        "boolean":      "bool is True or False. All values are truthy/falsy: 0, '', [], {}, None are falsy; everything else is truthy. Use 'and', 'or', 'not' for logic.",
        "none":         "None is Python's null value. A function with no return statement returns None. Check with 'if x is None:' not 'if x == None:'.",
        "list":         "list stores ordered, mutable collections. Created with []. Key methods: .append(x), .extend(lst), .insert(i,x), .remove(x), .pop(i), .sort(), .reverse(), .index(x), .count(x). Supports indexing and slicing.",
        "tuple":        "tuple stores ordered, immutable data. Created with (a, b) or just a, b. Cannot change after creation. Good for fixed data (coordinates, RGB). Unpack: x, y = (1, 2).",
        "dictionary":   "dict stores key-value pairs. Created with {} or dict(). Access: d[key] or d.get(key, default). Methods: .keys(), .values(), .items(), .update(), .pop(). Keys must be hashable (str, int, tuple).",
        "set":          "set stores unique, unordered values. Created with set() — not {}, which makes a dict. Methods: .add(), .remove(), .discard(), .union(), .intersection(), .difference(). Fast membership test: 'x in my_set'.",
        "bytes":        "bytes stores raw binary data. Created with b'hello' or bytes(n). Immutable. Use .decode() to convert to str. Use .encode() on strings to get bytes. Used in file I/O, networking.",
        "complex":      "complex stores complex numbers: 3+4j. Access parts with .real and .imag. Useful in signal processing and scientific computing.",

        # ── Variables & operators ─────────────────────────────────────────
        "variable":     "Variables store values. Python is dynamically typed — no type declaration. Names are case-sensitive. Convention: snake_case for variables, UPPER_CASE for constants. Assignment: x = 5.",
        "operator":     "Python operators: arithmetic (+,-,*,/,//,%,**), comparison (==,!=,<,>,<=,>=), logical (and,or,not), identity (is, is not), membership (in, not in), bitwise (&,|,^,~,<<,>>).",
        "comparison":   "Comparison operators return True/False: == (equal), != (not equal), < > <= >=. Chain comparisons: 0 < x < 10. Use 'is' only for None/True/False identity, not value equality.",
        "augmented":    "Augmented assignment combines operation + assignment: x += 1 means x = x + 1. Also: -=, *=, /=, //=, %=, **=, &=, |=.",
        "type":         "type(x) returns the type of x. isinstance(x, int) checks if x is an int (also works with subclasses). type(x) == int checks exact type only.",
        "casting":      "Type conversion: int('5'), float('3.14'), str(42), list('abc'), tuple([1,2]), bool(0). ValueError is raised if conversion is impossible, e.g. int('hello').",

        # ── Control flow ──────────────────────────────────────────────────
        "if":           "if-elif-else controls execution: 'if cond: ... elif other: ... else: ...'. Conditions can use any truthy/falsy value. One-liner: x = a if cond else b (ternary).",
        "for loop":     "for iterates over any iterable: lists, strings, ranges, dicts. Syntax: 'for item in sequence:'. Use range(n), range(start, stop), range(start, stop, step). Use enumerate() for index + value.",
        "while loop":   "while runs while a condition is True: 'while cond:'. Always ensure the condition can become False, or use break. Use a counter or update a variable inside the loop.",
        "loop":         "Python has 'for' loops (iterate over sequences) and 'while' loops (condition-based). break exits immediately. continue skips to the next iteration. else on a loop runs if it completed without break.",
        "break":        "break exits the nearest enclosing loop immediately. Often used inside an if to stop when a condition is met. Works in both for and while loops.",
        "continue":     "continue skips the rest of the current loop iteration and goes to the next one. Useful to skip certain values without breaking the whole loop.",
        "range":        "range(stop), range(start,stop), range(start,stop,step) generates a sequence of integers. range(5) → 0,1,2,3,4. Doesn't include stop. Combine with list() to see all values.",
        "pass":         "pass is a no-op placeholder. Used in empty function/class/if bodies that you plan to fill in later. It prevents syntax errors from empty blocks.",

        # ── Functions ─────────────────────────────────────────────────────
        "function":     "Functions are reusable blocks: 'def name(params): ... return value'. Parameters have local scope. Python passes objects by reference (but reassigning a parameter doesn't affect the caller). Default args: def f(x=10).",
        "return":       "return sends a value back from a function. No return (or bare return) → function returns None. Return multiple values as a tuple: 'return a, b'. Unpack: x, y = f().",
        "argument":     "Arguments are values passed to a function. Positional: f(1, 2). Keyword: f(x=1, y=2). *args collects extra positional args as a tuple. **kwargs collects extra keyword args as a dict.",
        "lambda":       "lambda creates small anonymous functions: lambda x: x * 2. Used inline with map(), filter(), sorted(). For anything longer than one expression, use a named def instead.",
        "scope":        "Scope determines where a variable is visible. LEGB rule: Local → Enclosing → Global → Built-in. Variables defined inside a function are local. Use 'global x' to modify a global from inside a function.",
        "closure":      "A closure is a function that remembers variables from its enclosing scope even after the outer function has returned. Useful for factory functions and decorators.",
        "decorator":    "Decorators wrap a function to add behaviour: @decorator above a def. Common decorators: @staticmethod, @classmethod, @property. Write your own with a wrapper function that accepts and returns a function.",
        "generator":    "Generators produce values lazily with 'yield'. Use when you don't need all values at once — saves memory. 'for x in gen():' iterates without building a list. Generator expression: (x*2 for x in range(10)).",
        "comprehension":"List comprehension: [expr for x in iterable if cond]. Dict: {k:v for ...}. Set: {expr for ...}. Generator: (expr for ...). More readable and often faster than a for loop with .append().",
        "recursion":    "Recursion is when a function calls itself. MUST have a base case to stop. Python's default limit is 1000 calls (RecursionError). Good for: trees, nested structures, divide-and-conquer. Example: factorial(n) = n * factorial(n-1), base: n==0.",
        "map":          "map(func, iterable) applies a function to every item. Returns a map object — wrap in list() to see results: list(map(str, [1,2,3])). Often replaced by list comprehensions.",
        "filter":       "filter(func, iterable) keeps items where func returns True. Returns a filter object — wrap in list(): list(filter(lambda x: x>0, [-1,2,-3,4])). Often replaced by [x for x in lst if cond].",
        "zip":          "zip(a, b) pairs elements from two iterables: list(zip([1,2],[3,4])) → [(1,3),(2,4)]. Stops at the shorter iterable. Unzip: a, b = zip(*pairs). Great for parallel iteration.",
        "sorted":       "sorted(iterable, key=func, reverse=False) returns a new sorted list. list.sort() sorts in place. Use key= for custom sort: sorted(words, key=len). sorted() works on any iterable.",

        # ── OOP ───────────────────────────────────────────────────────────
        "class":        "Classes are blueprints for objects: 'class Name:'. __init__(self, ...) is the constructor. Instance attributes: self.x = value. Create objects: obj = Name(args). Methods are functions with self as first param.",
        "object":       "Everything in Python is an object — integers, strings, functions, classes. Objects have attributes (data) and methods (behaviour). dir(obj) lists all attributes and methods.",
        "inheritance":  "Inheritance: 'class Child(Parent):'. Child inherits all parent methods and attributes. Override methods by redefining them. Use super() to call the parent's version: super().__init__().",
        "super":        "super() refers to the parent class. Most common use: super().__init__(args) to call the parent constructor inside a child's __init__. Avoids hard-coding the parent class name.",
        "method":       "Methods are functions defined inside a class. Instance methods take self. Class methods take cls and use @classmethod. Static methods take no special first arg and use @staticmethod.",
        "dunder":       "Dunder (double-underscore) methods like __init__, __str__, __repr__, __len__, __eq__, __add__ let you define how operators and built-in functions work on your class. Also called magic methods.",
        "property":     "@property turns a method into a read-only attribute. Add @name.setter to make it writable. This lets you add validation without changing the public interface.",
        "abstract":     "Abstract classes (from abc module) define methods that subclasses must implement: from abc import ABC, abstractmethod. Prevents instantiating the base class directly.",
        "dataclass":    "@dataclass (from dataclasses module) auto-generates __init__, __repr__, __eq__ from field annotations. Cleaner than writing them manually. Python 3.7+.",
        "polymorphism": "Polymorphism means different classes can respond to the same method call. Python uses duck typing — if an object has the right method, it works, regardless of class.",
        "encapsulation":"Encapsulation hides internal state. Convention: _name for protected, __name for private (name-mangled). Python doesn't enforce access control but respects the convention.",

        # ── Exception handling ────────────────────────────────────────────
        "exception":    "Exceptions are runtime errors. Common ones: ValueError, TypeError, KeyError, IndexError, AttributeError, NameError, ZeroDivisionError, FileNotFoundError, ImportError, StopIteration.",
        "try":          "try-except catches exceptions: 'try: ... except ErrorType as e: ...'. Use 'else:' for code that runs if no exception. Use 'finally:' for cleanup that always runs (e.g. closing files).",
        "raise":        "raise throws an exception: 'raise ValueError(\"message\")'. Re-raise the current exception with bare 'raise'. Create custom exceptions by subclassing Exception.",
        "assert":       "assert condition, 'message' raises AssertionError if condition is False. Used for debugging and unit tests. Disabled when Python runs with -O flag.",

        # ── File I/O ──────────────────────────────────────────────────────
        "file":         "Open files with open(path, mode). Modes: 'r' (read), 'w' (write/overwrite), 'a' (append), 'rb'/'wb' (binary). Always use 'with open(...) as f:' — it auto-closes the file.",
        "read":         "Read file contents: f.read() (whole file as string), f.readline() (one line), f.readlines() (list of lines). For large files, iterate: 'for line in f:'.",
        "write":        "Write to a file: f.write(string) or f.writelines(list). 'w' mode overwrites the file. 'a' mode appends. write() doesn't add newlines — add \\n manually.",
        "csv":          "csv module reads/writes CSV files. csv.reader(f) gives rows as lists. csv.DictReader(f) gives rows as dicts (header as keys). csv.writer(f).writerow(row) writes a row.",
        "json":         "json module: json.loads(str) → Python object. json.dumps(obj) → JSON string. json.load(f) reads from file. json.dump(obj, f) writes to file. Use indent= for pretty printing.",
        "os path":      "os.path functions: .exists(p), .isfile(p), .isdir(p), .join(dir, file), .basename(p), .dirname(p), .splitext(p). Also: os.listdir(dir), os.makedirs(dir, exist_ok=True).",

        # ── Standard library highlights ───────────────────────────────────
        "import":       "import loads modules: 'import math', 'from math import sqrt', 'import numpy as np'. Standard library needs no install. Third-party needs pip install first. __name__ == '__main__' guards script execution.",
        "math":         "math module: math.sqrt(x), math.floor(x), math.ceil(x), math.pow(x,y), math.log(x), math.pi, math.e, math.factorial(n), math.gcd(a,b). For complex math use cmath.",
        "random":       "random module: random.random() (0.0–1.0), random.randint(a,b) (inclusive), random.choice(seq), random.shuffle(lst) (in-place), random.sample(seq, k). Seed with random.seed(n) for reproducibility.",
        "datetime":     "datetime module: datetime.now() for current time. date.today() for today's date. timedelta for durations. strftime() to format dates as strings. strptime() to parse strings to dates.",
        "collections":  "collections module: Counter(iterable) counts elements. defaultdict(type) auto-creates missing keys. OrderedDict preserves insertion order (less needed in Python 3.7+). deque for fast append/pop from both ends.",
        "itertools":    "itertools module: chain() concatenates iterables, product() gives cartesian product, combinations(), permutations(), groupby(), islice(). All return iterators — wrap in list() to see.",
        "functools":    "functools module: functools.reduce(func, iterable) applies func cumulatively. lru_cache() memoises a function. partial() fixes some args of a function. wraps() preserves function metadata in decorators.",
        "re":           "re module for regular expressions. re.match() matches at start. re.search() finds anywhere. re.findall() returns all matches. re.sub() replaces. re.compile() pre-compiles a pattern for reuse.",
        "sys":          "sys module: sys.argv (command-line args list), sys.exit(code) (exit the program), sys.path (module search paths), sys.stdin/stdout/stderr (standard streams), sys.version.",
        "os":           "os module: os.getcwd(), os.chdir(path), os.listdir(path), os.makedirs(path), os.remove(file), os.rename(src, dst), os.environ (env vars dict), os.path for path operations.",
        "string module":"string module: string.ascii_letters, string.digits, string.punctuation, string.whitespace. string.Template for simple substitution. Useful for generating test data.",
        "typing":       "typing module provides type hints: List[int], Dict[str, int], Optional[str] (= str | None), Union[int, str], Tuple[int, ...], Callable. Type hints are not enforced at runtime — use mypy to check.",

        # ── Memory & performance ──────────────────────────────────────────
        "mutable":      "Mutable objects can be changed after creation: list, dict, set, bytearray. Immutable objects cannot: int, float, str, tuple, frozenset. Gotcha: using a mutable default argument like def f(x=[]) shares the same list across calls.",
        "reference":    "Python variables are references (pointers) to objects, not the objects themselves. 'a = b' makes both point to the same object. For lists/dicts, use copy() or [:] for a shallow copy, or copy.deepcopy() for a full copy.",
        "shallow copy": "A shallow copy (list[:], list.copy(), copy.copy()) creates a new container but the elements still point to the same objects. For nested lists/dicts, changes to inner objects affect both copies.",
        "deep copy":    "copy.deepcopy(obj) creates a fully independent copy — all nested objects are also copied. Slower than shallow copy. Use when you need to modify nested structures without affecting the original.",
        "memory":       "Python uses reference counting + garbage collection (gc module). Large data: use generators instead of lists, numpy arrays instead of lists of numbers. Measure with sys.getsizeof() or tracemalloc.",
        "complexity":   "Time complexity of common operations: list append O(1), insert O(n), search O(n). dict/set lookup O(1). Sorting O(n log n). Nested loops O(n²). Use sets/dicts for fast lookups instead of linear search.",

        # ── Intermediate topics ───────────────────────────────────────────
        "enumerate":    "enumerate(iterable, start=0) yields (index, value) pairs. Use in for loops when you need both: 'for i, val in enumerate(my_list):'. Cleaner than range(len(lst)) + lst[i].",
        "unpacking":    "Unpacking assigns iterables to variables: a, b = [1, 2]. Extended: first, *rest = [1,2,3,4]. Swap: a, b = b, a. Pass list as args: func(*lst). Pass dict as kwargs: func(**d).",
        "slice":        "Slicing: lst[start:stop:step]. Defaults: start=0, stop=len, step=1. Negative indices count from end: lst[-1] is last. Reverse: lst[::-1]. Slices create new objects (shallow copy).",
        "context manager": "Context managers (with statement) handle setup/teardown: 'with open(f) as h:'. Create your own with __enter__/__exit__ methods or the @contextmanager decorator from contextlib.",
        "walrus":       "Walrus operator := (Python 3.8+) assigns and returns a value in one expression: 'if (n := len(lst)) > 10: print(n)'. Useful in while loops: 'while chunk := f.read(1024):'.",
        "f-string":     "f-strings (Python 3.6+) embed expressions: f'Hello {name!r}'. Format numbers: f'{pi:.2f}'. Pad: f'{x:>10}'. Expressions inside {}: f'{2+2}'. Faster and more readable than .format() or %.",
        "global":       "The 'global' keyword lets a function read/write a module-level variable: 'global count; count += 1'. Without it, assigning inside a function creates a new local variable instead.",
        "nonlocal":     "nonlocal lets a nested function modify a variable from its enclosing function: 'nonlocal x'. Without it, assigning x in the inner function creates a new local x.",
        "match":        "match-case (Python 3.10+) is structural pattern matching: 'match value: case 1: ... case str(): ... case _:'. More powerful than if-elif chains for matching data shapes.",
        "async":        "async def defines a coroutine. await suspends it until a result is ready. Run with asyncio.run(main()). Use for I/O-bound concurrency (network, file) — not CPU-bound work (use multiprocessing for that).",
        "thread":       "threading module runs code in parallel threads. Good for I/O-bound tasks. Beware the GIL — true parallel CPU execution needs multiprocessing. Use threading.Lock() to prevent race conditions.",
        "process":      "multiprocessing module runs code in separate processes, bypassing the GIL for CPU-bound tasks. Pool.map() parallelises a function over a list. Use Queue or Pipe for inter-process communication.",
    }

    kw = keyword.lower().strip()

    # 1. Direct substring match (both directions)
    matches = [
        {"topic": t, "explanation": e}
        for t, e in python_docs.items()
        if kw in t or t in kw
    ]

    # 2. Any word in topic appears in keyword
    if not matches:
        matches = [
            {"topic": t, "explanation": e}
            for t, e in python_docs.items()
            if any(word in kw for word in t.split() if len(word) > 2)
        ]

    # 3. Keyword appears inside explanation text
    if not matches:
        matches = [
            {"topic": t, "explanation": e}
            for t, e in python_docs.items()
            if kw in e.lower()
        ]

    if not matches:
        topics = ", ".join(sorted(python_docs.keys()))
        return {
            "success": True,
            "results": [],
            "message": (
                f"No documentation found for '{keyword}'. "
                f"Available topics: {topics}"
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

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute Python code in a subprocess sandbox. "
                "Automatically installs missing pip packages. "
                f"Max {MAX_CODE_LINES} lines, {TIMEOUT_SECONDS}s timeout. "
                "Returns stdout, stderr, returncode, and any packages installed. "
                "ALWAYS call this first when the student submits code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The complete Python code to execute."
                    },
                    "timeout_s": {
                        "type": "integer",
                        "description": "Max execution time in seconds.",
                        "default": TIMEOUT_SECONDS,
                        "minimum": 1,
                        "maximum": TIMEOUT_SECONDS
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
                "Run ruff linter on Python code to find style issues, "
                "undefined names, unused variables, and code quality problems. "
                "Use when code runs correctly but may have quality issues."
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
                "Search 80+ Python documentation topics. Covers data types, "
                "OOP, exceptions, file I/O, standard library, functional tools, "
                "and intermediate topics. Use when the student is confused about "
                "a Python concept, keyword, or standard library module."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": (
                            "Python concept to look up. Examples: 'list', "
                            "'decorator', 'generator', 'async', 'dataclass', "
                            "'recursion', 'closure', 'comprehension'."
                        )
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
    """Run a tool and return a JSON string result."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({
            "success": False,
            "error": (
                f"Unknown tool '{tool_name}'. "
                f"Available: {list(TOOL_FUNCTIONS.keys())}"
            )
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

SYSTEM_PROMPT = """You are Mini-Tutor, a patient and encouraging AI coding tutor for Python learners.
Your goal is to help students UNDERSTAND and fix their own bugs — never to write the fix for them.

RULES:
1. When a student submits code, ALWAYS call run_python first to see actual runtime behaviour.
2. NEVER reveal the corrected code. Use a Socratic question to guide the student to the fix.
3. Structure every reply EXACTLY like this:

   **Diagnosis:** (one sentence — what is wrong and on which line, or what the output indicates)
   **Question:** (one guiding question that nudges the student toward the fix — not the answer itself)
   **Next Step:** (one small, concrete action the student can try right now)

4. If the code runs but the student says output is wrong, ask what they expected vs what they got.
5. If the student asks you to "just give the answer" or mentions graded work, redirect with a question.
6. Use doc_search if the student seems confused about a Python concept or module.
7. Use lint_code if the code runs correctly but has style/quality issues.
8. If packages were auto-installed, mention it briefly so the student knows.
9. Tone: warm, clear, patient. Never condescending. You are an AI tutor — be transparent about that.
10. Maximum 8 tool calls per turn."""


# -----------------------------------
# AGENT LOOP  (ReAct — OpenAI/Groq format)
# -----------------------------------

def run_tutor_agent(
    student_message: str,
    conversation_history: list = None
) -> tuple:
    """
    Run the Mini-Tutor ReAct loop using the Groq API.

    Args:
        student_message:       Latest message or code from the student.
        conversation_history:  Prior message dicts (role/content). Pass [] for fresh chat.

    Returns:
        (final_reply: str, updated_history: list)
    """

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
    final_reply = ""

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

        # ── Convert SDK object → plain dict (CRITICAL) ──────────────────
        # Groq API only accepts plain dicts in the messages list.
        # Appending the raw ChatCompletionMessage SDK object causes 400 errors.
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

        # ── Done ─────────────────────────────────────────────────────────
        if finish in ("stop", "length"):
            final_reply = message.content or ""
            break

        # ── Tool calls ───────────────────────────────────────────────────
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
            final_reply = (
                "I ran into an unexpected state. "
                "Please try submitting your code again."
            )
            break

    # Strip system prompt before returning — all entries are plain dicts
    updated_history = messages[1:]
    return final_reply, updated_history


# -----------------------------------
# CLI ENTRY POINT
# -----------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("  MINI-TUTOR  —  Generalised  —  CLI Mode")
    print("  Type 'quit' to exit.")
    print("=" * 55)

    history = []

    while True:
        print("\nPaste your Python code or question.")
        print("Press ENTER twice to submit.\n")

        lines       = []
        blank_count = 0

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