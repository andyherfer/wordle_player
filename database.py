import pandas as pd
import sqlite3
import string
from sqlite3 import OperationalError


def unsafe_in_db(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except Exception as e:
            self.close()
            print(f"Failed to execute function: {func.__name__}")
            raise (e)
        return result

    return wrapper


def unsafe(database):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                database.close()
                print("Successfully closed database.")
                raise (e)
            return result

        return wrapper

    return decorator


def get_feature_column_names():
    letters = list(string.ascii_lowercase)
    numbers = range(0, 5)
    columns = letters + [f"{i}{j}" for i in letters for j in numbers]
    return columns


def get_feature_column_names_with_query():
    columns = get_feature_column_names()
    columns = [f"{c} INTEGER NOT NULL" for c in columns]
    return columns


class Database:
    def __init__(self, database_path):
        self.database_path = database_path
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.create_table()
        self.word_count = self.get_max_id()
        self.word_count = 0 if self.word_count is None else self.word_count + 1
        self.feature_columns = get_feature_column_names()

    def commit(self):
        try:
            self.conn.commit()
            return True
        except Exception as e:
            print("Could not commit to database:", e.with_traceback())
            return False

    def close(self):
        self.conn.close()

    @unsafe_in_db
    def select(self, query):
        return pd.read_sql(query, self.conn)

    @unsafe_in_db
    def modify(self, *args, inplace=True):
        self.conn.execute(*args)
        if inplace:
            self.commit()

    def get_max_id(self):
        try:
            self.cur.execute("SELECT MAX(id) FROM words")
            return self.cur.fetchall()[0][0]
        except OperationalError:
            return 0

    def insert_word(self, word, inplace=True):
        word_encoding = self.encode_word(word)
        columns = f"id, word, {', '.join(word_encoding.keys())}"
        values_place_holders = ["?" for _ in range(len(word_encoding) + 2)]
        values_place_holders = ", ".join(values_place_holders)
        values = tuple([self.word_count, word] + list(word_encoding.values()))
        self.modify(
            f"INSERT INTO words ({columns}) VALUES ({values_place_holders})",
            values,
            inplace=inplace,
        )
        self.word_count += 1

    def create_table(self):
        feature_columns = get_feature_column_names_with_query()
        create_query = f"""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            word char(5) NOT NULL UNIQUE,
            {', '.join(feature_columns)}
            );
        """
        self.modify(create_query)

    def insert_words_file(self, file="words.txt"):
        with open(file, "r") as f:
            words = f.read().split("\n")

        for word in words:
            if len(word) <= 5:
                self.insert_word(word)

    def encode_word(self, word):
        all_features = self.feature_columns.copy()

        positive_features = {}
        for i, char in enumerate(word):
            positive_features[char] = 1
            char_i = f"{char}{i}"
            positive_features[char_i] = 1
            if char in all_features:
                all_features.remove(char)
            all_features.remove(char_i)

        negative_features = {feature: 0 for feature in all_features}
        all_features = positive_features.copy()
        all_features.update(negative_features)

        return all_features
