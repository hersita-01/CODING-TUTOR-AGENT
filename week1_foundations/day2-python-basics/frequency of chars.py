#number of times char appears in a str
string=input("Enter a string:")
d={}
for i in string:
    if i not in d.keys():
        d[i]=string.count(i)
print(d)
        
