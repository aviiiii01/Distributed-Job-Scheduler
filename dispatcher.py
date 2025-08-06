from queue import Queue
from typing import Optional
from models import Priority

class JobDispatcher:
    """Dispatches jobs to workers via priority queues."""
    def __init__(self):
        self.queues = {
            Priority.HIGH: Queue(),
            Priority.MEDIUM: Queue(),
            Priority.LOW: Queue()
        }
        self.priority_order = [Priority.HIGH, Priority.MEDIUM, Priority.LOW]

    def dispatch_job(self, job_id: str, priority: Priority):
        """Adds a job_id to the appropriate priority queue."""
        self.queues[priority].put(job_id)
        print(f"[Dispatcher] Job {job_id} queued with {priority} priority.")

    def get_job(self) -> Optional[str]:
        """
        Gets a job_id from the highest-priority queue that is not empty.
        This is a blocking operation (by default, but we use a short timeout).
        """
        for priority in self.priority_order:
            if not self.queues[priority].empty():
                return self.queues[priority].get()
        return None