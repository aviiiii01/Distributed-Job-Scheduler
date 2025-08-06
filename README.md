# Distributed-Job-Scheduler
Design a system that can schedule and execute a large number of user-defined jobs. Each job should have the following properties
This project implements a distributed job scheduling system in Python as per the assignment requirements. It is designed to be a simulation running within a single process, using threads to represent different components like the scheduler, workers, and the API server. This approach fulfills the requirements while avoiding the complexity of actual network communication.

System Architecture
The system is composed of several key components that work together:

Job Store (JobStore): This is a thread-safe, in-memory data store for all job definitions and their execution histories. It acts as the single source of truth for the entire system.

Scheduler (Scheduler): The brain of the system. It runs in a background thread, periodically scanning all jobs. For each job, it checks if its cron schedule is due and if all its dependencies have been met. If so, it places the job into the appropriate priority queue for execution.

Dispatcher (JobDispatcher): A set of priority queues (High, Medium, Low). The Scheduler places ready-to-run jobs here, and Workers pick them up. This ensures that high-priority jobs are executed before lower-priority ones.

Worker (Worker): Represents a worker machine in the cluster. Each worker runs in its own thread, continuously polling the Dispatcher for jobs. When a job is received, the worker executes it, handles the retry logic on failure, and updates the Job Store with the final status.

API Server (api.py): A simple Flask-based web server that exposes a RESTful API. This allows users to add, view, modify, and delete jobs, as well as check their execution status.

Data Models (models.py): Defines the core data structures for Job, JobExecution, Priority, and JobStatus.

How it Works (Execution Flow)
A user defines a job (with its schedule, command, priority, etc.) by sending a POST request to the API server.

The API server validates the data and saves the new job definition in the JobStore.

The Scheduler thread periodically scans the JobStore.

It finds a job whose schedule is due (using the croniter library).

It then checks the job's dependencies by looking at the execution history in the JobStore. A dependency is considered met if it has at least one SUCCESS record.

If all conditions are met, the Scheduler puts the job ID into the JobDispatcher's queue corresponding to the job's priority.

An idle Worker thread pulls the job ID from the JobDispatcher (checking High, then Medium, then Low priority queues).

The Worker updates the job's status to RUNNING in the JobStore.

It simulates executing the job's command. If the job fails, the worker will retry according to the job's retry_policy.

Upon completion (either SUCCESS or final FAILED), the Worker updates the execution record in the JobStore with the final status.

The user can query the API at any time to see the status of their jobs.

File Structure
Here are the individual files for the project.

models.py

job_store.py

dispatcher.py

worker.py

scheduler.py

api.py

main.py

requirements.txt
