for i in {0..25}
do
	echo $i
	sbatch submit_job.slurm $i
done
