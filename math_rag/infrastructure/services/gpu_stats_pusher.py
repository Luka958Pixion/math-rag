from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from math_rag.infrastructure.clients import HPCClient


class GPUStatsPusher:
    def __init__(self, hpc_client: HPCClient, pushgateway_base_url: str):
        self.hpc_client = hpc_client
        self.pushgateway_base_url = pushgateway_base_url
        self.registry = CollectorRegistry()

        self.gpu_util_percent_gauge = Gauge(
            'resources_used_gpu_util_percent',
            'GPU utilization percent of PBS job',
            ['job_id', 'node', 'gpu'],
            registry=self.registry,
        )
        self.gpu_mem_bytes_gauge = Gauge(
            'resources_used_gpu_mem_bytes',
            'GPU memory used (bytes) of PBS job',
            ['job_id', 'node', 'gpu'],
            registry=self.registry,
        )

    async def push(self):
        gpu_stats = await self.hpc_client.gpu_statistics()
        for entry in gpu_stats.entries:
            job_id = str(entry.job_id)
            for sub in entry.sub_entries:
                self.gpu_util_percent_gauge.labels(job_id=job_id, node=sub.node, gpu=sub.gpu).set(
                    sub.used_percent
                )
                self.gpu_mem_bytes_gauge.labels(job_id=job_id, node=sub.node, gpu=sub.gpu).set(
                    sub.mem_used
                )

        push_to_gateway(self.pushgateway_base_url, job='gpu_stats', registry=self.registry)
