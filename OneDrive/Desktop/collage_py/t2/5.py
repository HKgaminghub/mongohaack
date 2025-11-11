#given a list L of size and you need to count number of special elemts in the given list an 
#elemtes is specials if that removal of the element make the list the balance. the list is 
#balance if the sum of even index element is equal to sum of odd index element

l=[2,1,6,4]
sp=[]
for i in range(len(l)):
    p=l.copy()
    p.pop(i)
    pe=p[0::2]
    po=p[1::2]
    if sum(pe)==sum(po):
        sp.append(i)

print(sp)
