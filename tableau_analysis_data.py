import pandas as pd
import numpy as np
import os
import glob

def daily_return_of_stock(sorted_ticker_wise_data):
    daily_return=[]
    prev_close_price = 0.0
    skipSymbolFirstFlag=True
    for rec in sorted_ticker_wise_data.itertuples(index=False):
        close_price=float(rec[1])
        if skipSymbolFirstFlag:
            skipSymbolFirstFlag=False
        else:
            daily_return.append((close_price-prev_close_price)/prev_close_price)
        prev_close_price=close_price
    return daily_return

dest_dir=str(input('Enter Destination Path for csv file creation:'))
os.makedirs(dest_dir, exist_ok=True)

src_file_dir=str(input('Enter Source Path for reading Stock file(s): (*.csv) files are supported right now'))
csv_files = glob.glob(os.path.join(src_file_dir, "*.csv"))
csv_data=pd.DataFrame()
for f in csv_files:
    print(f'Processing File:: {f}')
    if csv_data.empty:
        csv_data=pd.read_csv(f)
    else:
        csv_data=pd.concat([csv_data,pd.read_csv(f)],axis=0)

print(csv_data.head(5))
unique_ticker=csv_data['Ticker'].unique()
#print(csv_data.info())
ticker_vs_metrics=pd.DataFrame(columns=['Ticker','volatality'])

#1. Volatile Data
print('Starting capture of Volatality for each Ticker')
volatality_anal={}
for i in unique_ticker:
        ticker_wise_data = csv_data[csv_data['Ticker']==i]
        sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
        daily_return=daily_return_of_stock(sorted_ticker_wise_data)
        std_dev=np.std(np.array(daily_return))
        volatality_anal[i]=std_dev
        ticker_vs_metrics.loc[len(ticker_vs_metrics)]=[i,std_dev]

print(ticker_vs_metrics.head(5))
print('Volatality for each Ticker is captured')

#3. Avg Yearly return for sector wise
print('Starting capture of Sector wise Yearly performance - by grouping each Ticker')
sector_df=pd.read_csv('/Users/manikandan/Documents/Sujitha/stockAnalysis/Sector_data-Sheet1.csv')
sector_df['Ticker']=sector_df.apply(lambda x : str(x['Symbol']).split(':')[1].strip(), axis=1)
sector_df=sector_df.drop(columns=['COMPANY','Symbol'])
sector_df.loc[sector_df['Ticker']=='ADANIGREEN','Ticker']='ADANIENT'
sector_df.loc[sector_df['Ticker']=='AIRTEL','Ticker']='BHARTIARTL'
sector_df.loc[sector_df['Ticker']=='TATACONSUMER','Ticker']='TATACONSUM'
sector_df.loc[len(sector_df)]=['FMCG','BRITANNIA']
print(sector_df)
avg_daily_ret={}
for i in unique_ticker:
    ticker_wise_data = csv_data[csv_data['Ticker']==i]
    sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
    daily_return=daily_return_of_stock(sorted_ticker_wise_data)
    avg_daily_ret[i]=np.average(daily_return)
    
avg_daily_ret_df=pd.DataFrame.from_dict(avg_daily_ret,orient='index',columns=['Average Yearly Return'])
#print(avg_daily_ret_df)
ticker_vs_metrics=ticker_vs_metrics.set_index('Ticker').join(avg_daily_ret_df,on="Ticker")
print(ticker_vs_metrics.head(5))
ticker_vs_metrics=ticker_vs_metrics.join(sector_df.set_index('Ticker'),on="Ticker")
print(ticker_vs_metrics)

#ticker_vs_metrics.to_csv(f'{dest_dir}TickerVsVolatileSectorReturnData.csv',index=True)
print('Captured data of Sector wise Yearly performance - by grouping each Ticker')

# 4. Correlation between Tickers
print('Starting capture of Correlation matrix between each Ticker close price')
corr_data=csv_data[['Ticker','close','Date','Month','Year']]
corr_data['calendar_date']=corr_data.apply(lambda x: '-'.join([str(x['Year']),str(x['Month']),str(x['Date'])]),axis=1)
corr_data=corr_data.drop(columns=['Year','Date','Month'])
corr_df=corr_data.pivot(index='calendar_date', columns='Ticker', values='close')
print(corr_df.head(5)) 
corr_chart=corr_df.pct_change().corr()
#corr_chart.to_csv(f'{dest_dir}CorrelationTickerData.csv',index=True)
print('Captured Correlation matrix between each Ticker close price')

