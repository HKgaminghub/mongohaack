msg=input("Enter the message: ")
key = int(input("Enter the Key: "))
enc=""
j=0
for i in range(key):
    while True:
        if j>=len(msg):
            break
        enc+=msg[j]
        j+=key
    j=i+1

print(enc)

d=len(enc)//key
t=0
h=len(enc)%key
dec=""
part1=enc[:(d+1)*h]
part2=enc[(d+1)*h:]
for i in range(d+1):
    if i<d:
        dec+=part1[i::d+1]+part2[i::d]
    else:
        dec+=part1[i::d+1]
print(part1)
print(part2)
print(dec)