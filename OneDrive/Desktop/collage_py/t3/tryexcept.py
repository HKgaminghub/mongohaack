a=8
import math
try:
    print(math.exp(1000)) 
except NameError:
    print("The error is about Name not defined")
except OverflowError:
    print("Error")
    