from flask import Flask, request, jsonify
from models import Job, Priority, RetryPolicy, JobStatus
from job_store import JobStore

def create_api_server(job_store: JobStore):
    app = Flask(__name__)

    @app.route('/jobs', methods=['POST'])
    def add_job():
        data = request.get_json()
        if not data or 'name' not in data or 'schedule' not in data or 'command' not in data:
            return jsonify({"error": "Missing required fields: name, schedule, command"}), 400
        
        try:
            job = Job(
                name=data['name'],
                schedule=data['schedule'],
                command=data['command'],
                priority=Priority(data.get('priority', 'MEDIUM')),
                dependencies=data.get('dependencies', []),
                retry_policy=RetryPolicy(max_retries=data.get('retries', 3))
            )
            job_store.add_job(job)
            return jsonify({"message": "Job added successfully", "job_id": job.id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/jobs', methods=['GET'])
    def get_all_jobs():
        jobs = job_store.get_all_jobs()
        return jsonify([job.__dict__ for job in jobs])

    @app.route('/jobs/<job_id>', methods=['GET'])
    def get_job(job_id):
        job = job_store.get_job(job_id)
        if job:
            return jsonify(job.__dict__)
        return jsonify({"error": "Job not found"}), 404

    @app.route('/jobs/<job_id>/status', methods=['GET'])
    def get_job_status(job_id):
        executions = job_store.get_job_executions(job_id)
        if not job_store.get_job(job_id):
             return jsonify({"error": "Job not found"}), 404
        return jsonify([ex.__dict__ for ex in executions])

    @app.route('/jobs/<job_id>', methods=['DELETE'])
    def delete_job(job_id):
        if job_store.delete_job(job_id):
            return jsonify({"message": "Job deleted successfully"}), 200
        return jsonify({"error": "Job not found"}), 404

    return app