import pandas as pd
from database import Database, get_feature_column_names


class WordlePlayer:
    def __init__(self, database_path="words.db"):
        self.db = Database(database_path)
        self.condition = ""

    def close(self):
        self.db.close()

    def get_char_count_query(self):
        columns = get_feature_column_names()
        summed_columns = [f"SUM({c}) AS {c}" for c in columns]
        query = f"SELECT {', '.join(summed_columns)} FROM words"
        query = query + self.condition
        return query

    def add_condition(self, condition):
        if self.condition != "":
            self.condition = f"{self.condition} AND {condition}"
        else:
            self.condition = f" WHERE {condition}"

    def parse_char(self, char):
        if len(char) == 2:
            char = char[0] + str(int(char[1]) - 1)
        char = char.lower()
        return char

    def add_positive(self, char):
        char = self.parse_char(char)
        condition = f"{char} = 1"
        self.add_condition(condition)

    def add_negative(self, char):
        char = self.parse_char(char)
        condition = f"{char} = 0"
        self.add_condition(condition)

    def add_negatives(self, chars):
        for char in chars:
            self.add_negative(char)

    def add_positives(self, chars):
        for char in chars:
            self.add_positive(char)

    def get_weighted_words(self):
        words_table = self.db.select("SELECT * FROM words" + self.condition)
        words_table = words_table.set_index("word").drop(columns=["id"])
        words = words_table.index.values
        columns = words_table.columns.values
        words_matrix = words_table.values * self.get_char_counts().values
        return pd.DataFrame(words_matrix, index=words, columns=columns)

    def get_char_counts(self):
        query = self.get_char_count_query()
        return self.db.select(query)

    def get_top_words(self, n=10):
        weighted = self.get_weighted_words()
        return weighted.sum(axis=1).sort_values(ascending=False).head(n)
