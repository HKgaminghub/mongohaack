#wriet a program to check if two string entered by users are balanced or not.
# For example s1 and s2 are balnced if all the character in s1 are present s2

s1=input("Enter the string s1 :")
s2=input("Enter the string s2 :")


for i in s1:
    if i in s2:
        continue
    else:
        print("Not balanced")
        break
else:
    print("Balanced")