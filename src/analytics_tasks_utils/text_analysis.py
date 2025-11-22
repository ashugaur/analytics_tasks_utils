## Text mining functions
import re
import pandas as pd
from collections import Counter
import spacy
import itertools
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet, cmudict
import textwrap
import nltk
from collections import defaultdict
from analytics_tasks_utils.exporting import dataframe_to_excel
# import coreferee


"""
import nltk
nltk.download("punkt")
nltk.download("wordnet")
nltk.download('cmudict')
nltk.download('averaged_perceptron_tagger')
nlp.add_pipe('coreferee')
"""


def anagrams(word):
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


def antonym(word):
    antonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name().lower())
    return ", ".join(antonyms)


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


def chunking_noun(df):
    nlp = spacy.load("en_core_web_sm")
    docs = nlp.pipe(df["text"])
    df["noun_chunks"] = [[chunk.text for chunk in doc.noun_chunks] for doc in docs]
    return df


if __name__ == "__main__":
    data = {
        "text": [
            "Autonomous cars shift insurance liability toward manufacturers",
            "The new policy will affect all vehicle owners",
            "Machine learning models are increasingly being used in finance",
        ]
    }
    df = pd.DataFrame(data)

    df = chunking_noun(df)

    print(df)


def combine_and_split_text(df, width):
    combined_text = " ".join(df["text"].astype(str).tolist())
    wrapped_lines = textwrap.wrap(combined_text, width=width)
    new_df = pd.DataFrame({"text": wrapped_lines})
    return new_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "text": [
                "Lorem ipsum dolor sit amet",
                "consectetur adipiscing elit",
                "Sed do eiusmod tempor incididunt",
                "ut labore et dolore magna aliqua",
            ]
        }
    )

    new_df = combine_and_split_text(df, width=5)
    print(new_df)


def coreferences(df, column_name):
    """
    Extract coreferences from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract coreferences from.

    Returns:
    pd.DataFrame: DataFrame with coreferences.
    """

    # Process the text data using SpaCy
    coreferences = []
    for text in df[column_name]:
        doc = nlp(text)
        if doc._.coref_chains:
            for chain in doc._.coref_chains:
                mentions = []
                for mention in chain.mentions:
                    mentions.append(
                        {
                            "text": mention.text,
                            "start": mention.start,
                            "end": mention.end,
                        }
                    )
                coreferences.append({"chain_id": chain.chain_id, "mentions": mentions})

    # Create a DataFrame with coreferences
    output_df = pd.DataFrame(
        [
            (
                coref["chain_id"],
                ", ".join([mention["text"] for mention in coref["mentions"]]),
            )
            for coref in coreferences
        ],
        columns=["chain_id", "mentions"],
    )

    return output_df


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("coreferee")
    df = pd.DataFrame(
        {"text": ["John Smith is a developer. He works at XYZ Corporation."]}
    )
    print(coreferences(df, "text"))


def emojis(string):
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


def frequent_words(df, text_column, threshold=10):
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
    combined_df = frequent_words(combined_df, "text_lower_case", threshold=3)

    print(combined_df)


def format_lowercase(df, col):
    df[col] = df[col].str.lower()
    return df


def html_tags(df, text_column):
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
    combined_df = html_tags(combined_df, "text_lower_case")

    print(combined_df)


def homographs(df, column_name):
    """
    Extract homographs from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract homographs from.

    Returns:
    pd.DataFrame: DataFrame with words and their corresponding homograph senses.
    """

    # Get unique words from the DataFrame column
    words = df[column_name].str.lower().str.split().explode().unique()

    # Create a dictionary to store homographs
    homographs_dict = defaultdict(list)

    # Populate the homographs dictionary
    for word in words:
        synsets = wordnet.synsets(word)
        if len(synsets) > 1:
            for synset in synsets:
                homographs_dict[word].append(
                    {"sense": synset.definition(), "pos": synset.pos()}
                )

    # Filter out words with only one sense
    homographs_dict = {k: v for k, v in homographs_dict.items() if len(v) > 1}

    # Create a DataFrame with words and their homograph senses
    output_df = pd.DataFrame(
        [
            (
                word,
                ", ".join([f"{sense['sense']} ({sense['pos']})" for sense in senses]),
            )
            for word, senses in homographs_dict.items()
        ],
        columns=["word", "senses"],
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "text": [
                "The bank is a financial institution",
                "The bank of the river was lined with trees",
            ]
        }
    )
    print(homographs(df, "text"))


