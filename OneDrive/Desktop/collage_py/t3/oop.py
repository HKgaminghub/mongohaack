class Name:
    def __init__(self):
        print("I am created")
    def fun(self,a):
        self.name="Hard"
        print(self.name)
    def display(self):
        print(self.name)
n=Name()
n.fun(57)