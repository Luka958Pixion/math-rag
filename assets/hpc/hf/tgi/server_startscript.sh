#!/bin/bash
set -e
cat > /tmp/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tgi'
    static_configs:
      - targets: ['0.0.0.0:8000']
EOF

if [ -z "$LORA_ADAPTERS" ]; then
    echo "Starting TGI..."
    text-generation-launcher \
        --model-id /model \
        --port 8000 \
        --hostname 0.0.0.0 \
        --prometheus-port 9000 \
        > /tmp/tgi_output.log \
        2> /tmp/tgi_error.log &
else
    echo "Starting TGI with LoRA adapters: $LORA_ADAPTERS..."
    text-generation-launcher \
        --model-id /model \
        --lora-adapters "$LORA_ADAPTERS" \
        --port 8000 \
        --hostname 0.0.0.0 \
        --prometheus-port 9000 \
        > /tmp/tgi_output.log \
        2> /tmp/tgi_error.log &
fi

TGI_PID=$!

/opt/prometheus/prometheus \
    --config.file=/tmp/prometheus.yml \
    --storage.tsdb.path=/data \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-admin-api \
    --log.level=debug \
    > /tmp/prometheus_output.log \
    2> /tmp/prometheus_error.log &

PROMETHEUS_PID=$!

wait $TGI_PID $PROMETHEUS_PID