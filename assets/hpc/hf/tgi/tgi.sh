#!/bin/bash
#PBS -P gpu
#PBS -N tgi
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu

cd "${PBS_O_WORKDIR:-""}"

# exit immediately if a command exits with a non-zero status
set -e

set -a
source .env.hpc.hf.tgi
set +a

export PYTHONUNBUFFERED=1
export TGI_BASE_URL="http://0.0.0.0:8000"

export http_proxy="http://10.150.1.1:3128"
export https_proxy="http://10.150.1.1:3128"

mkdir -p data/$MODEL_HUB_ID
apptainer run --nv --bind $PWD/data:/data hf_cli.sif

unset http_proxy
unset https_proxy

# uses & to run in the background
#apptainer run --nv --bind $PWD/data/$MODEL_HUB_ID:/model tgi_server.sif &
apptainer instance start --nv --bind $PWD/data/$MODEL_HUB_ID:/model tgi_server.sif tgi_server_instance


echo "Waiting for the TGI server to become healthy..."

while true; do
    # || true ensures zero exit status even if command fails because of the set -e
    response=$(curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:8000/health || true)

    if [ "$response" -eq 200 ]; then
        echo "TGI server is healthy."
        break

    else
        echo "Health check returned status code $response. Retrying in 5 seconds..."
        sleep 5
    fi
done

env -u MODEL_HUB_ID apptainer run --env-file .env.hpc.hf.tgi tgi_client.sif
apptainer instance stop tgi_server_instance
