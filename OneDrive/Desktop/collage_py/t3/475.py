f = open("pager.txt","r",encoding='utf-8')
count=1
for i in f.readlines():
    print(i,end="")
    if count%25==0:
        e=input()
        if e.lower()=="e":
            break
    count+=1