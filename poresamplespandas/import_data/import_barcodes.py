import pandas as pd
import yaml


def make_barcodes_df(file: str) -> pd.DataFrame:
    """
    Turns a yaml file into a df with barcodes in long format.
    """
    with open(file, "r") as f:
        codes = yaml.safe_load(f)

    return (
        pd.DataFrame(codes)
        .reset_index()
        .melt(id_vars="index", var_name="kit", value_name="sequence")
        .rename(columns={"index": "name"})
        .assign(whole_name=lambda x: x.kit + " --- " + x.name)
    )
