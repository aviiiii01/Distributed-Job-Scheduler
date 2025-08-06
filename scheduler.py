import threading
import time
from croniter import croniter
from job_store import JobStore
from dispatcher import JobDispatcher

class Scheduler(threading.Thread):
    def __init__(self, job_store: JobStore, dispatcher: JobDispatcher, check_interval_seconds=10):
        super().__init__()
        self.job_store = job_store
        self.dispatcher = dispatcher
        self.check_interval = check_interval_seconds
        self.daemon = True
        self.running = True

    def run(self):
        print("[Scheduler] Starting...")
        while self.running:
            self.schedule_jobs()
            time.sleep(self.check_interval)
    
    def stop(self):
        self.running = False

    def schedule_jobs(self):
        print("[Scheduler] Checking for jobs to run...")
        now = time.time()
        all_jobs = self.job_store.get_all_jobs()

        for job in all_jobs:

            if not croniter.is_valid(job.schedule):
                print(f"[Scheduler] Job {job.name} has invalid cron schedule: {job.schedule}")
                continue


            base_time = job.last_triggered_at if job.last_triggered_at else now - 3600 
            cron = croniter(job.schedule, base_time)
            next_run_time = cron.get_next(float)
            
            if next_run_time > now:
                continue

            dependencies_met = True
            if job.dependencies:
                for dep_id in job.dependencies:
        
                    if not self.job_store.has_successful_execution(dep_id):
                        dependencies_met = False
                        print(f"[Scheduler] Job {job.name} waiting for dependency {dep_id} to succeed.")
                        break
            
            if dependencies_met:
                print(f"[Scheduler] Job {job.name} is due and dependencies are met. Dispatching.")
                job.last_triggered_at = now 
                self.dispatcher.dispatch_job(job.id, job.priority)