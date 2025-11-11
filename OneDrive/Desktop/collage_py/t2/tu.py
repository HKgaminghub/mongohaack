# WAP to find maximum even number maximum odd number minmum even number and minimum odd number from a tuple of numbers

t=tuple(input("Enter a tuple: ").split())
maxe=None
mine=None
maxo=None
mino=None
for i in t:
    i=int(i)
    if i%2==0:
        if maxe==None or maxe<i:
            maxe=i
        if mine==None or mine>i:
            mine=i
    else:
        if maxo==None or maxo<i:
            maxo=i
        if mino==None or mino>i:
            mino=i


print(f"max even {maxe}")
print(f"max odd {maxo}")
print(f"min even {mine}")
print(f"min odd {mino}")