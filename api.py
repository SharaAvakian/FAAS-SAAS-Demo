import json
import time
import os
import logging

logging.basicConfig(filename='faas_saas.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobAPI:
    def __init__(self):
        os.makedirs('jobs', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        logging.info("JobAPI initialized")
    
    def submit_job(self, operation, num1, num2):
        job_id = "job_" + str(int(time.time())) + "_" + os.urandom(4).hex()
        
        try:
            a = float(num1)
            b = float(num2)
        except:
            logging.error("Invalid input for job " + job_id + ": num1=" + str(num1) + ", num2=" + str(num2))
            return {"error": "Invalid numbers"}
        
        job_data = {
            "job_id": job_id,
            "operation": operation,
            "num1": a,
            "num2": b,
            "status": "queued",
            "submitted_at": time.time()
        }
        
        with open('jobs/' + job_id + '.json', 'w') as f:
            json.dump(job_data, f)
        
        logging.info("Job submitted: " + job_id + " - " + operation + " " + str(a) + " " + str(b))
        print("Job submitted: " + job_id)
        return {"job_id": job_id, "status": "queued"}
    
    def get_result(self, job_id):
        result_file = 'results/' + job_id + '.json'
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                result = json.load(f)
            logging.info("Result retrieved for job " + job_id)
            return result
        
        job_file = 'jobs/' + job_id + '.json'
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                result = json.load(f)
            logging.info("Job " + job_id + " still in queue")
            return result
        
        logging.warning("Job " + job_id + " not found")
        return {"error": "Job not found"}