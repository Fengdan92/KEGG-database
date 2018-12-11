#!/bin/bash
#SBATCH --job-name=ECOLI
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --ntasks=16
#SBATCH --mem-per-cpu=1G
#SBATCH --mail-user=email
#SBATCH --mail-type=ALL
#SBATCH --time=23:59:59
srun ./run_jobs $1