def homophones(df, column_name):
    """
    Extract homophones from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract homophones from.

    Returns:
    pd.DataFrame: DataFrame with words and their corresponding homophones.
    """

    # Initialize the CMU Pronouncing Dictionary
    d = cmudict.dict()

    # Function to get phonemes for a word
    def get_phonemes(word):
        try:
            return d[word.lower()][0]
        except KeyError:
            return None

    # Get unique words from the DataFrame column
    words = df[column_name].str.lower().str.split().explode().unique()

    # Create a dictionary to store homophones
    homophones_dict = defaultdict(list)

    # Populate the homophones dictionary
    for word in words:
        phonemes = get_phonemes(word)
        if phonemes is not None:
            homophones_dict[tuple(phonemes)].append(word)

    # Filter out words with no homophones
    homophones_dict = {k: v for k, v in homophones_dict.items() if len(v) > 1}

    # Create a DataFrame with words and their homophones
    output_df = pd.DataFrame(
        [
            (word, ", ".join([w for w in homophones if w != word]))
            for homophones in homophones_dict.values()
            for word in homophones
        ],
        columns=["word", "homophones"],
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {"text": ["This is a test sentence", "Another sentence with different words"]}
    )
    print(homophones(df, "text"))


def hyponyms(df, column_name):
    """
    Extract hyponyms from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract hyponyms from.

    Returns:
    pd.DataFrame: DataFrame with words and their corresponding hyponyms.
    """

    # Get unique words from the DataFrame column
    words = df[column_name].str.lower().str.split().explode().unique()

    # Create a dictionary to store hyponyms
    hyponyms_dict = defaultdict(list)

    # Populate the hyponyms dictionary
    for word in words:
        synsets = wordnet.synsets(word)
        for synset in synsets:
            for hyponym in synset.hyponyms():
                hyponyms_dict[word].append(
                    {
                        "hyponym": hyponym.name().split(".")[0],
                        "definition": hyponym.definition(),
                        "pos": hyponym.pos(),
                    }
                )

    # Remove duplicates and filter out words with no hyponyms
    hyponyms_dict = {
        k: [dict(t) for t in {tuple(d.items()) for d in v}]
        for k, v in hyponyms_dict.items()
        if v
    }

    # Create a DataFrame with words and their hyponyms
    output_df = pd.DataFrame(
        [
            (
                word,
                ", ".join(
                    [
                        f"{hyponym['hyponym']} ({hyponym['pos']}) - {hyponym['definition']}"
                        for hyponym in hyponyms
                    ]
                ),
            )
            for word, hyponyms in hyponyms_dict.items()
        ],
        columns=["word", "hyponyms"],
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame({"text": ["The tree is a plant", "The car is a vehicle"]})
    print(hyponyms(df, "text"))


def lemmatize_text(text):
    nlp = spacy.load("en_core_web_sm")
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


def lexical_chains(text):
    """
    Extract lexical chains from a given text.

    Args:
    text (str): The text to extract lexical chains from.

    Returns:
    list: A list of lexical chains, where each chain is a set of words.
    """

    # Tokenize the text
    words = nltk.word_tokenize(text)

    # Remove stopwords and punctuation
    stop_words = set(nltk.corpus.stopwords.words("english"))
    words = [
        word.lower()
        for word in words
        if word.isalpha() and word.lower() not in stop_words
    ]

    # Function to get synonyms for a word
    def get_synonyms(word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().lower())
        return synonyms

    # Build lexical chains
    lexical_chains = []
    for word in words:
        found_chain = False
        word_synonyms = get_synonyms(word)
        # Check if word fits into any existing chain
        for chain in lexical_chains:
            if chain.intersection(word_synonyms):
                chain.update(word_synonyms)
                found_chain = True
                break
        if not found_chain and word_synonyms:
            lexical_chains.append(word_synonyms)

    # Filter out empty chains
    lexical_chains = [chain for chain in lexical_chains if chain]

    return lexical_chains


if __name__ == "__main__":
    nltk.download("averaged_perceptron_tagger")
    text = "The company will hire new employees. The employees will be trained by the HR department."
    print(lexical_chains(text))


def ner(df, text_column, pattern_df=None):
    nlp = spacy.load("en_core_web_sm")
    if pattern_df is not None:
        patterns = [
            {"label": row["label"], "pattern": row["pattern"].lower()}
            for index, row in pattern_df.iterrows()
        ]
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.overwrite = True
        ruler.add_patterns(patterns)
    docs = nlp.pipe(
        df[text_column].astype(str).str.lower()
    )  # Process text as lowercase
    entities = [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]
    df["entities"] = entities
    return df


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")

    pattern_df = pd.DataFrame({"label": ["GPE"], "pattern": [[{"LOWER": "indus"}]]})
    data_df = pd.DataFrame({"text": ["Example mentioning indus"]})
    result_df = ner(data_df, "text", pattern_df=pattern_df)
    print(result_df)

    data = {"text": ["Apple is a tech company", "John works in New York"]}
    df = pd.DataFrame(data)
    result_df = ner_v0(df, "text")
    print(result_df)

    content = (
        "The World Health Organization (WHO)[1] is a specialized agency"
        " of the United Nations responsible for international public health.[2] The"
        " WHO Constitution states its main objective as 'the attainment by all peoples"
        " of the highest possible level of health'.[3] Headquartered in Geneva,"
        " Switzerland, it has six regional offices and 150 field offices worldwide. "
        "The WHO was established on 7 April 1948.[4][5] The first meeting of the World"
        " Health Assembly (WHA), the agency's governing body, took place on 24 July"
        " of that year. The WHO incorporated the assets, personnel, and duties of the"
        " League of Nations' Health Organization and the Office International"
        " d'Hygiène Publique, including the International Classification of"
        " Diseases (ICD).[6] Its work began in earnest in 1951 after a significant"
        " infusion of financial and technical resources.[7]"
    )
    sentences = re.split(r"\[\d+\]", content)
    sentences = [s.strip() for s in sentences if s.strip()]
    df = pd.DataFrame(sentences, columns=["text"])

    ## Slow
    df["ner"] = df["text"].apply(ner_slow)

    ## Fast
    df = ner(df, "text")
    df


def ner_slow(texts):
    nlp = spacy.load("en_core_web_sm")
    docs = nlp.pipe(texts)
    return [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]


def ner_v0(df, text_column):
    """
    Extract Named Entities from a Pandas DataFrame's text column.

    Parameters:
    - df: Pandas DataFrame
    - text_column: str, name of the column containing text

    Returns:
    - df with a new 'entities' column containing lists of (text, label) tuples
    """
    nlp = spacy.load("en_core_web_sm")

    # Apply nlp.pipe for batch processing
    docs = nlp.pipe(df[text_column])

    # Extract entities
    entities = [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]

    # Add entities to the DataFrame
    df["entities"] = entities

    return df


def ner_summary(df):
    """
    Extracts entities from a dataframe with 'text' and 'entities' columns
    and returns a new dataframe with entity, label, count, and sentences columns.
    
    Parameters:
    df: DataFrame with columns 'text' (str) and 'entities' (list of tuples)
    
    Returns:
    DataFrame with columns: entity, label, count, sentences
    """
    # Dictionary to store entity info: {(entity, label): [sentences]}
    entity_dict = defaultdict(list)
    
    # Iterate through each row
    for idx, row in df.iterrows():
        text = row['text']
        entities = row['entities']
        
        # Process each entity in the row
        for entity, label in entities:
            # Store the sentence (text) for this entity
            entity_dict[(entity, label)].append(text)
    
    # Build result dataframe
    result_data = []
    for (entity, label), sentences in entity_dict.items():
        result_data.append({
            'entity': entity,
            'label': label,
            'count': len(sentences),
            'sentences': ', '.join(sentences)
        })
    
    # Create dataframe and sort by entity
    result_df = pd.DataFrame(result_data)
    result_df = result_df.sort_values('entity').reset_index(drop=True)
    
    return result_df


if __name__ == '__main__':
    result_df = ner_summary(df_ner)
    dataframe_to_excel(result_df, sheet_name='ner_summary')
    print(result_df)


def ner_tracking(df, column_name):
    """
    Extract entity tracking from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract entity tracking from.

    Returns:
    pd.DataFrame: DataFrame with entity tracking.
    """

    # Initialize a dictionary to store entity tracking
    entity_tracking = {}
    nlp = spacy.load("en_core_web_sm")

    # Process the text data using SpaCy
    for text in df[column_name]:
        doc = nlp(text)
        for sent in doc.sents:
            # Iterate through named entities in the sentence
            for ent in sent.ents:
                # Track entities and update if seen again
                if ent.text in entity_tracking:
                    entity_tracking[ent.text]["count"] += 1
                    entity_tracking[ent.text]["sentences"].append(sent.text)
                else:
                    entity_tracking[ent.text] = {
                        "label": ent.label_,
                        "count": 1,
                        "sentences": [sent.text],
                    }

    # Create a DataFrame with entity tracking
    output_df = pd.DataFrame(
        [
            (entity, info["label"], info["count"], ", ".join(info["sentences"]))
            for entity, info in entity_tracking.items()
        ],
        columns=["entity", "label", "count", "sentences"],
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "text": [
                "John Smith is a developer. He works at XYZ Corporation.",
                "John Smith is a great developer.",
            ]
        }
    )
    print(ner_tracking(df, "text"))


