# %% Text mining functions

## Dependencies
import pandas as pd
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import spacy
import itertools
from nltk.stem import PorterStemmer


nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")


def chat_word_converter(text):
    for chat_word, formal_word in chat_to_formal.items():
        text = re.sub(r"\b" + re.escape(chat_word) + r"\b", formal_word, text)
    return text


if __name__ == "__main__":
    chat_to_formal = {
        "u": "you",
        "r": "are",
        "lol": "laughing out loud",
        "brb": "be right back",
        "ttyl": "talk to you later",
        "thx": "thanks",
        "gtg": "got to go",
        "b4": "before",
    }

    data = {
        "text_lower_case": [
            "hey john! r u coming to the function this evening? lol, thx for your invite!",
            "gtg now, ttyl!",
            "no chat words here",
        ]
    }
    combined_df = pd.DataFrame(data)

    # Convert chat words
    combined_df["text_lower_case_converted"] = combined_df["text_lower_case"].apply(
        chat_word_converter
    )

    print(combined_df)


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
    """Treats: punctuations, lemmatize, stopwords"""
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


def extract_noun_chunks(text):
    doc = nlp(text)
    return [chunk.text for chunk in doc.noun_chunks]


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")

    data = {
        "text": [
            "Autonomous cars shift insurance liability toward manufacturers",
            "The new policy will affect all vehicle owners",
            "Machine learning models are increasingly being used in finance",
        ]
    }
    df = pd.DataFrame(data)

    df["noun_chunks"] = df["text"].apply(extract_noun_chunks)

    df


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


def remove_emojis(string):
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )

    return emoji_pattern.sub(r"", string)


def lemmatize_text(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc]


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")

    text_data = pd.DataFrame(
        {
            "text": [
                "He is very methodical and orderly in his execution",
                "he is driving and drives the down of the drived vehicle",
            ]
        }
    )

    text_data["lemmatized"] = text_data["text"].apply(lemmatize_text)

    print(text_data)


def remove_frequent_words(df, text_column, threshold=10):
    """
    Removes frequent words from a given text column in a DataFrame.

    Args:
    - df (DataFrame): Input DataFrame.
    - text_column (str): Name of the text column.
    - threshold (int): Number of most common words to remove. Defaults to 10.

    Returns:
    - DataFrame: Input DataFrame with an additional column 'frequent_removed'.
    """

    # Combine all text into a single string and split into individual words.
    all_words = " ".join(df[text_column]).split()

    # Count the frequency of every word.
    word_counts = Counter(all_words)

    # Determine the threshold for frequent words.
    most_common_words = word_counts.most_common(threshold)

    # Set of the frequent words.
    frequent_words = {word for word, count in most_common_words}

    # Remove frequent words from the text column.
    df["frequent_removed"] = df[text_column].apply(
        lambda x: " ".join([word for word in x.split() if word not in frequent_words])
    )

    return df


if __name__ == "__main__":
    data = {
        "text_lower_case": [
            "this is a sample text",
            "this text is another sample",
            "sample text is the best",
        ]
    }
    combined_df = pd.DataFrame(data)

    # Remove frequent words
    combined_df = remove_frequent_words(combined_df, "text_lower_case", threshold=3)

    print(combined_df)


def remove_html_tags(df, text_column):
    """
    Removes HTML tags from a given text column in a DataFrame.

    Args:
    - df (DataFrame): Input DataFrame.
    - text_column (str): Name of the text column.

    Returns:
    - DataFrame: Input DataFrame with HTML tags removed from the text column.
    """

    # Define the HTML tag pattern
    html_tag_pattern = re.compile(r"<[^>]+>")

    # Apply the HTML tag removal function to the text column
    df[text_column] = df[text_column].apply(lambda x: html_tag_pattern.sub("", x))

    return df


if __name__ == "__main__":
    data = {
        "text_lower_case": [
            "<p>hi john! <a href='https://example_url.com'>click here</a> to visit.</p>",
            "<b>bold text</b> and <i>italic text</i>",
            "no html tags here",
        ]
    }
    combined_df = pd.DataFrame(data)

    # Remove HTML tags
    combined_df = remove_html_tags(combined_df, "text_lower_case")

    print(combined_df)


def text_to_lowercase():
    pass


def remove_punctuations():
    pass


def remove_rare_words(df, text_column, threshold=5):
    """
    Removes rare words from a given text column in a DataFrame.

    Args:
    - df (DataFrame): Input DataFrame.
    - text_column (str): Name of the text column.
    - threshold (int): Frequency threshold for rare words. Defaults to 5.

    Returns:
    - DataFrame: Input DataFrame with an additional column 'rare_removed'.
    """

    # Combine all text into a single string and split into individual words.
    all_words = " ".join(df[text_column]).split()

    # Count the frequency of every word.
    word_counts = Counter(all_words)

    # Define the set of rare words.
    rare_words = {word for word, count in word_counts.items() if count < threshold}

    # Remove rare words from the text column.
    df["rare_removed"] = df[text_column].apply(
        lambda x: " ".join([word for word in x.split() if word not in rare_words])
    )

    return df


if __name__ == "__main__":
    # Create a sample DataFrame
    data = {
        "text_lower_case": [
            "this is a sample text",
            "this text is another sample",
            "sample text is the best",
            "xyz",
            "abc once",
            "def twice",
        ]
    }
    combined_df = pd.DataFrame(data)

    # Remove rare words
    combined_df = remove_rare_words(combined_df, "text_lower_case", threshold=2)

    print(combined_df)


def remove_stopwords():
    pass


def remove_urls(df, text_column):
    """
    Removes URLs from a given text column in a DataFrame.

    Args:
    - df (DataFrame): Input DataFrame.
    - text_column (str): Name of the text column.

    Returns:
    - DataFrame: Input DataFrame with URLs removed from the text column.
    """

    # Define the URL pattern
    url_pattern = re.compile(r"http[s]?://\S+|www\.\S+")

    # Apply the URL removal function to the text column
    df[text_column] = df[text_column].apply(lambda x: url_pattern.sub("", x))

    return df


if __name__ == "__main__":
    data = {
        "text_lower_case": [
            "check out this link: https://www.example.com and also visit http://example.org.",
            "visit our website at www.example.net for more info.",
            "no urls here",
        ]
    }
    combined_df = pd.DataFrame(data)

    # Remove URLs
    combined_df = remove_urls(combined_df, "text_lower_case")

    print(combined_df)


def pos_tags_df(df, col):
    """Process the text and get POS tags"""
    nlp = spacy.load("en_core_web_sm")
    df[f"{col}_pos_tags"] = df[col].apply(
        lambda x: [(token.text, token.pos_) for token in nlp(str(x))]
    )

    return df


if __name__ == "__main__":
    df = pd.DataFrame({"text": ["This is a sample text.", "Another sample text."]})

    df = pos_tags_df(df, "text")

    print(df)


def stem_text(text):
    """
    Stems a text string using SpaCy for tokenization and NLTK for stemming.
    """
    doc = nlp(text)
    stemmed_tokens = [porter.stem(token.text) for token in doc]
    return " ".join(stemmed_tokens)


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    porter = PorterStemmer()
    data = {
        "text": [
            "SpaCy is a great tool.",
            "I am running fast.",
            "Cats are cute animals.",
        ]
    }
    df = pd.DataFrame(data)
    # Apply the stemming function to the 'text' column
    df["stemmed_text"] = df["text"].apply(stem_text)

    print(df)
