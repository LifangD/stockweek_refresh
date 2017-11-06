# -*- encoding:utf-8 -*-
import datetime
import xlrd
import tushare as ts
import sys
import numpy as np    
import matplotlib
import matplotlib.mlab as mlab    
import matplotlib.pyplot as plt

from astropy.units import percent
from tushare.stock.trading import get_h_data
reload(sys)  
sys.setdefaultencoding('utf-8')  

def stockweek_get(d):
     #isoweekday 周一返回1，周二返回2，一次类推
    weekdate=[]
    dayscount =datetime.timedelta(days=(d.isoweekday()))
    dayto =d -dayscount  
    sixdays =datetime.timedelta(days=6)
    dayfrom =dayto -sixdays
    date_from =datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day)
    dayto-=datetime.timedelta(2)
    date_to =datetime.datetime(dayto.year, dayto.month, dayto.day)
    weekdate.append(date_from.strftime("%Y-%m-%d"))
    weekdate.append(date_to.strftime("%Y-%m-%d"))
    return weekdate;

#某一个指数的一周变动；如深证报收3378.65点，下跌0.35个百分点;
#需要获取 指数名称，上周五的close 收盘点


def board_change(number,year,month,day):
    #d =datetime.datetime.now() ##获取当前日期
    result=[];
    d=datetime.datetime(year,month,day)
    week=stockweek_get(d)  
    df=ts.get_h_data(number,index=True,start=week[0],end=week[1])
    weekend_close=df[u'close'][0]
    weekstart_close=df[u'close'][4]
    change_percent=round((weekend_close-weekstart_close)/weekstart_close*100,4)
    result.append(weekend_close)
    result.append(change_percent)
    return result
    #print weekend_close #报收XXX
    #print change_percent #涨跌幅
def single_change(number,year,month,day):
    #d =datetime.datetime.now() ##获取当前日期
    
    d=datetime.datetime(year,month,day)
    week=stockweek_get(d)
    df=ts.get_h_data(number,start=week[0],end=week[1])
    if df.empty:
        change_percent=0;
    else:
        weekend_close=df[u'close'][0]
        weekstart_close=df[u'close'][4]
        change_percent=round((weekend_close-weekstart_close)/weekstart_close*100,4)
    
    #sprint weekend_close #报收XXX
    print change_percent #涨跌幅
    return change_percent  
    
def temp_pre(arr=[]):  ##描述总体情况
    counter=0
    for i in arr:
        if i>0:
           counter+=1 #计算正数个数         
    if(counter==0):
        con= "上周A股市场有所回落，各重要指数成绩不佳。"
    if(counter==len(arr)): 
        con= "上周A股市场表现良好，各重要指数有所上升。"
    else: 
        con= "上周A股市场运行正常，各重要指数有升有降。"
    return con
    
    
def temp_single_index(name,close,change_percent): ##单句描述涨幅
    if(change_percent>0):
        choice="上涨了"
    else:
        choice="下跌了"
        change_percent*=(-1)
    con='%s报收%.2f点，%s%.2f个百分点。'%(name,close,choice,change_percent)
    return con

data = xlrd.open_workbook('f:/day/sw_industry.xlsx')
table = data.sheets()[1]
nrows = table.nrows 

def name(code):
    for i in range(nrows):
        if (table.row(i)[1].value==code):
            return str(table.row(i)[1].value)+str(table.row(i)[2].value)
def codelist():
    codes=[]    
    
    for i in range(nrows):
        codes.append(str(table.row(i)[1].value))
    return codes  

def changeper_ord():#交运板块涨幅排序
    change_array={}
    for c in codelist():
        change_percent=single_change(c, 2017, 11, 1)
        change_array.setdefault(c,change_percent)
    print change_array 


def changeper2(year,month,day):
    d=datetime.datetime(year,month,day)
    week=stockweek_get(d)
    df1=ts.get_stock_basics(week[0])
    df2=ts.get_stock_basics(week[1])
    result={}
    for code in codelist():
        price_day1=df1.ix[code]['pe']*df1.ix[code]['esp']
        price_day2=df2.ix[code]['pe']*df2.ix[code]['esp']
        percent=price_day2/price_day1-1
        result.setdefault(code,percent)
    return result


def sort_map(year,month,day):
    before=changeper2(year,month,day)
    after=sorted(before.items(),key=lambda asd:asd[1],reverse=True)
    topx=[]
    topy=[]
    for i in range(5):
        topx.append(name(after[i][0]))
        topy.append(after[i][1])
    lables=topx
    quants=topy
    width = 0.4  
    ind = np.linspace(0.5,9.5,5)  
    # make a square figure  
    fig = plt.figure(1)  
    ax  = fig.add_subplot(111)  
    # Bar Plot  
    ax.bar(ind-width/2,quants,width,color='green')  
    # Set the ticks on x-axis  
    ax.set_xticks(ind)  
    zhfont1 = matplotlib.font_manager.FontProperties(fname='f:/msyh.ttc')
    ax.set_xticklabels(lables,fontproperties=zhfont1)  
    # labels  
    print "交通行业个股涨幅前五如图所示："
    ax.set_xlabel('涨幅',fontproperties=zhfont1)  
    ax.set_ylabel('个股编号与名称',fontproperties=zhfont1)  
    # title  
    ax.set_title('个股涨幅前五', bbox={'facecolor':'0.8', 'pad':5},fontproperties=zhfont1)  
    plt.grid(True)  
    plt.show()  
    plt.savefig("bar.jpg")  
    plt.close()   
    print "个股涨幅最高为%s,上涨了%.2f个百分点"%(name(after[i][0]),after[i][1]*100)    
    
      
def temp_all(year,month,day):  
    index={'000001':'上证指数','399001':'深证成指','000300':'沪深300','399006':'创业板指'}
    rate=[]
    con1='其中：'
    for c1 in index.keys():
        result=board_change(c1, year, month, day)
        rate.append(result[1])
        con1+=temp_single_index(index[c1],result[0],result[1])
    con0=temp_pre(rate)
    print con0,con1
                
if __name__ == "__main__":
    #date = raw_input("请输入要查询的日期，系统将返回上一周的大盘指数情况(输入格式：YYYY-MM-DD):") 
    
    #ymd=date.split('-')
    #board_change('000001',int(ymd[0]),int(ymd[1]),int(ymd[2]))
    #temp_x('上证综指',3378.65,-0.35,)
    
    #temp_all(int(ymd[0]),int(ymd[1]),int(ymd[2]))
    temp_all(2017, 11, 1)
    #changeper_ord()
    #change=single_change('600026', 2017, 11, 1)  
    #print change
    sort_map(2017,11,1)
    

    
    