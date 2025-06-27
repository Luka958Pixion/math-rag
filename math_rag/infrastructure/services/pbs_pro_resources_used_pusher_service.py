from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from math_rag.application.base.services import BasePBSProResoucesUsedPusherService
from math_rag.infrastructure.clients import PBSProClient


class PBSProResoucesUsedPusherService(BasePBSProResoucesUsedPusherService):
    def __init__(self, pbs_pro_client: PBSProClient, pushgateway_base_url: str):
        self.pbs_pro_client = pbs_pro_client
        self.pushgateway_base_url = pushgateway_base_url
        self.registry = CollectorRegistry()

        self.cpu_percent_gauge = Gauge(
            'resources_used_cpu_percent',
            'CPU percentage of PBS job',
            ['job_id'],
            registry=self.registry,
        )
        self.cpu_time_gauge = Gauge(
            'resources_used_cpu_seconds_total',
            'Total CPU time of PBS job in seconds',
            ['job_id'],
            registry=self.registry,
        )
        self.num_cpus_gauge = Gauge(
            'resources_used_num_cpus',
            'Number of CPUs allocated to PBS job',
            ['job_id'],
            registry=self.registry,
        )
        self.mem_bytes_gauge = Gauge(
            'resources_used_mem_bytes',
            'Resident memory bytes of PBS job',
            ['job_id'],
            registry=self.registry,
        )
        self.vmem_bytes_gauge = Gauge(
            'resources_used_vmem_bytes',
            'Virtual memory bytes of PBS job',
            ['job_id'],
            registry=self.registry,
        )
        self.wall_time_gauge = Gauge(
            'resources_used_wall_seconds_total',
            'Wall clock time of PBS job in seconds',
            ['job_id'],
            registry=self.registry,
        )

    async def push(self, job_name: str):
        job_id = await self.pbs_pro_client.queue_select(job_name)

        if not job_id:
            return

        pbs_pro_job_full = await self.pbs_pro_client.queue_status_full(job_id)
        resources_used = pbs_pro_job_full.resources_used

        self.cpu_percent_gauge.labels(job_id=job_id).set(resources_used.cpu_percent)
        self.cpu_time_gauge.labels(job_id=job_id).set(resources_used.cpu_time.total_seconds())
        self.num_cpus_gauge.labels(job_id=job_id).set(resources_used.num_cpus)
        self.mem_bytes_gauge.labels(job_id=job_id).set(resources_used.mem)
        self.vmem_bytes_gauge.labels(job_id=job_id).set(resources_used.vmem)
        self.wall_time_gauge.labels(job_id=job_id).set(resources_used.wall_time.total_seconds())

        push_to_gateway(
            self.pushgateway_base_url,
            job=f'pbs_pro_resources_used_{job_id}',
            registry=self.registry,
        )
