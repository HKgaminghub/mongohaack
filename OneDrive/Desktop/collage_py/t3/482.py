f1=open("482.1.txt")
f2=open("482.2.txt")
l=1
c=0
for i,j in zip(f1.read(),f2.read()):
    c+=1
    if i==j:
        if i=="\n":
            l+=1
            c=0
    else:
        print(l,c)