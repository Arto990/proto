import argparse
from neuro_core.neuropacks.health.protocheck.ingesters import deleted
from neuro_core.neuropacks.health.protocheck.core.utils.prosthetics_filter import filter_prosthetics

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True)
args = parser.parse_args()

df = deleted.load_deleted_from_file(args.file)
df = filter_prosthetics(df)
deleted.upsert_deleted_acts(df)
