import json
import os
import time
import subprocess
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

logging.basicConfig(filename='faas_saas.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_single_job(job_path):
    with open(job_path, 'r') as f:
        job_data = json.load(f)
    
    job_id = job_data['job_id']
    
    job_data['status'] = 'processing'
    job_data['started_at'] = time.time()
    with open(job_path, 'w') as f:
        json.dump(job_data, f)
    
    logging.info("Processing job: " + job_id)
    print("PROCESSING: " + job_id)
    
    start_time = time.time()
    result = subprocess.run(
        ['/home/shara/Desktop/faas-saas-demo/venv/bin/python', 'compute.py', 
         job_data['operation'], 
         str(job_data['num1']), 
         str(job_data['num2'])],
        capture_output=True,
        text=True
    )
    execution_time = (time.time() - start_time) * 1000
    wait_time = (start_time - job_data['submitted_at']) * 1000
    
    result_data = {
        "job_id": job_id,
        "operation": job_data['operation'],
        "num1": job_data['num1'],
        "num2": job_data['num2'],
        "result": result.stdout.strip(),
        "status": "completed",
        "submitted_at": job_data['submitted_at'],
        "started_at": job_data['started_at'],
        "completed_at": time.time(),
        "wait_time_ms": round(wait_time, 2),
        "execution_time_ms": round(execution_time, 2),
        "total_time_ms": round(wait_time + execution_time, 2)
    }
    
    with open('results/' + job_id + '.json', 'w') as f:
        json.dump(result_data, f)
    
    os.remove(job_path)
    logging.info("Completed job: " + job_id + " - wait " + str(round(wait_time)) + "ms, exec " + str(round(execution_time)) + "ms")
    print("COMPLETED: " + job_id + " (waited " + str(round(wait_time)) + "ms, ran " + str(round(execution_time)) + "ms)")
    
    return result_data

class QueueManager:
    def __init__(self, max_workers=3):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
        self.active_jobs = []
        logging.info("QueueManager initialized with " + str(max_workers) + " workers")
    
    def get_queue_info(self):
        queued = []
        processing = []
        
        if os.path.exists('jobs'):
            for filename in os.listdir('jobs'):
                if filename.endswith('.json'):
                    with open('jobs/' + filename, 'r') as f:
                        job = json.load(f)
                        if job['status'] == 'queued':
                            queued.append(job['job_id'])
                        elif job['status'] == 'processing':
                            processing.append(job['job_id'])
        
        return {
            'max_workers': self.max_workers,
            'queued_count': len(queued),
            'processing_count': len(processing),
            'queued_jobs': queued,
            'processing_jobs': processing
        }
    
    def process_jobs(self):
        if not os.path.exists('jobs'):
            return
        
        job_files = []
        for f in os.listdir('jobs'):
            if f.endswith('.json'):
                job_files.append('jobs/' + f)
        
        if not job_files:
            return
        
        logging.info("Processing " + str(len(job_files)) + " jobs with " + str(self.max_workers) + " workers")
        print("\nQUEUE STATUS: " + str(len(job_files)) + " jobs waiting, " + str(self.max_workers) + " workers available")
        
        futures = []
        for i in range(min(len(job_files), self.max_workers)):
            job_file = job_files[i]
            future = self.executor.submit(process_single_job, job_file)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error("Error processing job: " + str(e))
                print("Error: " + str(e))
    
    def run_forever(self):
        logging.info("Queue manager started")
        print("Queue manager started with " + str(self.max_workers) + " parallel workers")
        print("Watching for jobs...\n")
        while True:
            self.process_jobs()
            time.sleep(0.5)

if __name__ == "__main__":
    manager = QueueManager(max_workers=3)
    manager.run_forever()