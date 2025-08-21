# %% Text mining functions

## Dependencies
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import spacy
import pandas as pd
import itertools

nltk.download("wordnet")
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

nlp = spacy.load("en_core_web_sm")


def clean_series(x):
    """Return lemmatrized words with count"""
    # Convert to string and lower case
    corp = str(x).lower()

    # Remove non-alphanumeric characters and strip
    corp = re.sub("[^a-z0-9]+", " ", corp).strip()

    # Tokenize
    tokens = word_tokenize(corp)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    words = [t for t in tokens if t not in stop_words]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    lemmatize = [lemmatizer.lemmatize(w) for w in words]

    # Word frequency count
    freq = FreqDist(w for w in lemmatize)

    return freq


if __name__ == "__main__":
    series = pd.Series(["This is a sample text.", "Another sample text."])
    result = series.apply(clean_series)
    print(result)


def clean_text_df(df, col):
    # Create a copy of the original dataframe to avoid modifying it directly
    df = df.copy()

    # Calculate original text length
    df[f"{col}_len"] = df[col].apply(len)

    # Convert to lower case and remove punctuation
    df[col] = df[col].apply(
        lambda x: re.sub(f"[{string.punctuation}]", "", str(x).lower())
    )

    # Tokenize and lemmatize
    wordnet = WordNetLemmatizer()
    df[col] = df[col].apply(
        lambda x: " ".join([wordnet.lemmatize(word) for word in x.split()])
    )

    # Calculate post-lemmatization text length
    df[f"{col}_len_post"] = df[col].apply(lambda x: len(x))

    # Remove stopwords
    stop = set(stopwords.words("english"))  # Use a set for faster lookups
    df[f"{col}_c"] = df[col].apply(
        lambda x: " ".join([word for word in x.split() if word not in stop])
    )

    return df


if __name__ == "__main__":
    # Create a sample dataframe
    df = pd.DataFrame({"text": ["This is a sample text.", "Another sample text."]})

    # Clean the text
    df = clean_text_df(df, "text")

    print(df)


def generate_anagrams(word):
    """
    Generates all possible anagrams for a given word.

    Parameters:
        word (str): The input word to generate anagrams from.

    Returns:
        list: A list of unique anagrams.
    """
    # Use itertools.permutations to create all possible letter arrangements
    permutations = itertools.permutations(word)

    # Join the tuples into strings and remove duplicates by converting to a set
    unique_anagrams = set("".join(p) for p in permutations)

    # Return the sorted list of unique anagrams
    return sorted(unique_anagrams)


## pos_tags_df
def pos_tags_df(df, col):
    # Process the text and get POS tags
    df[f"{col}_pos_tags"] = df[col].apply(
        lambda x: [(token.text, token.pos_) for token in nlp(str(x))]
    )

    return df


if __name__ == "__main__":
    df = pd.DataFrame({"text": ["This is a sample text.", "Another sample text."]})

    df = pos_tags_df(df, "text")

    print(df)
