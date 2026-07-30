num1 = float(input("Enter First Number: "))
oper = input("Choose an operation (+, -, *, /, %): ")
num2 = float(input("Enter Second Number: "))

if oper == "+":
    result = num1 + num2
    print(num1, "+", num2, "=", result)

elif oper == "-":
    result = num1 - num2
    print(num1, "-", num2, "=", result)

elif oper == "*":
    result = num1 * num2
    print(num1, "*", num2, "=", result)

elif oper == "/":
    if num2 != 0:
        result = num1 / num2
        print(num1, "/", num2, "=", result)
    else:
        print("Can't Divide by Zero")

elif oper == "%":
    result = num1 % num2
    print(num1, "%", num2, "=", result)

else:
    print("Invalid Operation")
   
