classify_prompt = """Multi-choice problem: Define the category of the transcript?
Categories:
- Unfinished Thought
- Not related to code
- Finished and Code related

Please only print the category name without anything else.

Ticket: please
Category: Unfinished Thought

Ticket: import
Category: Unfinished Thought

Ticket: for i in range ten
Category: s

Ticket: wait what
Category: Not related to code

Ticket: can you change line 4 to import
Category: Unfinished Thought

Ticket: {Transcript}
Category:
"""
prompt = """Use the speech-to-text transcript to output a new file of python code with the changes or continuation of the code requested. Do NOT add to the code what is not in the transcript, and no comments.  Format the code correctly with correct indentation. Variable names may be incorrectly transcribed. 

input: Current File:

Transcript:
import math define foo parenthesis bar close parenthesis return math dot pi times bar
output: ```python
import math
def foo(bar):
return math.PI * bar```

input: Current File: 
 ```python
def foo(bar):
```

Transcript:
for I in range ten
output: ```python
def foo(bar):
for i in range(10):
```
input: Current File: 
 ```python
def foo(bar):
for i in range(10):
```

Transcript:
print I times bar
output: ```python
def foo(bar):
for i in range(10):
print(i * bar)

input: Current File:
```{Current}
```
Transcript:
{Transcript}
output:
"""