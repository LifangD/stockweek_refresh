# -*- encoding:utf-8 -*-
'''
Created on 2017年11月6日

@author: Sally
'''
from jinja2 import Template
from WindPy import *
import pandas as pd
import xlrd
import matplotlib
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
w.start();

'''
上证 ：000001.SH
沪深：000300.SH
深圳成指：399001.SZ
创业板指：399006.SZ
申万交运：801170.SI
'''
code_index=['000001.SH','000300.SH','399001.SZ','399006.SZ','801170.SI']

code_sw1=['801010.SI',
'801020.SI',
'801030.SI',
'801040.SI',
'801050.SI',
'801080.SI',
'801110.SI',
'801120.SI',
'801130.SI',
'801140.SI',
'801150.SI',
'801160.SI',
'801170.SI',
'801180.SI',
'801200.SI',
'801210.SI',
'801230.SI',
'801710.SI',
'801720.SI',
'801730.SI',
'801740.SI',
'801750.SI',
'801760.SI',
'801770.SI',
'801780.SI',
'801790.SI',
'801880.SI',
'801890.SI'
]


'''
港口Ⅱ
公交Ⅱ
航空运输Ⅱ
机场Ⅱ
高速公路Ⅱ
航运Ⅱ
铁路运输Ⅱ
物流Ⅱ

'''
code_trans=['801171.SI', 
            '801172.SI',
            '801173.SI',
            '801174.SI',
            '801175.SI',
            '801176.SI',
            '801177.SI',
            '801178.SI'
            ]

# 获取一级行业与二级行业指数对应的编码 
def sw_industry():
    wsd_data=data=w.wset("SectorConstituent", u"date=20171113;sector=申银万国一级行业指数;field=wind_code,sec_name")  
    #wsd_data=data=w.wset("SectorConstituent", u"date=20171113;sector=申银万国二级行业指数;field=wind_code,sec_name")
    if wsd_data.ErrorCode != 0:
        print("Get Data failed! exit!")
        exit()
    fm=pd.DataFrame(wsd_data.Data,index=wsd_data.Fields)
    fm=fm.T #将矩阵转置
    print('fm:/n',fm)
    fm.to_excel("f:/sw_industry/class1.xlsx")
    #fm.to_excel("f:/sw_industry/class2.xlsx")
    
 
#获取涨跌幅，分别需要获取 大盘、交通板块、个股三类涨跌幅
def close_change(codes=[]):
    data=w.wsq(codes,"rt_pre_close,rt_pct_chg_5d,rt_pct_chg_ytd").Data #前收、5日涨幅、年初至今涨幅   
    return codes,data[0],data[1],data[2]

#  重组数据  
def pre_sort(arr1=[],arr2=[]):
    res={}
    for i in len(arr1):
        res.append(arr1[i])
        res.append(arr2[i])
    return res
    
#根据涨跌幅排序
def sort_change(arr):
    sorted_arr = sorted(arr.items(),key=lambda asd:asd[1],reverse=True)
    return sorted_arr

#取涨幅前五
def top_five(sorted_arr):
    top_five=[]
    for i in range(5):
        top_five.append(sorted_arr[i])
    return top_five
    
#曲跌幅前五
def bottom_five(sort_arr):
    bottom_five=[]
    for i in range(5):
        bottom_five.append(sort_arr[-i])
    return bottom_five


data = xlrd.open_workbook('f:/sw_industry.xlsx') 
#获取 大盘指数编号 与对应名称
def index_info():
    table = data.sheets()[0]
    nrows = table.nrows 
    code=[]
    name=[]
    for i in range(nrows):
        code.append(table.row(i)[0].value)
        name.append(table.row(i)[1].value)  
    return code,name
#一级分类
def class1_info():
    table = data.sheets()[1]
    nrows = table.nrows 
    code=[]
    name=[]
    for i in range(nrows):
        code.append(table.row(i)[0].value)
        name.append(table.row(i)[1].value)  
    return code,name 
# 二级分类
def class2_info():
    table = data.sheets()[2]
    nrows = table.nrows 
    code=[]
    name=[]
    for i in range(nrows):
        code.append(table.row(i)[0].value)
        name.append(table.row(i)[1].value)  
    return code,name 

#个股信息
def single_info():
    table = data.sheets()[3]
    nrows = table.nrows 
    code=[]
    name=[]
    for i in range(nrows):
        code.append(table.row(i)[0].value)
        name.append(table.row(i)[1].value)  
    return code,name 

def part_1(): 
    res=index_info() 
    codes=res[0]
    name=res[1]
    index=[]
    array= close_change(codes)
    for i in range(len(array[0])):
        index.append({"name":name[i],"close":array[1][i],"w_change":array[2][i]*100,"y_change":array[3][i]*100})
      
    return index

#获取 排序的板块
def sort_class(res):
    codes=res[0]
    name=res[1]
    c2_idry=[]
    array= close_change(codes)
    for i in range(len(array[0])):
        c2_idry.append([name[i],array[2][i]*100])
    c2_idry=sorted(c2_idry, key=lambda asd:asd[1], reverse = True) 
    return c2_idry

