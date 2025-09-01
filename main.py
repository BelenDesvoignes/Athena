def main():
   
    print("Inicio de calculadora ")

from src import calculator

if __name__ == "__main__":
    num = float(input("Enter a number: "))
    other_num = float(input("Enter another number: "))
    operation = input("Enter an operation (+,-,*,/ ): ")
    result = calculator.calculate(operation, num, other_num)
    print(result)