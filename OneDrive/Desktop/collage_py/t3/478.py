f = open("478.txt")
for i in f:
    for j in i.split():
        if j[0].lower()=="i":
            print(j[::-1],end=" ")
        else:
            print(j,end=" ")
    print()