# # s1=">"
# # s2="CBA"
# # print("Hello".join("ABC"))

# # import string
# # s="!hi. wh?at is the weat[h]er"
# # print(s.translate(s.maketrans("","",string.punctuation)))
# # print(string.ascii_letters)

# s="This is Python"
# print(s.strip("Tihps ytPno"))

# t=("HEllo",)
# print(type(t),len(t))

# print(("apple","banana","mango")>("apple","mango",2))
# print()

# ()
# (3,5,7,9)
# (1,2,3,4,5,6,7,8)
# (6,5,4,3)
# (9,8,7,6,5)

# t=tuple(range(1,11))
# print((t[-1:-5]))
# print((t[2::2]))
# print((t[:-2:1]))
# print((t[-5:1:-1]))
# print((t[-2:-7:-1]))

# t=(1,2,3,4,5,"Appl")
# print(min(t))
t=(1,2,3,4,5)
for i,j in enumerate(t):
    print(i,j)