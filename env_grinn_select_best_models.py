import pandas as pd
import glob, os, sys

# Scan through the folder hierarchy in models folder, find a csv file containing molpdf scores,
# read it, and find the best model based on the lowest molpdf score.

folders = glob.glob('E:\Evren-Tez\HLA-A Subtypes/*/*')

# Start a data frame to store the best model for each folder
df_best = pd.DataFrame(columns=['folder', 'best_model', 'molpdf'])

for fold in folders:
    files = glob.glob(fold + '/*.tsv')
    print(files)
    for fl in files:
        if 'molpdf' in fl:
            df = pd.read_csv(fl, delimiter='\t',header=None)
            best_model = df.loc[df[1].idxmin()]
            print(fold, best_model[0], best_model[1])
            df_best = df_best._append({'folder': fold, 'best_model': best_model[0], 'molpdf': best_model[1]}, ignore_index=True)
            break

df_best.to_csv('best_models_10mers.csv', index=False)