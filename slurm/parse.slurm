#!/bin/bash

#SBATCH --cpus-per-task 1
#SBATCH --time 1:00:00
#SBATCH --mem=200
#SBATCH --requeue
#SBATCH --job-name="parsewiki"
#SBATCH --ntasks=1
#SBATCH --array=1-99%10
#SBATCH --output=log/%A_%a.out

source /etc/profile.d/modules.sh
module load python3.8.0

# Print out the hostname to the log
hostname
# cd to the directory
cd /p/wikiactors/nsdb
# Run programs
# the environment variable SLURM_ARRAY_TASK_ID contains
# the index corresponding to the current job step
sleep $((SLURM_ARRAY_TASK_ID % 10))
python --version
date
python slurm.py $SLURM_JOB_ID$SLURM_ARRAY_TASK_ID

# source:
#   -  https://rcc.uchicago.edu/docs/tutorials/kicp-tutorials/running-jobs.html
#   _  https://help.rc.ufl.edu/doc/SLURM_Job_Arrays