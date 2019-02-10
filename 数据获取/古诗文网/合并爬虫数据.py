file1 = open('gsww_1001.txt', encoding='utf-8')
file2 = open('gsww_all.txt', encoding='utf-8')
file_new = open('gsww.txt', 'a', encoding='utf-8')
set1 = set(i for i in file1)
set2 = set(j for j in file2)
set_new = set1.union(set2)
for o in set_new:
    file_new.write(o)
