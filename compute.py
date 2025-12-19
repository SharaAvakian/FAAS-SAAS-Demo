import sys
import time

def compute(operation, num1, num2):
    time.sleep(0.5)
    
    a = float(num1)
    b = float(num2)
    
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            return "Error: Division by zero"
        return a / b
    elif operation == 'power':
        return a ** b
    else:
        return "Error: Unknown operation"

if __name__ == "__main__":
    operation = sys.argv[1]
    num1 = sys.argv[2]
    num2 = sys.argv[3]
    
    result = compute(operation, num1, num2)
    
    print(result)