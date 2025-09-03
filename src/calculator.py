""" 
Este archivo controla el programa principal, recibe la entrada del usuario
y dirige a la operacion. 
"""
from src import operations

def calculate(operation, a, b):
    if operation == "+":
        return operations.add(a, b)
    elif operation == "-":
        return operations.subtract(a, b)
    elif operation == "*":
        return operations.multiply(a, b)
    elif operation == "/":
        return operations.divide(a, b)
    else:
        return "Invalid operation"