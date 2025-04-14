#!/bin/bash
#PBS -P gpu
#PBS -N tgi
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu

cd "${PBS_O_WORKDIR:-""}"

export PYTHONUNBUFFERED=1

apptainer run tgi.sif
