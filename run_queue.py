from queue_manager import QueueManager

if __name__ == "__main__":
    manager = QueueManager()
    manager.run_forever()