prompt = """Use the speech-to-text transcript to output a new file of python code with the changes requested. Do NOT add to the code what is not in the transcript, and no comments.  Format the code correctly with correct indentation. Variable names may be incorrectly transcribed. Don't change anything if the transcript is not related to code. If the transcript is an unfinished thought, you respond with User Not Finished

input: Current File:

Transcript:
import math define foo parenthesis bar close parenthesis return math dot pi times bar
output: ```python
import math
def foo(bar):
return math.PI * bar```

input: Current File:
``python
import math
def foo(bar):
return math.PI * bar```
```
Transcript:
define 

output: User Not Finished

input: Current File:

Transcript:
import
output: User Not Finished

input: Current File:
```{Current}
```
Transcript:
{Transcript}
output:
"""