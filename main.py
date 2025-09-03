from src import calculator

def main():
    print("Inicio de calculadora ")


if __name__ == "__main__":
    num = float(input("Ingresa un numero: "))
    other_num = float(input("Ingresa otro numero: "))
    operation = input("Ingresa una operacion (+,-,*,/ ): ")
    result = calculator.calculate(operation, num, other_num)
    print(result)