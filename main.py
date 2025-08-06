import time
from job_store import JobStore
from dispatcher import JobDispatcher
from scheduler import Scheduler
from worker import Worker
from api import create_api_server
from models import Job, Priority

def main():
    job_store = JobStore()
    dispatcher = JobDispatcher()
    print("--- Seeding initial jobs ---")
    

    job1 = Job(name="Critical API Health Check", schedule="* * * * *", command="api_call", priority=Priority.HIGH)
    job_store.add_job(job1)
    print(f"Added Job: {job1.name} (ID: {job1.id})")
    

    job2 = Job(name="Daily Report Generation", schedule="* * * * *", command="run_script", priority=Priority.MEDIUM, dependencies=[job1.id])
    job_store.add_job(job2)
    print(f"Added Job: {job2.name} (ID: {job2.id}), depends on {job1.id}")

    job3 = Job(name="Log Archiving", schedule="*/2 * * * *", command="run_script", priority=Priority.LOW)
    job_store.add_job(job3)
    print(f"Added Job: {job3.name} (ID: {job3.id})")
    
    print("----------------------------")

    scheduler = Scheduler(job_store, dispatcher)
    scheduler.start()

    num_workers = 3
    workers = []
    for i in range(num_workers):
        worker = Worker(worker_id=f"W{i+1}", job_store=job_store, dispatcher=dispatcher)
        worker.start()
        workers.append(worker)

    app = create_api_server(job_store)
    print("API Server starting on http://127.0.0.1:5000")
    print("Use Ctrl+C to stop the system.")

    app.run(host='0.0.0.0', port=5000)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- Shutting down ---")
        scheduler.stop()
        for worker in workers:
            worker.stop()
        
        scheduler.join()
        for worker in workers:
            worker.join()
        print("System stopped.")


if __name__ == "__main__":
    main()