def draw_class2(c2):
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    c2_idry=sort_class(c2)
    class2_name=[]
    class2_change=[]
    for c2 in c2_idry:
        class2_name.append(c2[0])
        class2_change.append(c2[1])
    y_pos = np.arange(len(class2_name))
    bar_labels=class2_name
    x =class2_change
    plt.yticks(y_pos, bar_labels, fontsize=10,fontproperties=zhfont1)
    plt.barh(y_pos,x,align='center', alpha=0.4, color='g')
    # 标签
    plt.xlabel('5日涨幅',fontproperties=zhfont1)
    t = plt.title('交通运输行业子板块涨跌幅情况',fontproperties=zhfont1)
    plt.ylim([-1,len(class2_name)+1+0.1])
    plt.xlim([-max(x)-1, max(x)+1])
    plt.grid()
    plt.savefig("class2.jpg")
    plt.show()
    
def draw_class1(c1):
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    c1_idry=sort_class(c1)
    class1_name=[]
    class1_change=[]
    for c1 in c1_idry:
        class1_name.append(c1[0])
        class1_change.append(c1[1])
    y_pos = np.arange(len(class1_name))
    bar_labels=class1_name
    x =class1_change
    plt.yticks(y_pos, bar_labels, fontsize=7,fontproperties=zhfont1)
    plt.barh(y_pos,x,align='center', alpha=0.4, color='b')
    # 标签
    plt.xlabel('5日涨幅',fontproperties=zhfont1)
    t = plt.title('各行业板块涨跌幅情况',fontproperties=zhfont1)
    plt.ylim([-1,len(class1_name)+1+0.1])
    plt.xlim([-max(x)-1, max(x)+1])
    plt.grid()
    plt.savefig("class1.jpg")
    plt.show()

def draw_single1(single):
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    s_idry=sort_class(single)
    s_name=[]
    s_change=[]
    for i,s in zip(range(5),s_idry):
        s_name.append(s[0])
        s_change.append(s[1])
        
    lables=s_name
    quants=s_change
    width = 0.4  
    ind = np.linspace(0.5,9.5,5)  
    # make a square figure  
    fig = plt.figure(1)  
    ax  = fig.add_subplot(111)  
    # Bar Plot  
    ax.bar(ind-width/2,quants,width,color='green')  
    # Set the ticks on x-axis  
    ax.set_xticks(ind)  
    #设置中文字体
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    ax.set_xticklabels(lables,fontproperties=zhfont1)  
    # labels  
    ax.set_xlabel('个股名称',fontproperties=zhfont1)  
    ax.set_ylabel('涨幅',fontproperties=zhfont1)  
    # title  
    ax.set_title('交运行业个股涨幅前五', bbox={'facecolor':'0.8', 'pad':5},fontproperties=zhfont1)  
    plt.grid(True)     
    plt.savefig("topfive.jpg") 
    plt.show()   
    plt.close()     
    
def draw_single2(single):
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    s_idry=sort_class(single)
    s_name=[]
    s_change=[]
    for i,s in zip(range(5),reversed(s_idry)):
        s_name.append(s[0])
        s_change.append(s[1])
    
    lables=s_name
    quants=s_change
    width = 0.4  
    ind = np.linspace(0.5,9.5,5)  
    # make a square figure  
    fig = plt.figure(1)  
    ax  = fig.add_subplot(111)  
    # Bar Plot  
    ax.bar(ind-width/2,quants,width,color='green')  
    # Set the ticks on x-axis  
    ax.set_xticks(ind)  
    #设置中文字体
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    ax.set_xticklabels(lables,fontproperties=zhfont1)  
    # labels  
    ax.set_xlabel('个股名称',fontproperties=zhfont1)  
    ax.set_ylabel('跌幅',fontproperties=zhfont1)  
    # title  
    ax.set_title('交运行业个股跌幅前五', bbox={'facecolor':'0.8', 'pad':5},fontproperties=zhfont1)  
    plt.grid(True)  
    
    plt.savefig("botfive.jpg") 
    plt.show()   
    plt.close()     
 

def render(c2,c1,single):
    with open("template.html", "r") as fd:
        template = Template(fd.read())
    index=part_1()
    c2_idry=sort_class(c2)
    c2_top={"name":c2_idry[0][0],"w_change":c2_idry[0][1]}
    c2_bot={"name":c2_idry[-1][0],"w_change":c2_idry[-1][1]}
    c1_idry=sort_class(c1)
    rank = [i for i, x in enumerate(c1_idry) if x[0] == "交通运输"][0]+1
    single=sort_class(single)
    w_top={"name":single[0][0],"w_change":single[0][1]}
    w_bot={"name":single[-1][0],"w_change":single[-1][1]}

    config_content = template.render(stocks=index,c2_top=c2_top,c2_bot=c2_bot,rank=rank,w_top=w_top,w_bot=w_bot) 
    f = open("stockinfo.html",'w')
    f.write(config_content)
    f.close()   
   

       
   
if __name__ == "__main__":
   
    #index_info()
 
    # part_1()
  
    c2=class2_info() 
    c1=class1_info()
    single=single_info()
    render(c2,c1,single)
    draw_class2(c2)
    draw_class1(c1)
    draw_single1(single)
    draw_single2(single)
    
   
   

