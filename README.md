# wordle_player

A Class that plays wordle optimally

if you want to play wordle optimally, first you need to setup the database.

Run:

```python
from database import Database

db = Database("<path to database>")
db.insert_words_file("<words.txt file path>")
```

Then you can play wordle optimally by running the following commands:

```python

from wordle_player import WordlePlayer

player = WordlePlayer('<path to database>')

player.get_top_words(10) # get the top 10 most likely words

"""
After you get a response from wordle, add rejected chars as:
"""

player.add_negatives(['a', 'b', 'c'])
player.add_negative('a1') # a1 was yello colored in wordle

"""
Add yellow chars as:
"""

player.add_positives(['d', 'e', 'f'])

"""
Add green chars as:
"""

player.add_positives(['g0', 'h2', 'i4']) # 0 indexed
```
