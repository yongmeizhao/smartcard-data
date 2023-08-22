import csv
import datetime
import os
import time

import pandas as pd


#获取刷入站点列表
def get_station(data):
    station_data = data.loc[(source_txtdata['TYPE'] == 21)]
    station_list=station_data[['STATION']].drop_duplicates().values.tolist()
    return station_list

#处理数据方法
def smart_one(source_txtdata):
    #下面四行代码定义一个结果表
    resultfile = os.getcwd() + '/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '_one.csv'
    file = open(resultfile, 'w', encoding='gbk', newline='')  # 生成结果表，并写入表头
    csv_writer = csv.writer(file)
    csv_writer.writerow(['STATION', 'TIME', 'COUNT'])

    station_list=get_station(source_txtdata) #调用方法返回唯一站点列表
    #循环对每一个站点进行统计
    #station_list=[['五和']]
    for item in range(len(station_list)):
        station=station_list[item][0]
        station_info=source_txtdata.loc[(source_txtdata['STATION'] == station) &(source_txtdata['TYPE'] == 21)] #根据站点名称和输入类型过滤出该站点数据
        station_info_timesort=station_info.sort_values(by='TIME', ascending=True) #按照时间列排序
        station_info_timesort['TIME'] = pd.to_timedelta(station_info_timesort.TIME) #格式化时间列
        station_info_time=station_info_timesort[['ID','TIME']] #过滤ID列和时间列，对这两列数据进行分组统计处理
        #按照时间列，间隔5分钟进行分组统计数量
        station_info_count = station_info_time.groupby(pd.Grouper(key='TIME', freq='5Min')).count()
        station_info_count.reset_index(level=0, inplace=True) #重置索引，目的是将时间索引列作为数据使用
        last_data=station_info_count.values.tolist() #将结果转list
        #循环将数据写入结果表
        for row in range(len(last_data)):
            csv_writer.writerow(
                [station, str(last_data[row][0]+datetime.timedelta(minutes=5)).split(' ')[2], str(last_data[row][1])])

def smart_two(source_txtdata):
    #下面四行定义一个结果表
    resultfile = os.getcwd() + '/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '_two.csv'
    file = open(resultfile, 'w', encoding='gbk', newline='')  # 生成结果表，并写入表头
    csv_writer = csv.writer(file)
    csv_writer.writerow(['STATION', 'TIME', 'COUNT','SWITCH'])

    station_list = get_station(source_txtdata)  # 调用方法返回唯一站点列表
    print("len(station_list):",station_list)
    # 循环对每一个站点进行统计
    #station_list = [['五和']]
    for item in range(len(station_list)):
        station = station_list[item][0]
        station_info = source_txtdata.loc[(source_txtdata['STATION'] == station) & (source_txtdata['TYPE'] == 21)]  # 根据站点名称和输入类型过滤出该站点数据
        station_info.loc['TIME'] = pd.to_timedelta(station_info.TIME)  # 格式化时间列
        station_info_timesort = station_info.sort_values(by='TIME', ascending=True)  # 按照时间列排序
        station_info_list=station_info_timesort.values.tolist()
        new_station_info_list=[]
        for id_i in range(len(station_info_list)-1):
            station_rowdata=station_info_list[id_i]
            id=station_rowdata[0]
            station_time=station_rowdata[1]
            #根据ID过滤出来这个乘客的历史乘车记录并按照时间排序
            id_his_data=source_txtdata.loc[(source_txtdata['ID'] == id)]
            #下面就是对这个智能卡出行记录按照时间排序，排序之后才能根据时间顺序判断公交转地铁
            id_his_data.loc['TIME'] = pd.to_timedelta(id_his_data.copy().TIME)  # 格式化时间列
            id_his_data_timesort = id_his_data.sort_values(by='TIME', ascending=True).values.tolist()  # 按照时间列排序
            #对每一条进行判断，如果第一条的时间和station_time相等，则表示第一次乘车，还没有转乘情况，如果不是第一条相等，那就判断这个时间点的上一条是不是类型是31，如果是则表示转乘
            for switch_i in range(len(id_his_data_timesort)):
                new_time=id_his_data_timesort[switch_i][1]
                new_type=str(id_his_data_timesort[switch_i-1][2]) #这里减去1的目的是判断
                if new_time==station_time:
                    if switch_i==0: #如果是第一条，那就不存在前面转乘的逻辑，因为这是乘客当日第一次乘车,直接标志0就可以了
                        if len(station_rowdata)<=4: #这个判断主要是防止同一秒存在刷入刷出的异常数据，下同
                            station_rowdata.append(0)
                    else:
                        if new_type=='31':
                            if len(station_rowdata)<=4:
                                station_rowdata.append(1) #如果是公交转地铁，设置为1，后续用这个求和，并且终端此次循环，因为找到了目标
                            break;
                        else:
                            if len(station_rowdata)<=4:
                                station_rowdata.append(0)
            #将每一个站点时间加入到总的列表，便于转pandas进行处理
            new_station_info_list.append(station_rowdata)
        #list转pandas
        if len(new_station_info_list)>0:
            new_data=pd.DataFrame(new_station_info_list)
            #new_data=mid_data[['0','1','2','3','4']]
            new_data.columns = ['ID', 'TIME', 'TYPE', 'STATION','SWITCH'] #重新命名列名称
            #重新的新的pandas进行时间列格式化
            new_data_timesort = new_data.sort_values(by='TIME', ascending=True)  # 按照时间列排序
            new_data_timesort['TIME'] = pd.to_timedelta(new_data_timesort.TIME)  # 格式化时间列
            #按照时间平吕汇总统计
            new_data_count = new_data_timesort[['ID', 'TIME']]
            station_count=new_data_count.groupby(pd.Grouper(key='TIME', freq='5Min')).count()
            #对是否公交转地铁的SWITCH按照时间频率求和统计
            new_data_sum = new_data_timesort[['TIME', 'SWITCH']]
            station_sum = new_data_sum.groupby(pd.Grouper(key='TIME', freq='5Min')).sum()

            #以上两种统计得到的就是每一个站点的流量以及这个站点每一个乘客上一个站是公交站的标志求和
            #按照第一个表格的逻辑写入结果表即可
            station_count.reset_index(level=0, inplace=True)  # 重置索引，目的是将时间索引列作为数据使用
            last_station_count = station_count.values.tolist()  # 将结果转list
            last_station_sum=station_sum.values.tolist()# 将结果转list
            for r_i in range(len(last_station_count)):
                #写入csv，因为last_station_count的长度和对应的值last_station_sum一致，所以写入的时候找到last_station_sum对应的下标位置的值即可
                csv_writer.writerow([station, str(last_station_count[r_i][0] + datetime.timedelta(minutes=5)).split(' ')[2], str(last_station_count[r_i][1]),str(last_station_sum[r_i][0])])

#文件入口
if __name__ == '__main__':
    txt_dir='SmartCardData.txt'
    source_txtdata = pd.read_table(txt_dir, sep=',', encoding='utf-8')  # 读取原始数据并根据原始数据逗号作为分隔
    source_txtdata.columns = ['ID', 'TIME', 'TYPE', 'STATION']
    #smart_one(source_txtdata) #第一个表格函数
    smart_two(source_txtdata)  #第二个表格函数
