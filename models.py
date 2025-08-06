import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class JobStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY" 
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class RetryPolicy:
    max_retries: int = 3
    
@dataclass
class Job:

    name: str
    schedule: str
    command: str


    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: Priority = Priority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    last_triggered_at: Optional[float] = None

@dataclass
class JobExecution:

    job_id: str

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    worker_id: Optional[str] = None
    output: Optional[str] = None