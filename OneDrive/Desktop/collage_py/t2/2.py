#wap to create ceasor cipher encription

s=input("Enter the string: ")
key=int(input("Enter the key"))
e=input("Enter the method encription or decription")
for i in s:
    if ord(i)>=97 and ord(i)<=122:
        if e=="e":
            value=key+ord(i)
            if value>122:
                value-=26
            print(chr(value),end="")

            continue
        else:
            value=ord(i)-key
            if value<97:
                value+=26
            print(chr(value),end="")
            continue
    elif ord(i)>=65 and ord(i)<=90:
        if e=="e":
            value=key+ord(i)
            if value>90:
                value-=26
            print(chr(value),end="")

            continue
        else:
            value=ord(i)-key
            if value<65:
                value+=26
            print(chr(value),end="")
            continue
    else:
        print(i,end="")

