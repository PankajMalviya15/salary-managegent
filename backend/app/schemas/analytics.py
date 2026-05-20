"""
Pydantic schemas for analytics endpoints.
"""

from pydantic import BaseModel


class CountrySalarySummary(BaseModel):
    country: str
    min_salary: float
    max_salary: float
    avg_salary: float
    employee_count: int


class JobTitleSalarySummary(BaseModel):
    job_title: str
    country: str
    avg_salary: float
    employee_count: int


class HeadcountByGroup(BaseModel):
    group: str
    count: int


class SalaryBucket(BaseModel):
    bucket_min: float
    bucket_max: float
    count: int


class SalaryDistribution(BaseModel):
    buckets: list[SalaryBucket]
    total: int


class OutlierEmployee(BaseModel):
    id: int
    full_name: str
    email: str
    job_title: str
    country: str
    salary: float
    peer_mean: float
    peer_std: float
    deviation: float  # how many SDs above/below mean

    model_config = {"from_attributes": True}
