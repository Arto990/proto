import argparse
from neuro_core.neuropacks.health.protocheck.ingesters import invoices
from neuro_core.neuropacks.health.protocheck.core.utils.prosthetics_filter import filter_prosthetics

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True)
args = parser.parse_args()

df = invoices.load_invoices_from_file(args.file)
df = filter_prosthetics(df)
invoices.upsert_invoices(df)
