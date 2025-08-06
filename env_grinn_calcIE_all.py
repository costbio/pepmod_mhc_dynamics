import pandas as pd
import glob, os, sys, tqdm
import subprocess

# Read best_models.csv file
df = pd.read_csv('best_models.csv')

# Create output_ie folder if not exists
if not os.path.exists('output_ie_all'):
    os.makedirs('output_ie_all')

# For each row, call /mnt/d/repos/structbio_workflows/grinn_workflow.py
for index, row in tqdm.tqdm(df.iterrows()):
    # Get the folder name
    folder = row['folder']

    # Get the file name
    fl = row['best_model']

    # File full path
    fl = os.path.join(folder, fl)

    # Output folder full path
    output_folder = os.path.join('output_ie_all', folder)

    # Call /mnt/d/repos/structbio_workflows/grinn_workflow.py
    # Note that source_sel must be chain C to select peptide (gromacs reset chain IDs somehow?)
    subprocess.run(['python', '/mnt/e/repos/structbio_workflows/grinn_workflow.py', fl, '/mnt/e/repos/structbio_workflows/mdp_files/', output_folder, 
                    '--initpairfiltercutoff', '10', '--gmxrc_path', '/mnt/d/software/gromacs2023_4/bin/GMXRC','--nt','18',
                    '--source_sel','all','--target_sel','all'])
    
