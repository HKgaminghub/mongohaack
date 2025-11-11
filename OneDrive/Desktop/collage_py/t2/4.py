# #WAP to find longest common prefix from given list of string 

l = ["less","lesson","lessonplan"]
# a=[]
# b=[]
# j=0
# while True:
#     # print(j)
#     if j==-1:
#         break
#     b=a.copy()
#     a=[]
#     for i in l:
#         a.append(i[0:j+1])
#         if i[j]=="":
#             j=-2
#             break
#     for i in a:
#         if i==a[0]:
#             pass
#         else:
#             j=-2
#             break
#     j+=1
# if len(b)==0:
#     print("-1")
# else:
#     print(b[0])

l.sort()
ans=""
for i in range(min(len(l[0]),len(l[-1]))):
    if l[0][0:i+1]==l[-1][0:i+1]:
        ans=l[0][0:i+1]
    else:
        break

if ans=="":
    print(-1)
else:
    print(ans)