def polysemy(df, column_name):
    """
    Extract polysemous words from a given DataFrame column.

    Args:
    df (pd.DataFrame): DataFrame containing text data.
    column_name (str): Name of the column to extract polysemous words from.

    Returns:
    pd.DataFrame: DataFrame with words and their corresponding polysemous senses.
    """

    # Get unique words from the DataFrame column
    words = df[column_name].str.lower().str.split().explode().unique()

    # Create a dictionary to store polysemous words
    polysemy_dict = defaultdict(list)

    # Populate the polysemy dictionary
    for word in words:
        synsets = wordnet.synsets(word)
        if len(synsets) > 1:
            # Check if the synsets are related (i.e., polysemous)
            root_hypernyms = [synset.root_hypernyms() for synset in synsets]
            if (
                len(
                    set([hypernym[0].name() for hypernym in root_hypernyms if hypernym])
                )
                == 1
            ):
                for synset in synsets:
                    polysemy_dict[word].append(
                        {
                            "sense": synset.definition(),
                            "pos": synset.pos(),
                            "examples": synset.examples(),
                        }
                    )

    # Filter out words with no polysemous senses
    polysemy_dict = {k: v for k, v in polysemy_dict.items() if len(v) > 1}

    # Create a DataFrame with words and their polysemous senses
    output_df = pd.DataFrame(
        [
            (
                word,
                ", ".join([f"{sense['sense']} ({sense['pos']})" for sense in senses]),
            )
            for word, senses in polysemy_dict.items()
        ],
        columns=["word", "senses"],
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "text": [
                "The head of the company is very experienced",
                "The head of the river is in the mountains",
            ]
        }
    )
    print(polysemy(df, "text"))


