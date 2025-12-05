f1 = open("file1.txt")
f2 = open("file2.txt")
f3 = open("file3.txt","w+")

for i,j in zip(f1,f2):
    f3.write(i) 
    f3.write(j)
f1.close() 
f2.close() 
f3.seek(0)
print(f3.read())
f3.close()