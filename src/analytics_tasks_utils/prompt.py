# %% Prompts

import pandas as pd


def create_prompt_with_dataframe(question: str, df: pd.DataFrame) -> str:
    """
    Combines a question with a Pandas DataFrame into a single prompt string.

    Args:
        question: The main question or instruction for the language model.
        df: The Pandas DataFrame to include in the prompt.

    Returns:
        A string containing the combined prompt. The DataFrame is formatted
        as a string and appended to the question.
    """
    dataframe_string = df.to_string()
    full_prompt = f"{question}\n\nData:\n{dataframe_string}"
    return full_prompt


if __name__ == "__main__":
    data = {"col1": [1, 2], "col2": ["a", "b"]}
    my_df = pd.DataFrame(data)
    my_question = (
        "Based on the following data, what is the relationship between col1 and col2?"
    )

    prompt = create_prompt_with_dataframe(my_question, my_df)
    print(prompt)

    # Now you can pass this 'prompt' string to your Ollama model.
    # For example (assuming you have a way to interact with Ollama in Python):
    # response = ollama_model.generate(prompt)
    # print(response)