def pos_tag(df, col):
    """Process the text and get POS tags"""
    nlp = spacy.load("en_core_web_sm")
    df[f"{col}_pos_tag"] = df[col].apply(
        lambda x: [(token.text, token.pos_) for token in nlp(str(x))]
    )

    return df


if __name__ == "__main__":
    df = pd.DataFrame({"text": ["This is a sample text.", "Another sample text."]})

    df = pos_tag(df, "text")

    print(df)


def punctuations():
    pass


def rare_words(df, text_column, threshold=5):
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
    combined_df = rare_words(combined_df, "text_lower_case", threshold=2)

    print(combined_df)


def stopwords(df, column_name):
    """
    Removes stopwords from a specified text column in a pandas DataFrame.

    This function processes each text entry in the given column, tokenizes it
    using spaCy, and filters out tokens that are identified as stopwords,
    punctuation, or whitespace.

    Args:
        df (pd.DataFrame): The input pandas DataFrame.
        column_name (str): The name of the column containing the text data.

    Returns:
        pd.DataFrame: A new DataFrame with the specified column processed
                      and stopwords removed.
    """

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading 'en_core_web_sm' model...")
        from spacy.cli import download

        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in the DataFrame.")
        return df

    def process_text(text):
        """Helper function to process a single string."""
        if pd.isna(text):
            return ""

        doc = nlp(str(text))
        # Filter out stopwords, punctuation, and spaces.
        filtered_tokens = [
            token.text
            for token in doc
            if not token.is_stop and not token.is_punct and not token.is_space
        ]
        return " ".join(filtered_tokens)

    # Apply the processing function to the specified column.
    df[column_name] = df[column_name].apply(process_text)

    return df


