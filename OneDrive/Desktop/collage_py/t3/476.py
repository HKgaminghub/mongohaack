f1=open("file1.txt")
fr=open("rev.txt","w")
frc=open("cap.txt","w")
fr.write(f1.read()[::-1])
f1.seek(0)
frc.write(f1.read()[::-1].upper())
frc.seek(0)
volvel=0
frc=open("cap.txt")
for i in frc.read():
    if i in ["A","E","I","O","U"]:
        volvel+=1
frc.seek(0)
print("Vovel=",volvel)
print("Second line",frc.readlines()[1])