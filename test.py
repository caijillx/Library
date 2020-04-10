# 导入库，正则匹配需要
import re

# 定义符数组
input = ['input1.txt','input2.txt','input3.txt','input4.txt','input5.txt']
output = ['output1.txt','output2.txt','output3.txt','output4.txt','output5.txt']
dingyi = ['var', 'const', 'procedure']
# 计数字典
count = {}
# 程序分割后的语句
yuju = []
# 标识符存储数组
bianliang = []
# 存储语句的数组
a = []
for i in range(0,5):
    count = {}
    # 程序分割后的语句
    yuju = []
    # 标识符存储数组
    bianliang = []
    # 读文件操作
    with open(input[i]) as f:
        # 将字符全部转为小写
        content = f.read().lower().split('\n')
        print(content)
        for c in content:
            #print(c)
            c = c.strip()
            #print(c)
            # 去除注释
            if len(c) != 0:
                if c[0] == '{':
                    continue
                # 判断字符串定义
                if c[0:3] == 'var' or c[0:5] == 'const' or c[0:9] == 'procedure':
                    if 'var' in c:
                        c = c.replace('var ', '')
                    if 'const' in c:
                        c = c.replace('const ', '')
                    elif 'procedure' in c:
                        c = c.replace('procedure', '')
                    c.replace(' ', '')
                    con = c.split(',')
                    for cd in con:
                        x = cd.split('=')
                        count[x[0].rstrip(";").replace(' ', '')] = 0
                        # 存储字符串
                        bianliang.append(x[0].rstrip(";").replace(' ', ''))
        #print(bianliang)

        for c in content:
            # 去除字符左右两边的空格
            c = c.strip()
            if len(c) != 0:
                # 去除注释
                if c[0] == '{':
                    continue
                for b in bianliang:
                    # 正则匹配  [^a-z]为非字母
                    matchObj = re.match(r'.*[^a-z]' + b + '[^a-z^0-9]', c, re.M | re.I)
                    a = -1
                    while matchObj:
                        count[b] = count[b] + 1
                        a = matchObj.end() - 2
                        matchObj = re.match(r'.*[^a-z]' + b + '[^a-z^0-9]', c[:matchObj.end() - 2], re.M | re.I)
                    matchObj = re.match(r'' + b + '[^a-z^0-9]', c[:a], re.M | re.I)
                    while matchObj:
                        count[b] = count[b] + 1
                        matchObj = re.match(r'' + b + '[^a-z^0-9]', c[:matchObj.end() - 2], re.M | re.I)
    # 写入文件操作
    with open(output[i], 'w') as f:
        for i in bianliang:
            f.write("(" + i + ":\t" + str(count[i]) + ")\n")