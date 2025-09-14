import argparse
from neuro_core.neuropacks.health.protocheck.ingesters.quotes import load_quotes_csv, upsert_quotes


def main():
    parser = argparse.ArgumentParser(description="Load deleted quotes CSV into the database.")
    parser.add_argument("--csv", required=True, help="Path to deleted quotes CSV file.")
    args = parser.parse_args()

    df = load_quotes_csv(args.csv)
    upsert_quotes(df)


if __name__ == "__main__":
    main()
