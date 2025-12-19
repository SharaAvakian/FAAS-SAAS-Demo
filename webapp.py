from flask import Flask, render_template, request, jsonify
from api import JobAPI
import os
import json
import logging

logging.basicConfig(filename='faas_saas.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
api = JobAPI()

@app.route('/')
def home():
    logging.info("Home page accessed")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    operation = data.get('operation')
    num1 = data.get('num1')
    num2 = data.get('num2')
    
    logging.info("Job submission request: " + str(operation) + " " + str(num1) + " " + str(num2))
    result = api.submit_job(operation, num1, num2)
    return jsonify(result)

@app.route('/result/<job_id>')
def get_result(job_id):
    logging.info("Result request for job " + job_id)
    result = api.get_result(job_id)
    return jsonify(result)

@app.route('/jobs')
def list_jobs():
    jobs = []
    
    if os.path.exists('results'):
        for filename in os.listdir('results'):
            if filename.endswith('.json'):
                with open('results/' + filename, 'r') as f:
                    jobs.append(json.load(f))
    
    if os.path.exists('jobs'):
        for filename in os.listdir('jobs'):
            if filename.endswith('.json'):
                with open('jobs/' + filename, 'r') as f:
                    jobs.append(json.load(f))
    
    jobs.sort(key=lambda x: x.get('submitted_at', 0), reverse=True)
    
    logging.info("Jobs list requested, returning " + str(len(jobs)) + " jobs")
    return jsonify(jobs)

@app.route('/queue-status')
def queue_status():
    queued = []
    processing = []
    completed_count = 0
    
    if os.path.exists('jobs'):
        for filename in os.listdir('jobs'):
            if filename.endswith('.json'):
                with open('jobs/' + filename, 'r') as f:
                    job = json.load(f)
                    if job['status'] == 'queued':
                        queued.append(job['job_id'])
                    elif job['status'] == 'processing':
                        processing.append(job['job_id'])
    
    if os.path.exists('results'):
        completed_files = []
        for f in os.listdir('results'):
            if f.endswith('.json'):
                completed_files.append(f)
        completed_count = len(completed_files)
    
    status = {
        'max_workers': 3,
        'queued': queued,
        'queued_count': len(queued),
        'processing': processing,
        'processing_count': len(processing),
        'completed_count': completed_count,
        'total_jobs': len(queued) + len(processing) + completed_count
    }
    logging.info("Queue status requested: " + str(status))
    return jsonify(status)

if __name__ == '__main__':
    logging.info("Starting FaaS/SaaS Web App")
    print("Starting FaaS/SaaS Web App on http://localhost:5000")
    print("Queue info shows scheduling and parallel execution proof!")
    app.run(debug=True, port=5000)