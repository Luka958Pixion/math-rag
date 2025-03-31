#!/bin/bash

#PBS -N hello
#PBS -o output.log
#PBS -e error.log
#PBS -q cpu
#PBS -l ngpus=0
#PBS -l ncpus=4
sleep 600
echo "Hello world"