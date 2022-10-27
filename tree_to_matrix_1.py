from codeop import Compile
from operator import index
import numpy as np
import pandas as pd
import re
import argparse

parser = argparse.ArgumentParser(description='tree with nwk to matrix ')
parser.add_argument("-n","--nwk",)
parser.add_argument("-path","--path",)
args = parser.parse_args()
file1 = args.nwk
path= args.path

#find，find1 字符串中找出所有指定元素索引
def find(string, char,char1): 
    for i, c in enumerate(string):
        if c == char or c==char1:
            yield i

def find1(string, char):
    for i, c in enumerate(string):
        if c == char:
            yield i

def toupu():
    with open(file1) as f:
        contents = f.read().strip()
        comp1 = re.compile(r'XP_\d+\.\d?')  #nwk序列名称
        comp2 = re.compile(r'\(|\)')            #括号
        comp3 = re.compile(r'\.\d:\d\.\d+')         #序列支长
        comp4 = re.compile(r'\).?\.?\d*:\d\.\d+')    #节点支长
        XP = comp1.findall(contents)
        XP_xiabiao = [contents.find(i) for i in XP]
        kuohao_xiaobiao = list(find(contents,"(",")"))
        kuohao = comp2.findall(contents)
        xP_dist = ["%.2f"%float(i.split(":")[1]) for i in comp3.findall(contents)] #  XP本身支长
        XP_dist = [float(i) for i in xP_dist]
        zk = 0  #左括号
        yk = 0  #右括号
        tree = {}
        for i in range(len(kuohao)):
            if kuohao[i]=="(":
                zk+=1
            if kuohao[i] == ")":
                yk+=1
            if zk-yk==1 and i!=0 and i!=len(kuohao)-2:
                A=i   
        two = kuohao_xiaobiao[A]#二叉树 第一层节点索引 
        cengshu = [contents[:i].count("(")-contents[:i].count(")") if i <two else contents[two+1:i].count("(")-contents[two+1:i].count(")") for i in XP_xiabiao ]  叶子节点层数
        j1=0
        for j in XP_xiabiao:
            z1 = list(find1(contents,"("))
            y1 = list(find1(contents,")"))
            t1 = list(find(contents,"(",")"))
            if j< two:
                z = [s1 for s1 in z1 if s1<j]
                y = [s2 for s2 in y1 if s2>j and s2<=two]
                yt = [s4 for s4 in t1 if s4>j and s4<=two]
            else:
                z = [s1 for s1 in z1 if s1<j and s1>two]
                y = [s2 for s2 in y1 if s2>j]
                yt = [s4 for s4 in t1 if s4>j]
            flag1 = 1
            flag2 = 1
            yzk = []
            yyk =[]
            value = []
            L=len(z) #左边括号数量
            L3=0
            for kh in yt:
                v = 1
                L2 = yt.index(kh)           #右边第一个括号下标
                if kh in y and L2==0:              #支的第一个右括号
                    v = float("%.2f"%float(comp4.findall(contents[kh:])[0].split(":")[1]))
                    L3+=1                        #该位点匹配成功一次+1，用来算该支长的层数
                    L-=1                      # 左边括号-1，层数（深度-1）
                else:
                    if kh not in y:
                        flag1+=1
                        yzk.append(kh)
                    else:
                        flag2+=1
                        yyk.append(kh)
                    if flag2-flag1 <= L and flag2-flag1>0:
                        if len(yzk)==0 and L>= L2+1:
                            if len(comp4.findall(contents[kh:]))!=0:
                                v = float("%.2f"%float((comp4.findall(contents[kh:])[0].split(":")[1])))
                                #value.append("%.2f"%float(comp4.findall(contents[kh:])[0].split(":")[1]))
                                L3+=1
                        else:
                            L4 = L2-L3
                            if L4==2*len(yzk) and kh in y :
                                #print(comp4.findall(contents[kh:]))
                                if len(comp4.findall(contents[kh:]))!=0:
                                    v = float("%.2f"%float(comp4.findall(contents[kh:])[0].split(":")[1]))
                                    L3+=1
                if v<1:  #支长小于1
                    value.append(v)  #叶子节点的逐级父节点支长
            va= [cengshu[j1],XP_dist[j1],value,sum(value)]
            tree[XP[j1]]= va
            j1+=1

        y =  XP + ["rank"]
        mat1 = np.zeros([len(XP),len(y)])
        table = pd.DataFrame(mat1,columns = y,index=XP)
        row_name = list(table.index)
        col_name = list(table)
        for r in range(len(row_name)):
            cs = tree[row_name[r]][0]
            table.loc[row_name[r],"rank"] = tree[row_name[r]][0]
            for c in range(r,len(col_name)-1):
                b = sorted([contents.find(row_name[r]),contents.find(col_name[c]),two])
                r_self = tree[row_name[r]][1]
                c_self = tree[col_name[c]][1]
                if row_name[r]==col_name[c]:
                    table.iloc[r,c]=0
                else:
                    if b.index(two)==1: #二叉树两端判断
                        r_v = tree[row_name[r]][-1]
                        c_v = tree[col_name[c]][-1]
                        table.iloc[r,c] = "%.2f"%float(r_v+c_v+r_self+c_self)
                        table.iloc[c,r] = "%.2f"%float(r_v+c_v+r_self+c_self)
                    else:
                        xx = tree[row_name[r]][-2][::-1]
                        xxx = tree[col_name[c]][-2][::-1]
                        x1 = [x for x in range(len(xx)) for y in range(len(xxx)) if x==y and xx[x] == xxx[y]]#找出两序列最近的父节点
                        if len(x1)!=0:x2 = len(x1)
                        else:x2 = 0
                        if x2!=0:
                            father = sum(tree[row_name[r]][-2][:-x2])
                            f2 = sum(tree[col_name[c]][-2][:-x2])
                        else:
                            father = sum(tree[row_name[r]][-2])
                            f2 = sum(tree[col_name[c]][-2])
                        table.iloc[r,c] = "%.2f"%float(father+r_self+c_self+f2)
                        table.iloc[c,r] = "%.2f"%float(father+r_self+c_self+f2)
        table.to_csv(root)
toupu()
