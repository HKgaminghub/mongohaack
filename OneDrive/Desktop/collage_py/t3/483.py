f=open("mbox-short.txt")
d={}
flag=0
for i in f.read().split():
    if flag:
        d[i]=d.get(i,0)+1
    if i=="From":
        flag=1
    else:
        flag=0
print(d)
max=sorted(d.items(),key=lambda x:x[1])[-1]
print(max)
