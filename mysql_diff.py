#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# 202-06-18 MySQL数据库表/字段对比工具
import pymysql

SDB={'host':'172.16.0.xx','port':3306,'user':'root','password':'111111','database':'erp_station'}
DDB={'host':'xx.xx.xx.xx','port':3306,'user':'read','password':'111111','database':'erp_station'}


#根据数据库连接地址和SQL返回查询结果
def get_data(DB_CONN, SQL):
    db = pymysql.connect(**DB_CONN, charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(SQL)
        if cursor.rowcount != 0:
            results=cursor.fetchall()
    except:
        print ("在%s的%s数据库中执行%s命令失败！！！" %(DB_CONN['host'],DB_CONN['database'],SQL))
        exit(404)
    cursor.close()
    db.close()
    return results

# 把返回的嵌套元素转换为列表
def to_list(result):
    r_list = []
    for t in result:
        r_list.append(t[0])
    return r_list

def to_print(key,value1,value2):
    tplt = "{0:<%d}\t{1:<15}\t{2:<15}" %DATA_LENGTH
    value1=value1.replace("NO","\033[31mNO\033[30m")
    value2=value2.replace("NO","\033[31mNO\033[30m")
    print(tplt.format(key, value1, value2))

# 比较两个表是否有不同字段。
def diff_data(ALL_DATA,S_HOST,S_NAME,S_DATA,D_HOST,D_NAME,D_DATA):
    global DATA_LENGTH
    S_VIEW='Column' if "." in S_NAME else 'Table'
    print ("\r\n\r\n%s的%s共有%s个%s，%s的%s共有%s个%s" %(S_HOST,S_NAME,len(S_DATA),S_VIEW,D_HOST,D_NAME,len(D_DATA),S_VIEW))
    #获取所有值中最长的值，然后加10，用于固定显示列宽。
    #DATA_LENGTH=len(sorted(ALL_DATA,key=lambda i:len(i),reverse=True)[0])+10
    DATA_LENGTH=50
    to_print(S_VIEW, S_HOST, D_HOST)
    for i in ALL_DATA:
        if i in S_DATA:
            to_print(i,'YES','YES') if i in D_DATA else to_print(i,'YES','NO')
        else:
            to_print(i,'NO','YES') if i in D_DATA else to_print(i,'NO','NO')

def diff(DATA,SQL='show tables'):
    if DATA=='column':
        sname=SDB['database']+"."+SQL
        dname=DDB['database']+"."+SQL
        SQL='desc %s' %SQL
    else:
        sname=SDB['database']
        dname=DDB['database']
    sdata=to_list(get_data(SDB,SQL))
    ddata=to_list(get_data(DDB,SQL))
    alldata=list(set(sdata+ddata))     #合并两个库的表并去重。
    diff_data(alldata,SDB['host'],sname,sdata,DDB['host'],dname,ddata)

def main():
    #比较两个库的表是否相等。
    diff('table')
    #以SDB为标准库，比较SDB和DDB两个库的所有表的字段是否相等。
    for i in to_list(get_data(SDB,'show tables')):
        diff('column',i)


if __name__ == '__main__':
    main()
