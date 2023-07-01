#!/usr/bin/env python

import argparse
import json
import glob
import os
import shutil
from pathlib import Path
import pandas as pd

 # argparse
HELPTEXT = """
Script to reorg SP's T1w directory into quasi-bids and write participants.tsv
"""
parser = argparse.ArgumentParser(description=HELPTEXT)
parser.add_argument('--global_config', type=str, help='path to global configs for a given mr_proc dataset', required=True)
parser.add_argument('--session_id', type=str, help='session_id of the participant', default="01")
parser.add_argument('--run_id', type=str, help='run_id of the scan', default="1")

args = parser.parse_args()

global_config_file = args.global_config
session_id = args.session_id
run_id = args.run_id

# Read global configs
with open(global_config_file, 'r') as f:
    global_configs = json.load(f)


DATASET_ROOT = global_configs["DATASET_ROOT"]
mr_proc_manifest = f"{DATASET_ROOT}/tabular/mr_proc_manifest.csv"

non_bids_dir = f"{DATASET_ROOT}/scratch/T1/"
bids_dir = f"{DATASET_ROOT}/bids/"
bids_participants_tsv = f"{bids_dir}/participants.tsv"

manifest_df = pd.read_csv(mr_proc_manifest)
participant_ids = manifest_df["participant_id"].values
bids_ids = manifest_df["bids_id"].values

print(f"n_participants: {len(participant_ids)}")

successful_bids_ids = []
for p_id, b_id in list(zip(participant_ids, bids_ids)):
    print(f"participant: {p_id}, bids: {b_id}")
    
    # src
    non_bids_T1_file = f"{non_bids_dir}/{p_id}/{p_id}.nii"
    non_bids_json_file = f"{non_bids_dir}/{p_id}/{p_id}.json"

    # dst
    bids_participant_dir = f"{bids_dir}/{b_id}/ses-{session_id}/anat/"
    bids_T1_file = f"{bids_participant_dir}/{b_id}_ses-{session_id}_run_{run_id}_T1w.nii"
    bids_json_file = f"{bids_participant_dir}/{b_id}_ses-{session_id}_run_{run_id}_T1w.json"

    # check subdirs 
    Path(f"{bids_participant_dir}").mkdir(parents=True, exist_ok=True)

    # copy + rename files
    try:
        shutil.copyfile(f"{non_bids_T1_file}", f"{bids_T1_file}")
        shutil.copyfile(f"{non_bids_json_file}", f"{bids_json_file}")

        successful_bids_ids.append(b_id)
    
    except Exception as e:
        print(e) 

# Save minimal participants.tsv
bids_participants_df = pd.DataFrame()
bids_participants_df["participant_id"] = successful_bids_ids
bids_participants_df.to_csv(bids_participants_tsv, index=None, sep="\t")
