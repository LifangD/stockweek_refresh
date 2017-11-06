# -*- encoding:utf-8 -*-
import datetime
import xlrd
import tushare as ts
import sys
reload(sys)  
sys.setdefaultencoding('utf-8')  
import numpy as np    
import matplotlib
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt
import math
from astropy.units import percent
from tushare.stock.trading import get_h_data

#获取新浪标准下交通行业下的个股的名单
data = xlrd.open_workbook('f:/day/sw_industry.xlsx')
table = data.sheets()[1]
nrows = table.nrows 

#根据编号返回编号+个股名称
def name(code):
    for i in range(nrows):
        if (table.row(i)[1].value==code):
            return str(table.row(i)[1].value)+str(table.row(i)[2].value)
        
#返回包含所有交通行业个股编号的数组        
def codelist():
    codes=[]    
    for i in range(nrows):
        codes.append(str(table.row(i)[1].value))
    return codes  

#获取上周五和上上周五 两天的日期；
def two_friday(date):  
    weekdate=[]
    ymd=date.split('-')
    d=datetime.datetime(int(ymd[0]),int(ymd[1]),int(ymd[2]))
    dayscount =datetime.timedelta(days=(d.isoweekday()))
    #isoweekday 周一返回1，周二返回2，
    dayto =d -dayscount-datetime.timedelta(days=2) #上一个周五  
    sevendays =datetime.timedelta(days=7)
    dayfrom =dayto -sevendays #上上个周五
    date_from =datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day)
    date_to =datetime.datetime(dayto.year, dayto.month, dayto.day)
    weekdate.append(date_from.strftime("%Y-%m-%d"))
    weekdate.append(date_to.strftime("%Y-%m-%d"))
    return weekdate;

def show(day2):
    res="%s至%s:"%(day2[0],day2[1])
    return res

#单个指数的一周变动；如深证报收3378.65点，下跌0.35个百分点;需要获取 指数名称，上周五的close 收盘点
def board_change(number,twoday):
    result=[];   
    df=ts.get_h_data(number,index=True,start=twoday[0],end=twoday[1])
    weekend_close=df[u'close'][0]
    weekstart_close=df[u'close'][4]
    change_percent=round((weekend_close-weekstart_close)/weekstart_close*100,4)
    result.append(weekend_close)
    result.append(change_percent)
    return result
    #print weekend_close #报收XXX
    #print change_percent #涨跌幅
    
 
#个股涨跌幅情况   
def single_change(number,twoday):
    df=ts.get_h_data(number,start=twoday[0],end=twoday[1])
    if df.empty:
        change_percent=0;
    else:
        weekend_close=df[u'close'][0]
        weekstart_close=df[u'close'][4]
        change_percent=round((weekend_close-weekstart_close)/weekstart_close*100,4)
    return change_percent  
 
 
#描述总体情况    
def temp_pre(arr):  
    time="上周行情回顾:"
    up="A股市场有所回落，各重要指数成绩不佳。"
    down="A股市场表现良好，各重要指数有所上升。"
    middle="A股市场运行正常，各重要指数有升有降。"
    counter=0
    for i in arr:
        if i>0:
           counter+=1 #计算正数个数         
    if(counter==0):
        con=up 
    if(counter==len(arr)): 
        con=down 
    else: 
        con=middle 
    return time+con
   
##单句描述涨幅   
def temp_single_index(name,close,change_percent): 
    if(change_percent>0):
        choice="上涨了"
    else:
        choice="下跌了"
        change_percent*=(-1)
    con='%s报收%.2f点，%s%.2f个百分点。'%(name,close,choice,change_percent)
    return con

#交运板块涨幅排序 法1：根据个股 get_h_data()
def changeper_ord(date):
    change_array={}
    for c in codelist():
        change_percent=single_change(c, date)
        change_array.setdefault(c,change_percent)
    print change_array 

#交运板块涨幅排序 法2：根据个股 get_stock_basics()
def changeper2(twoday):
    df1=ts.get_stock_basics(twoday[0])
    df2=ts.get_stock_basics(twoday[1])
    result={}
    for code in codelist():
        price_day1=df1.ix[code]['pe']*df1.ix[code]['esp']
        price_day2=df2.ix[code]['pe']*df2.ix[code]['esp']
        if(price_day1==0):
            continue
        percent=price_day2/price_day1-1
        if(math.isnan(percent)):
            percent=0
        result.setdefault(code,percent)
    return result

# 挑选出涨幅前五的股票
def top_five(twoday):
    before=changeper2(twoday)
    after=sorted(before.items(),key=lambda asd:asd[1],reverse=True)
    topx=[]
    topy=[]
    for i in range(5):
        topx.append(name(after[i][0]))
        topy.append(after[i][1])
    return topx,topy
 
#挑选出涨幅最高，并文字说明
def descript(top5):
    topx=top5[0][0]
    topy=top5[1][0]
    res="交通行业个股涨幅前五如图所示，其中涨幅最高为%s,上涨了%.2f个百分点"%(topx,topy*100) 
    return res
#为涨幅前五的股票画柱状图   
def map(top5):
    lables=top5[0]
    quants=top5[1]
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
    ax.set_xlabel('个股编号与名称',fontproperties=zhfont1)  
    ax.set_ylabel('涨幅',fontproperties=zhfont1)  
    # title  
    ax.set_title('个股涨幅前五', bbox={'facecolor':'0.8', 'pad':5},fontproperties=zhfont1)  
    plt.grid(True)  
    plt.show()  
    plt.savefig("bar.jpg")  
    plt.close()   
       
         
def temp_allindex(twoday):    
    index={'000001':'上证指数','399001':'深证成指','000300':'沪深300','399006':'创业板指'}
    rate=[]
    con1='其中：'
    for c1 in index.keys():
        result=board_change(c1, twoday)
        rate.append(result[1])
        con1+=temp_single_index(index[c1],result[0],result[1])
    con0=temp_pre(rate)
    return con0+con1

def show_all(date):
    twoday=two_friday(date)
    str0=show(twoday)   
    str1=temp_allindex(twoday)
    top5=top_five(twoday)
    str2=descript(top5)
    print '\n'
    print str0
    print str1
    print str2
    map(top5)
   
                
if __name__ == "__main__":
    date = raw_input("请输入要查询的日期(输入格式：YYYY-MM-DD):") 
    show_all(date)
    #df1=ts.get_stock_basics('2017-08-25')
    #df1.to_excel('f:/day/0825.xlsx')
    #df2=ts.get_stock_basics('2017-08-31')
    #df2.to_excel('f:/day/0831.xlsx')
    

    
    