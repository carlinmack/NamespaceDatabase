#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --time=1:00:00
#SBATCH --mem=200
#SBATCH --requeue
#SBATCH --job-name="parsewiki"
#SBATCH --array=1-4
#SBATCH --output=log/%A_%a.out

source /etc/profile.d/modules.sh
module load python3.8.0

# Print out the hostname to the log
hostname
# cd to the directory
cd /p/wikiactors/nsdb

sleep $SLURM_ARRAY_TASK_ID
python --version
date
srun --cpus-per-task 5 python nsdb.py $SLURM_JOB_ID

# source:
#   -  https://rcc.uchicago.edu/docs/tutorials/kicp-tutorials/running-jobs.html
#   _  https://help.rc.ufl.edu/doc/SLURM_Job_Arrays