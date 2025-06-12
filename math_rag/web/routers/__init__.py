from .datasets.math_expressions.create import router as create_math_expression_dataset_router
from .datasets.math_expressions.delete import router as delete_math_expression_dataset_router
from .fine_tune_jobs.create import router as create_fine_tune_job_router
from .health import router as health_router
from .indexes.create import router as create_index_router
from .problems.create import router as create_problem_router
from .scalar import router as scalar_router


routers = [
    create_math_expression_dataset_router,
    delete_math_expression_dataset_router,
    create_fine_tune_job_router,
    health_router,
    create_index_router,
    create_problem_router,
    scalar_router,
]

__all__ = ['routers']
