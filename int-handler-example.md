# Implementing more complex constant handlers

```python
# Driver code

from ast import parse, Constant, Name, Attribute, Compare, BoolOp, BinOp, Call

from xpytex import expressions, constants, names, attributes, comparisons, bool_operations, binary_operations, function_calls

from xpytex.utils import displaymath



expressions.register_handler(Constant, constants)

expressions.register_handler(Name, names)

expressions.register_handler(Attribute, attributes)

expressions.register_handler(Compare, comparisons)

expressions.register_handler(BoolOp, bool_operations)

expressions.register_handler(BinOp, binary_operations)

expressions.register_handler(Call, function_calls)



code = '278_956'

AST = parse(code) # This generates a Module AST

AST = AST.body # Gets the lines of the Module

AST = AST[0] # Gets the first line

AST = AST.value # Gets the contents of the line
```

Output:
## Int handler
So, we've created the following `int` handler:

```python
# A simple int handler

def int_to_latex(x: int) -> str: return str(x)

constants.register_handler(int, int_to_latex)



displaymath( expressions.latexify(AST) )
```

Output:

$$
\displaystyle 278956
$$
What if we wanted to display numbers greater than $10,000$ with scientific notation?





We have a few options to achieve that...

```python
# Suppose we have a function that converts a number to scientific notation in LaTeX



def scientific_notation(x: int) -> str:

    return rf"{float(str(x)[0] + '.' + str(x)[1:])} \times 10^{{{len(str(x)) - 1}}}"



displaymath( scientific_notation(1) )

displaymath( scientific_notation(2300) )

displaymath( scientific_notation(123_456) )
```

Output:

$$
\displaystyle 1.0 \times 10^{0}
$$

$$
\displaystyle 2.3 \times 10^{3}
$$

$$
\displaystyle 1.23456 \times 10^{5}
$$

```python
# The first option we have is to modify the handler function directly.



def int_to_latex(x: int) -> str: 

    if x < 10_000:

        return str(x)

    else:

        return scientific_notation(x)

    

constants.register_handler(int, int_to_latex)



displaymath( expressions.latexify(AST) )
```

Output:

$$
\displaystyle 2.78956 \times 10^{5}
$$
But this could be inconvenient for adding complex behaviour, specially if more rules are involved.

Then, because the handler has to be a callable (not necessarily a function), then we could create a callable object, or register a static method from a handler class.
For example, take this `int_handler` object:

```python
from typing import List, Callable



class int_handler:

    default: Callable[[int], str]

    rules: List[Callable[[int], str]] = []



    @staticmethod

    def default(x: int) -> str: return str(x)

    

    @classmethod

    def add_rule(cls, rule):

        cls.rules.append(rule)

    

    @classmethod

    def get_rule(cls, x: int) -> Callable[[int], str]:

        if len(cls.rules) == 0: return cls.default(x)



        ys = [f(x) for f in cls.rules]

        matches = map(lambda x: x != '', ys)

        matches = list(matches)



        if not any(matches):

            # print("int_handler didn't match any rules, backing to default formatting.")

            return cls.default(x)

        elif matches.count(True) > 1:

            raise LookupError("Multiple rules match.")

        else:

            return ys[matches.index(True)]



    @classmethod

    def apply(cls, x: int) -> str:

        return cls.get_rule(x)
```

Output:
In this example, this handler is a bit more complex. It has a 'rules' registry. A 'rule' is just another function. If a rule matches, then it returns some relevant output. If not, it just returns an empty string. The handler then evaluates this rules one by one per input. If multiple rules match, it throws an error. If no rules match, it uses some default formatting. If a single rule matches, it returns that output.
Let's register it and try it.

```python
constants.register_handler(int, int_handler.apply)



displaymath( expressions.latexify(AST) )
```

Output:

$$
\displaystyle 278956
$$
Wait, we forgot to add the rules!

```python
def scientific_notation_rule(x: int):

    return '' if x < 10_000 else scientific_notation(x)



int_handler.add_rule(scientific_notation_rule)



displaymath( expressions.latexify(AST) )
```

Output:

$$
\displaystyle 2.78956 \times 10^{5}
$$
And with some other numbers...

```python
code = '9_999'

AST = parse(code) # This generates a Module AST

AST = AST.body # Gets the lines of the Module

AST = AST[0] # Gets the first line

AST = AST.value # Gets the contents of the line



displaymath( expressions.latexify(AST) )
```

Output:

$$
\displaystyle 9999
$$
Let's add more rules! For example, say we want to display a Googol. A "Googol" is a '1' followed by a hundred zeroes.

We can generate such number as a string by:



```python

'1'+''.join(['0']*100)

```



A rule for that number could look something like this:

```python
def googol_rule(x: int) -> str: return '' if x != int('1'+''.join(['0']*100)) else r'\text{Googol}'

int_handler.add_rule(googol_rule)
```

Output:
Let's try it!



```python

googol = '1'+''.join(['0']*100)



code = googol

AST = parse(code) # This generates a Module AST

AST = AST.body # Gets the lines of the Module

AST = AST[0] # Gets the first line

AST = AST.value # Gets the contents of the line



displaymath( expressions.latexify(AST) ) # -> LookupError: Multiple rules match.

```



Oh no! Multiple rules match. Remember that our handler doesn't have resolution strategies for collision in the rules, and in this case the `scientific_notation` rule is colliding with `googol_rule`.
## What can we do about it?



Well, there's a lot of possible answers. We could implement the handler in some better way. Note that this handler only provides ways for adding rules and not removing them, so to resolve our conflict we have to restart the program.



Maybe some better design decisions on the handler can make this work. That also includes maybe implementing resolution strategies for rule collisioning.



The point of this example is to show the capabilities of segregating the responsability of the handlers as much as possible.



Because the handlers just need to be _callable_ we _can_ in fact implement this in much better ways, without needing to modify the rest of the source code.
