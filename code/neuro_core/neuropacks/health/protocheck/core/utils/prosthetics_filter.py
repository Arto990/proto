import pandas as pd
import sqlite3
from neuro_core.neuropacks.health.protocheck.core.constants import DB_PATH

def filter_prosthetics(df: pd.DataFrame, db_path: str = DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        prosthetics = pd.read_sql("SELECT code FROM ccam_prosthetics", conn)['code'].tolist()
    return df[df["code"].isin(prosthetics)].copy()
