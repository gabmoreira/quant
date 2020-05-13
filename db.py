#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 19:21:40 2020

@author: gabriel
"""


import pandas as pd      
import yfinance as yf
import mysql.connector

from getpass import getpass
from influxdb import DataFrameClient



YHQUERY = ['symbol',
           'longName',
           'sector', 
           'industry', 
           'longBusinessSummary',
           'country', 
           'city', 
           'address1', 
           'fullTimeEmployees', 
           'exchangeTimezoneShortName',
           'exchange', 
           'market', 
           'currency', 
           'website', 
           'logo_url']


SQL_COL_MAXSIZES = [7, 64, 255, 255, 4095, 63, 63, 511, 7, 7, 15, 32, 7, 255, 255]


TABLES = ["companies", "historical"]



def as_strutf8(data):
    '''
        Converts the input data to a UTF-8 encoded string. Non UTF-8 characters
        are eliminated.
    '''
    data_str = str(data)
    new_str = data_str.encode('ascii',errors='ignore').decode('utf-8',errors='ignore')
    return new_str



def parse_yahoo(yh_info_dict, query=YHQUERY):
    '''
        Returns a tuple with the desired data, specified in the query, for 
        a yfinance stock info dictionary
    '''
    data = []
    for (i,q) in enumerate(query):    
        yh_data_utf8 = as_strutf8(yh_info_dict[q])
        yh_data_utf8 = yh_data_utf8[:SQL_COL_MAXSIZES[i]] 
        data.append(yh_data_utf8)
    return tuple(data)



class Database(object):
    
    @classmethod
    def session(cls):
        '''
            Starts a database session connected to MySQL database "exchanges"
            and influxDB database "historical". Requests user login info.
        '''
        cls.HOST            = "localhost"
        cls.MYSQL_USR       = input("User: ")
        cls.MYSQL_DATABASE  = "exchanges"
        cls.INFLUX_USR      = "root"
        cls.INFLUX_PASSWD   = "root"
        cls.INFLUX_PROTOCOL = "line"
        cls.INFLUX_DATABASE = "historical"
        cls.INFLUX_PORT     = 8086
            

        # Establish connection to MySQL server
        try:
            cls.mysql_client = mysql.connector.connect(host     = cls.HOST,
                                                       user     = str(cls.MYSQL_USR),
                                                       passwd   = str(getpass("Password: ")),
                                                       database = cls.MYSQL_DATABASE)
            
        except:
            print("Cannot establish connection to MySQL server.")
            exit
            
        else:
            cls.cursor = cls.mysql_client.cursor(buffered=True)  
            cls.companies_insert_cmd = "INSERT INTO companies (ticker, name, sector, industry, summary, country, city,\
                                        address, employees, timezone, exchange, market, currency, website, logo) VALUES \
                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                      
            n_stocks = cls.SQLQuery("SELECT COUNT(*) FROM companies")[0]
            print("Connected to exchange database %d registered companies." % (n_stocks))


        # Establish connection to influxDB server
        try:
            cls.influx_client = DataFrameClient(host     = cls.HOST,
                                                port     = cls.INFLUX_PORT,
                                                username = cls.INFLUX_USR,
                                                password = cls.INFLUX_PASSWD,
                                                database = cls.INFLUX_DATABASE)
        except:
            print("Cannot establish connection to influxDB server.")
            exit

        else:
            print("Connected to historical database.")
            


    @classmethod
    def SQLQuery(cls, sql_cmd, verbose=False):
        '''
            Processes SQL query <sql_cmd> to MySQL server
        '''
        cls.cursor.execute(sql_cmd)
        out = cls.cursor.fetchall() 
        if verbose:
            for x in out:
              print(x) 
        return out
          
  
    
    @classmethod
    def influxQuery(cls, influx_cmd):
        '''
            Processes influx query <influx_cmd> to influxDB server
        '''
        return cls.influx_client.query(influx_cmd)



    @classmethod
    def getListInfluxTickers(cls):
         query_result = cls.influxQuery("SHOW MEASUREMENTS").raw
         list_tickers = sum(query_result['series'][0]['values'], [])
         return list_tickers



    @classmethod
    def getListMySQLTickers(cls):
         query_result  = cls.SQLQuery("SELECT ticker FROM companies")
         list_tickers  = [ticker[0] for ticker in query_result] 
         return list_tickers


    
    @classmethod
    def getHistorical(cls, ticker):
        query_result = cls.influxQuery("SELECT * FROM " + ticker)
        return query_result.get(ticker)


    @classmethod
    def updateInflux(cls):
        '''
            Updates historical data for all the tickers in MySQL 'companies'
        '''
        tickers_SQL = cls.getListMySQLTickers()
        for t in tickers_SQL:
            cls.updateInfluxMeasurement(t.upper())



    @classmethod
    def updateInfluxMeasurement(cls, ticker):
        '''
        '''       
        # Check if the ticker is in MySQL 'companies'
        if ticker in cls.getListMySQLTickers():
            # If measurement does not exist in the influxDB, create a new one
            if ticker not in cls.getListInfluxTickers():
                try:
                    s = yf.Ticker(ticker)
                    print("Fetched <" + ticker + "> historical data from Yahoo.\n")
                    df = s.history(period="max")
                    df.columns = ["open", "high", "low", "close", "volume", "dividends", "stock splits"]
                    df.rename_axis(None, axis=1).rename_axis("date", axis=0)
                    cls.influx_client.write_points(df, ticker.upper(), protocol=cls.INFLUX_PROTOCOL)
                    print("Added historical data <" + ticker + "> to influxDB.\n")
                except:
                    print("Error retrieving historical data of <" + ticker + ">.\n")
                    pass
                   
            # If measurement already exists in influxDB, update it
            else:
                print("Historical measurements for <" + ticker + "> already available.\n")
                pass
        else:
            print("<" + ticker + "> is not recognized. Try updating the sources.\n")



    @classmethod
    def createMySQLTable(cls):
        '''
        '''
        cls.cursor.execute("CREATE TABLE companies (ticker VARCHAR(7),    \
                                                    name VARCHAR(64),     \
                                                    sector VARCHAR(255),  \
                                                    industry VARCHAR(255),\
                                                    summary VARCHAR(4095),\
                                                    country VARCHAR(63),  \
                                                    city VARCHAR(63),     \
                                                    address VARCHAR(511), \
                                                    employees VARCHAR(7), \
                                                    timezone VARCHAR(7),  \
                                                    exchange VARCHAR(15), \
                                                    market VARCHAR(32),   \
                                                    currency VARCHAR(7),  \
                                                    website VARCHAR(255), \
                                                    logo VARCHAR(255))")
        
        cls.cursor.execute("ALTER TABLE companies ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY") 


    
    @classmethod
    def dropTable(cls, table):
        '''
        '''
        cls.sql("DROP TABLE " + table)



    @classmethod
    def updateCompanyData(cls):
        '''
        '''
        df1 = pd.read_csv('./database/nyse.csv')
        df2 = pd.read_csv('./database/nasdaq.csv')
        df  = pd.concat([df1, df2])

        for i in range(df.shape[0]):
            stock = yf.Ticker(df['ticker'].iloc[i])
            
            cmd = "SELECT ticker FROM companies WHERE ticker = '" + df['ticker'].iloc[i] + "' "
            cls.cursor.execute(cmd)
            print(cmd)
            
            myresult = cls.cursor.fetchall()
        
            if len(myresult) == 0:
                print('Counter: ' + str(i))
                print(df['ticker'].iloc[i])
            
                try:
                    stock.get_info()
                    val = parse_yahoo(stock.info)
                    print('Retrieved.\n')
                    
                except:      
                    val = (as_strutf8(df['ticker'].iloc[i]),
                           as_strutf8(df['name'].iloc[i]),
                           as_strutf8(df['sector'].iloc[i]),
                           as_strutf8(df['industry'].iloc[i]),
                           "na", "na", "na", "na", "na", "na", "na", "na", "na", "na", "na")
                    print('Cannot retrieve data from Yahoo.\n')
                    
                finally:
                    print(val)
                    cls.cursor.execute(cls.companies_insert_cmd, val)
                    cls.mysql_client.commit()             
                    print(cls.cursor.rowcount, "record inserted in stocks table.")
            else:
                print('Row already exists. Not added.\n')
                
        


