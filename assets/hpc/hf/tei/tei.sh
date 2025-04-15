#!/bin/bash
#PBS -P gpu
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu

cd "${PBS_O_WORKDIR:-""}"
module load utils/python/3.12.2

export PYTHONUNBUFFERED=1

python3 tei.py