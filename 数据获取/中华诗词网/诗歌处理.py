import re
import chardet
texts = open('zgsg5.txt', 'r', encoding='utf-8', errors='ignore')
newt = open('modern.txt', 'a', encoding='utf-8')
lines = texts.readlines()

for line in lines:
    if len(line) < 4 or re.search(r'[a-zA-Z0-9/(●)<>〈•〉"”“‘’\'（：）■【】《》◎]', line) or re.search('作者', line) or len(re.findall(r'[\u4E00-\u9FFF]', line)) < 3:
        print(line)
    else:
        newt.write(line.lstrip())


# for i in range(1, len(lines)-1):
#     if lines[i-1] == '\n' and lines[i+1] == '\n':
#         l = [lines[i].rstrip('\n')]
#         i+=1
#         while not(lines[i-1] == '\n' and lines[i+1] == '\n') and i<len(lines):
#             if lines[i] != '\n' and lines[i] !='':
#                 l.append(lines[i].rstrip('\n'))
#             i+=1
#         if len(l)>3:
#             newt.write(l[0]+':')
#             l = l[1:]
#             for x in l:

#             newt.write('\n')
#             print(l)

newt.close()
texts.close()
