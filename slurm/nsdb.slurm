#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=11
#SBATCH --time=168:00:00
#SBATCH --mem=1000
#SBATCH --requeue
#SBATCH --job-name="parsewiki"
#SBATCH --array=1-2
#SBATCH --output=log/%A_%a.out

source /etc/profile.d/modules.sh
module load python3.8.0

# Print out the hostname to the log
hostname
# cd to the directory
cd /p/wikiactors/nsdb

sleep $(((SLURM_ARRAY_TASK_ID-1)*30))
python --version
date
srun --cpus-per-task 11 python nsdb.py $SLURM_JOB_ID

# source:
#   -  https://rcc.uchicago.edu/docs/tutorials/kicp-tutorials/running-jobs.html
#   _  https://help.rc.ufl.edu/doc/SLURM_Job_Arrays