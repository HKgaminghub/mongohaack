#WAP which will the sum of the number int the list except the number 13 and the number which comes imigiytly after 13 in a list 

l=list(eval(input("Enter the list")))
p=1
sum=0
for i in l:
    if i==13:
        p=0
    elif p:
        sum+=i
    else:
        p=1
print(sum)

# t_13=l.count(13)
# l1=l.copy()
# a=0
# index_13=[]
# for i in range(t_13):
#     ind=l1.index(13)
#     index_13.append(a+ind)
#     index_13.append(a+ind+1)
#     a+=1
#     l1.remove(13)
# sum=0
# for i in range(len(l)):
#     if i in index_13:
#         continue
#     sum+=l[i]
# print(sum)