#5. Month wise Data
print('Capture Top 5 Gainer and Loser Tickers by each month for a calendar year')
filtered_df=pd.DataFrame()
years=csv_data['Year'].unique()
for year in years:
    current_year_data=csv_data[csv_data['Year']==year]
    #ticker_vs_avg_monthly_ret=pd.DataFrame(columns=['Ticker','monthly_return','Month'])
    for month in current_year_data['Month'].unique():
        ticker_vs_avg_monthly_ret=pd.DataFrame(columns=['Ticker','monthly_return','Month-Year'])
        for i in unique_ticker:
            curr_month_data = current_year_data[(current_year_data['Ticker']==i) & (current_year_data['Month']==month)].sort_values(by=['Date'],ascending=True)
            daily_return=daily_return_of_stock(curr_month_data)
            ticker_vs_avg_monthly_ret.loc[len(ticker_vs_avg_monthly_ret)]=[i,np.sum(daily_return),f'{month}-{year}']
            ticker_vs_avg_monthly_ret=ticker_vs_avg_monthly_ret.sort_values(by=['monthly_return'],ascending=False)
        if filtered_df.empty:
            print('Here')
            filtered_df=ticker_vs_avg_monthly_ret.head(5)
            print(filtered_df['Month-Year'].unique())
        else:
            print('Here2')
            filtered_df=pd.concat([filtered_df,ticker_vs_avg_monthly_ret.head(5)],axis=0)
            print(filtered_df['Month-Year'].unique())
        print('Here3')
        filtered_df=pd.concat([filtered_df,ticker_vs_avg_monthly_ret.tail(5)],axis=0)
        print(filtered_df['Month-Year'].unique())
#filtered_df.to_csv(f'{dest_dir}MonthReturnTickerData.csv',index=False)
print('Captured Top 5 Gainer and Loser Tickers by each month for a calendar year')

#2. CumulativeReturnData
print('Capture Cumulative return for each Ticker and fetch top 5 Gainers to view their trend')
cum_ret_anal={}
ind_cum_ret={}
for i in unique_ticker:
    ticker_wise_data = csv_data[csv_data['Ticker']==i]
    sorted_ticker_wise_data=ticker_wise_data.sort_values(by=['Year','Month','Date'],ascending=True)
    final_cum_return=0.0
    cum_ret=[]
    daily_return=0.0
    prev_close_price = 0.0
    skipSymbolFirstFlag=True
    for rec in sorted_ticker_wise_data.itertuples(index=False):
        close_price=float(rec[1])
        if skipSymbolFirstFlag:
            skipSymbolFirstFlag=False
        else:
            daily_return=((close_price-prev_close_price)/prev_close_price)
        final_cum_return+=daily_return
        cum_ret.append(final_cum_return)
        prev_close_price=close_price
    ind_cum_ret[i]=cum_ret
    cum_ret_anal[i]=np.sum(ind_cum_ret[i])

cum_ret_anal_df=pd.DataFrame.from_dict(cum_ret_anal,orient='index',columns=['cumulative_return'])
cum_ret_anal_df=cum_ret_anal_df.sort_values(by=['cumulative_return'],ascending=False,axis=0)
print(cum_ret_anal_df.head(10))
ticker_vs_cum_ret_metrics=pd.DataFrame(data=range(1,len(ind_cum_ret[i])),dtype=int,columns=['Index'])
for i in cum_ret_anal_df.head(5).index:
    ind_cum_ret_df=pd.DataFrame({i:ind_cum_ret[i]})
    ticker_vs_cum_ret_metrics=pd.concat([ticker_vs_cum_ret_metrics,pd.DataFrame({i:ind_cum_ret[i]})],axis=1)
print(ticker_vs_cum_ret_metrics.head(5))
ticker_vs_cum_ret_metrics.to_csv(f'{dest_dir}CumulativeReturnData.csv',index=False)
print('Captured top 5 Gainers Cumulative return Ticker and its trend')


