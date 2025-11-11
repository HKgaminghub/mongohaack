#wap to given number between 0-1000 in words 
d={0:"",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"ninteen",20:"twenty",30:"thirty",40:"fourty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninty",100:"hundred"}

n=input("Enter the number")
if int(n)>=100:
    if n[-2]=="1":
        print(d.get(int(n[-3])),end=" ")
        print(d.get(int(100)),end=" ")
        print(d.get(int(n[-2:])))
    else:
        print(d.get(int(n[-3])),end=" ")
        print(d.get(int(100)),end=" ")
        print(d.get(int(n[-2]+"0")),end=" ")
        print(d.get(int(n[-1])),end=" ")
elif int(n)>=10:
    if n[-2]=="1":
        print(d.get(int(n[-2:])),end=" ")
    else:
        print(d.get(int(n[-2]+"0")),end=" ")
        print(d.get(int(n[-1])),end=" ")
else:
    print(d.get(int(n)),end=" ")

