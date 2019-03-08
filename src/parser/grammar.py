file = open("parser_final.py","r")

text = file.read()
outfile = open("grammar","w+")
# text = text.strip("")
print(len(text))

i=0
while i<len(text):
    if text[i]=="#" and text[i+1]==" " and text[i+2]=="-":
        while text[i] is not "\n":
            outfile.write(text[i])
            i+=1
        outfile.write("\n")
    if text[i]=="'" and text[i+1]=="'" and text[i+2]=="'":
        i+= 3
        start = i
        while (i+2)<len(text):
            if (text[i]=="'" and text[i+1]=="'" and text[i+2]=="'"):
                break
            i+=1
        end = i
        i+=3
        outfile.write(text[start:end])
        outfile.write("\n")
        print(text[start:end])
    else:
        i+=1