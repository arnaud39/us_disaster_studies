"""Automatic pipeline for CDC wonder grouped by months and UCD ICD chapter."""
from countries_code import code
from ast import Return
from typing import List

import pandas as pd
import os


def auto_wonder_pipeline(
    dir_: str = "data/CDC",
    columns: List[str] = ["State", "Month Code", "UCD - ICD Chapter", "Deaths"],
    observed_outcome: List[str] = [
        "Diseases of the circulatory system",
        "Diseases of the respiratory system",
    ],
    short_outcome: List[str] = ["circulatory system", "respiratory system"],
    identifer: str = "all",
) -> pd.DataFrame:
    """Load the CDC xonder data

    Args:
        dir_ (str, optional): _description_. Defaults to "data/CDC".
        columns (List[str], optional): _description_. Defaults to ["State", "Month Code", "UCD - ICD Chapter", "Deaths"].
        observed_outcome (List[str], optional): _description_. Defaults to [ "Diseases of the circulatory system", "Diseases of the respiratory system", ].
        short_outcome (List[str], optional): Used to name the column  in the dataframe. Defaults to ["circulatory system", "respiratory system"].
        identifer (str, optional): _description_. Defaults to "all".

    Returns:
        pd.DataFrame: _description_
    """
    files_ = [
        f"{dir_}/{data_file}"
        for data_file in os.listdir(dir_)
        if "txt" in data_file and identifer in data_file
    ]

    df_outcomes_ = pd.concat(
        objs=[
            pd.read_csv(file, delimiter="\t", parse_dates=["Month Code"])[
                columns
            ].dropna()
            for file in files_
        ]
    )

    df_outcomes_["date"] = df_outcomes_["Month Code"]

    df_outcomes_["State"] = df_outcomes_["State"].map(code)

    df_outcomes_.rename(
        columns={
            "State": "state",
            "UCD - ICD Chapter": "cause",
            "ICD Chapter": "cause",
            "Deaths": "deaths",
            "Month Code": "time",
        },
        inplace=True,
    )

    df_outcomes = df_outcomes_.set_index(["state", "time", "cause"])
    df_outcomes.sort_index(ascending=True, inplace=True)

    df_observed = pd.concat(
        [
            (
                df_outcomes.loc[(slice(None), slice(None), outcome), :]
                .reset_index()
                .set_index(["state", "time"])
                .rename(columns={"deaths": "{}deaths".format(short_outcome[:3])})
                .drop("cause", axis=1)
            )
            for outcome, short_outcome in zip(observed_outcome, short_outcome)
        ],
        axis=1,
    )

    df_observed = df_observed.assign(totaldeaths=lambda x: x.cirdeaths + x.resdeaths)

    return df_observed.loc[:, ~df_observed.columns.duplicated()]
