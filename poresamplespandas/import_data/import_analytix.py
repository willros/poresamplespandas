import pandas as pd

column_names = {
    "Beställarkod": "client",
    "Kön": "sex",
    "Prov ID": "sample_name",
    "Provdatum": "sample_date",
    "Analys": "analysis",
    "Ålder (vid provtagning)": "age",
    "ProvNr": "sample_id",
    "Godkännandedatum": "apprvl_date",
    "Resultat": "result",
}


def import_analytix(input_file: str) -> pd.DataFrame:
    """
    Returns a clean dataframe from Analytix input file
    :param input_file: str. Path to Analytix file.
    :returns: pd.DataFrame. Cleaned dataframe.
    """
    return (
        pd.read_csv(input_file, sep=";")
        .rename(columns=column_names)
        .dropna()
        # add new columns
        .assign(order=0, barcodes=" ", kit=" ", flowcell=" ", comment=" ", testar=" ")
        # order and filter the columns
        [["sample_id", "barcodes", "kit", "flowcell", "sex", "age", "comment", "order", "testar"]]
    )
