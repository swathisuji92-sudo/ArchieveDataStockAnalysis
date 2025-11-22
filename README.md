# ArchieveDataStockAnalysis
The repository provides solution to analysis on various Sector and Firms under it w.r.t their stock performance on Daily and Montly basis. The repo provide both GUI and Tableau/PowerBI capable data visualization. 

Current Features:

1. Load Archive Stock data(yml - format) and load into csv :
         cmd - python /ArchieveDataStockAnalysis/load_stock_data.py
         Prompt will appear to get Source Directory for Reading the source file(s) and to get Destination directory to write Ticker wise csv data.

2. Stock Analysis GUI - Streamlit app that gives visualization on different perspective of stock trends
         cmd - streamlit run /ArchieveDataStockAnalysis/stock_analysis_engine.py <SRC_DIR_PATH>

3. Provides consildated files on each terms of stock performance and trends. Which can be used in Power BI/Tableau to play around with rendered data file.
         cmd - python /ArchieveDataStockAnalysis/tableau_analysis_data.py
         Prompt will appear to get Source Directory for Reading the source stock file(s) and to get Destination directory to write satistics data.

Business scenarios covered:
  1. Captures Volatality for each Ticker
  2. Cumulative return by each Ticker for the provided period
  3. Group the Tickers by Sector and provides overall performance on each Sector
  4. Correlation between each of the Ticker close price's percentage of change
  5. Month wise break down of Top 5 Gainer and Loser Tickers


Future Scope:

    > Right now yaml is only supported this will be extended to other input formats for processing
    > Based on user input the type of chart rendered can be customized 
