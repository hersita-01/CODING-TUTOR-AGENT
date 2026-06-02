def insert(author):
    pos=int(input("Enter the position of the author's name to be inserted: "))
    if (pos-1)>len(author):
        print("The position of insertion is invalid ")
    else:
        new=input("Enter the author's name to be inserted: ")
        if new not in author:
            author.insert(pos-1,new)
        else:
            print("The name of the author already exists ")

def update(author):
    upd=input("Enter the author's name to be updated : ")
    if search(author,upd)!= (-9999):
        updated=input("Enter the updated author's name :")
        author[author.index(upd)]=updated
    else:
        print("The author's name to be updated is invalid ")

def search(author,x):
    for i in range (0,len(author)):
        if author[i]==x:
            position=i
            return position+1
    else:
        return -9999
            
def delete(author,x):
    if search(author,x)!=(-9999):
        author.remove(x)
    else:
        print("The author's name to be deleted is invalid ")

def display(author):
    print(author)
    
author=[]
while True:
    ch=int(input(" Menu options\n 1.Insert \n 2.Update \n 3.Delete \n 4.Search \n 5.Display \n 6.Exit\n Enter your choice :"))
    if ch==1:
        insert(author)
    elif ch==2:
        update(author)
    elif ch==3:
        p=input("Enter the name of the author to be deleted: ")
        delete(author,p)
    elif ch==4:
        x=input("Enter the name of the author to be searched: ")
        ret=search(author,x)
        if ret>0:
            print("The position of the searched author name is:" ,ret)
        else:
            print("The name of the author is not present ")
    elif ch==5:
        display(author)
    else:
        exit(0)
