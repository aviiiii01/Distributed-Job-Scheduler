import threading
import time
import random
from models import JobStatus, JobExecution
from job_store import JobStore
from dispatcher import JobDispatcher

def execute_api_call(job_name):
    print(f"Executing API call for job: {job_name}...")
    time.sleep(random.randint(2, 5)) 
    if random.random() < 0.8: 
        return f"API call for {job_name} succeeded."
    else:
        raise ConnectionError(f"API call for {job_name} failed.")

def execute_script(job_name):
    print(f"Executing script for job: {job_name}...")
    time.sleep(random.randint(3, 7)) 
    if random.random() < 0.9:
        return f"Script {job_name} completed successfully."
    else:
        raise ValueError(f"Script {job_name} failed with an error.")


COMMAND_MAP = {
    "api_call": execute_api_call,
    "run_script": execute_script,
}



class Worker(threading.Thread):
    def __init__(self, worker_id: str, job_store: JobStore, dispatcher: JobDispatcher):
        super().__init__()
        self.worker_id = worker_id
        self.job_store = job_store
        self.dispatcher = dispatcher
        self.daemon = True 
        self.running = True

    def run(self):
        print(f"[Worker-{self.worker_id}] Starting...")
        while self.running:
            job_id = self.dispatcher.get_job()
            if job_id:
                self.process_job(job_id)
            else:
               
                time.sleep(1)
    
    def stop(self):
        self.running = False

    def process_job(self, job_id: str):
        job = self.job_store.get_job(job_id)
        if not job:
            print(f"[Worker-{self.worker_id}] ERROR: Job {job_id} not found.")
            return

        print(f"[Worker-{self.worker_id}] Picked up job: {job.name} ({job_id})")

        execution = JobExecution(job_id=job_id, worker_id=self.worker_id)
        self.job_store.add_execution(execution)
        
        retries = job.retry_policy.max_retries
        for attempt in range(retries + 1):
            try:
                execution.start_time = time.time()
                execution.status = JobStatus.RUNNING
                self.job_store.update_execution(execution)

                command_func = COMMAND_MAP.get(job.command)
                if not command_func:
                    raise ValueError(f"Command '{job.command}' not found.")

                output = command_func(job.name)

                execution.status = JobStatus.SUCCESS
                execution.output = output
                print(f"[Worker-{self.worker_id}] Job {job.name} SUCCEEDED.")
                break 

            except Exception as e:
                print(f"[Worker-{self.worker_id}] Job {job.name} FAILED on attempt {attempt + 1}. Error: {e}")
                execution.status = JobStatus.FAILED
                execution.output = str(e)
                if attempt >= retries:
                    print(f"[Worker-{self.worker_id}] Job {job.name} has no retries left.")
                    break
                else:
                    time.sleep(2) 

        execution.end_time = time.time()
        self.job_store.update_execution(execution)