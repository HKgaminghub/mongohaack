#Wap to create a dic which gives me intial of a word as key and number of words strating form the intial from the given strings

s="this is a lecture of python and it is morning"
l=s.split()
d={}
for i in l:
    if i[0] in d:
        d[i[0]]+=1
    else:
        d[i[0]]=1

print(d) 
print(dict(sorted(d.items(),key=lambda x:x[1],reverse=True)))