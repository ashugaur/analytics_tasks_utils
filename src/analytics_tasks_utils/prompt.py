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
    full_prompt = f"\n\n{question}\n{dataframe_string}"
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


def persistency_calc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the rate of change for each drug as (lagged_value - current_value)
    for each data point, sorted by day.
    Also adds columns for the 'value' at Day 180 and Day 360 for each drug.

    Args:
        df (pd.DataFrame): The input DataFrame with 'x', 'y', and 'value' columns.

    Returns:
        pd.DataFrame: A DataFrame containing the drug, day, and the calculated
                      lagged rate of change, plus values at Day 180 and Day 360.
    """

    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()

    # Convert 'x' column to numerical days for easier sorting and calculations
    # This extracts the number from strings like "Day 0", "Day 30", etc.
    df_copy["day_num"] = df_copy["x"].str.extract("(\d+)").astype(int)

    # Sort the DataFrame first by drug ('y') and then by the numerical day ('day_num').
    # This is essential for correctly applying the 'shift' operation within each drug group.
    df_sorted = df_copy.sort_values(by=["y", "day_num"]).reset_index(drop=True)

    # Calculate the lagged value for each drug group.
    # The 'shift(1)' function gets the value from the previous row within each group.
    df_sorted["lagged_value"] = df_sorted.groupby("y")["value"].shift(1)

    # Calculate the rate of change as (lagged_value - current_value).
    # This effectively shows the decrease or increase from the previous time step.
    df_sorted["rate_of_change"] = df_sorted["lagged_value"] - df_sorted["value"]

    # Filter out the rows where 'lagged_value' is NaN (which will be the first data point
    # for each drug, as there's no preceding value to lag from).
    result_df = df_sorted.dropna(subset=["rate_of_change"]).copy()

    # --- New functionality: Add value at Day 180 and Day 360 ---
    day_180_values = df_copy[df_copy["day_num"] == 180][["y", "value"]].rename(
        columns={"value": "value_at_day_180"}
    )
    day_360_values = df_copy[df_copy["day_num"] == 360][["y", "value"]].rename(
        columns={"value": "value_at_day_360"}
    )

    # Merge these values back into the result_df based on the drug ('y')
    result_df = pd.merge(result_df, day_180_values, on="y", how="left")
    result_df = pd.merge(result_df, day_360_values, on="y", how="left")

    # Select and reorder the relevant columns for the final output, including the new columns
    return result_df[
        [
            "y",
            "x",
            "value",
            "lagged_value",
            "rate_of_change",
            "value_at_day_180",
            "value_at_day_360",
        ]
    ]


def persistency_measures(dft):
    """Create prompts using calculations on data."""
    input_text_data = create_prompt_with_dataframe("Data", dft)

    calc = persistency_calc(dft)
    persistency_by_days = (
        calc[["y", "value_at_day_180", "value_at_day_360"]]
        .drop_duplicates()
        .set_index(["y"])
    )

    measure_of_dispersion = calc.groupby(["y"]).agg(
        {"rate_of_change": ["mean", "var", "std"]}
    )

    input_text_persistency = create_prompt_with_dataframe(
        "Persistency", persistency_by_days
    )

    input_text_rate_of_change = create_prompt_with_dataframe("", measure_of_dispersion)

    return (
        persistency_by_days,
        measure_of_dispersion,
        input_text_data,
        input_text_persistency,
        input_text_rate_of_change,
    )
