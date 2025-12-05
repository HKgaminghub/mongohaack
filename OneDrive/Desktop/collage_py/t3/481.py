f=open("481.txt","w+")
while True:
    i=input("Enter END to quit: ")
    if i.lower()=="end":
        break
    f.write(i+"\n")
f.seek(0)
for i in f.readlines():
    if i[0].isupper():
        print(i,end="")