#!/bin/bash
#PBS -P gpu
#PBS -N tgi
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu

module load utils/python/3.12.2
cd "${PBS_O_WORKDIR:-""}"

export PYTHONUNBUFFERED=1

python tgi.py