if __name__ == "__main__":
    # Create a sample DataFrame.
    data = {
        "ID": [1, 2, 3],
        "text": [
            "This is a sample sentence to show how to use the function.",
            "The quick brown fox jumps over the lazy dog.",
            "I'm going to the store, and he is coming with me.",
        ],
    }
    sample_df = pd.DataFrame(data)

    print("--- Original DataFrame ---")
    print(sample_df)
    print("\n" + "-" * 30 + "\n")

    # Call the function to remove stopwords from the 'text' column.
    processed_df = stopwords(sample_df.copy(), "text")

    print("--- DataFrame with Stopwords Removed ---")
    print(processed_df)


def sentences_segmenter(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Performs sentence segmentation on a specified column of a pandas DataFrame.

    Each sentence is placed into a new row in the resulting DataFrame,
    with other columns from the original row duplicated.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the column containing the text to be segmented.

    Returns:
        pd.DataFrame: A new DataFrame with each sentence as a separate row.
    """
    try:
        # Load the English spaCy model
        # The 'sentencizer' component is automatically included in this model
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("SpaCy model 'en_core_web_sm' not found. Downloading now...")
        from spacy.cli import download

        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    segmented_data = []

    # Iterate over each row in the input DataFrame
    for _, row in df.iterrows():
        # Get the text from the specified column, handling potential NaN values
        text_to_segment = str(row[column_name]) if pd.notna(row[column_name]) else ""

        # Process the text with spaCy to get a Doc object
        doc = nlp(text_to_segment)

        # Iterate through the sentences identified by spaCy
        for sent in doc.sents:
            # Create a new row with the segmented sentence
            new_row = row.copy()
            new_row[column_name] = sent.text.strip()
            segmented_data.append(new_row)

    # Create a new DataFrame from the segmented data
    segmented_df = pd.DataFrame(segmented_data)

    return segmented_df


if __name__ == "__main__":
    # Create a sample DataFrame
    data = {
        "id": [1, 2, 3],
        "text": [
            "This is the first sentence. Here is the second sentence. Is this the third sentence?",
            "Another paragraph begins now. A new sentence follows. The end.",
            "A short sentence.",
        ],
        "category": ["A", "B", "A"],
    }
    df = pd.DataFrame(data)

    print("Original DataFrame:")
    print(df)
    print("\n" + "=" * 50 + "\n")

    # Segment the sentences in the 'text' column
    segmented_df = sentences_segmenter(df, "text")

    print("Segmented DataFrame:")
    print(segmented_df)
    print("\n" + "=" * 50 + "\n")

    # The resulting DataFrame has each sentence on a new line,
    # with the original metadata ('id' and 'category') preserved.
    # The original text is replaced with the segmented sentence.


def stem_text(text):
    """
    Stems a text string using SpaCy for tokenization and NLTK for stemming.
    """
    nlp = spacy.load("en_core_web_sm")
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


def synonym(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    # Remove the original word from the synonyms
    synonyms.discard(word.lower())
    return ", ".join(synonyms)


def wfd(df, column_name):
    """Word frequency distribution."""
    # Load Spacy model
    nlp = spacy.load("en_core_web_sm")

    # Process text data using Spacy pipe
    docs = nlp.pipe(df[column_name])

    # Get word frequencies
    word_freq = Counter(
        token.text.lower() for doc in docs for token in doc if not token.is_punct
    )

    # Calculate total words
    total_words = sum(word_freq.values())

    # Create output DataFrame
    output_df = pd.DataFrame(
        {
            "word": list(word_freq.keys()),
            "total words": [total_words] * len(word_freq),
            "frequency": list(word_freq.values()),
            "frequency %": [freq / total_words * 100 for freq in word_freq.values()],
        }
    )

    # Sort output DataFrame by frequency in descending order
    output_df = output_df.sort_values(by="frequency", ascending=False).reset_index(
        drop=True
    )

    return output_df


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "text": [
                "This is a sample text.",
                "Another text for analysis.",
                "Text analysis is fun.",
            ]
        }
    )
    output_df = wfd(df, "text")
    print(output_df)


def wfd_antonym(df, column_name, word_frequency, word_len):
    """Word frequency distribution."""
    # Load Spacy model
    nlp = spacy.load("en_core_web_sm")

    # Process text data using Spacy pipe
    docs = nlp.pipe(df[column_name])

    # Get word frequencies
    word_freq = Counter(
        token.text.lower() for doc in docs for token in doc if not token.is_punct
    )

    # Filter out words with frequency less than 2 or length less than 3
    filtered_word_freq = {
        word: freq
        for word, freq in word_freq.items()
        if freq >= word_frequency and len(word) >= word_len
    }

    # Get antonyms for filtered words
    output_df = pd.DataFrame({"word": list(filtered_word_freq.keys())})
    output_df["antonym"] = output_df["word"].apply(antonym)

    # Filter out words without antonyms
    output_df = output_df[output_df["antonym"] != ""]

    return output_df


if __name__ == "__main__":
    nltk.download("wordnet")

    df = pd.DataFrame(
        {
            "text": [
                "This is a good sample text.",
                "Another bad text for analysis.",
                "Text analysis is good.",
                "Bad analysis is a key part of the job.",
                "Job requires good analysis skills.",
                "Good job is appreciated.",
            ]
        }
    )
    output_df = wfd_antonym(df, "text")
    print(output_df)


def wfd_synonym(df, column_name, word_frequency, word_len):
    """Word frequency distribution."""
    # Load Spacy model
    nlp = spacy.load("en_core_web_sm")

    # Process text data using Spacy pipe
    docs = nlp.pipe(df[column_name])

    # Get word frequencies
    word_freq = Counter(
        token.text.lower() for doc in docs for token in doc if not token.is_punct
    )

    # Filter out words with frequency less than 2 or length less than 3
    filtered_word_freq = {
        word: freq
        for word, freq in word_freq.items()
        if freq >= word_frequency and len(word) >= word_len
    }

    # Get synonyms for filtered words
    output_df = pd.DataFrame({"word": list(filtered_word_freq.keys())})
    output_df["synonym"] = output_df["word"].apply(synonym)

    return output_df


if __name__ == "__main__":
    nltk.download("wordnet")

    df = pd.DataFrame(
        {
            "text": [
                "This is a sample text.",
                "Another text for analysis.",
                "Text analysis is fun.",
                "Analysis is a key part of the job.",
                "Job requires good analysis skills.",
            ]
        }
    )
    output_df = wfd_synonym(df, "text")
    print(output_df)


def wsd_example(word, context):
    # Simplistic approach for demonstration
    if word == "apple":
        if "pie" in context:
            return "The tech company"
        else:
            return "The fruit"
    return None


def urls(df, text_column):
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
    combined_df = urls(combined_df, "text_lower_case")

    print(combined_df)
