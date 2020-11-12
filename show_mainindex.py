# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 15:08:44 2020

@author: FTAsset
"""

import os
import datetime
import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 目前选取的主要指数：上证50，沪深300，中证500，中证1000
today = datetime.datetime.today() - datetime.timedelta(days=0)

tuples = [
    ('上证50', 'sh000016', 'sh510050', 'IH'),
    ('沪深300', 'sh000300', 'sh510300', 'IF'),
    ('中证500', 'sh000905', 'sh510500', 'IC'),
    ('中证1000', 'sh000852', 'sh512100', '')]

result_dict = {}
for name, index, etf, fut_type in tuples:
    stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=index)
    index_pct = (
        stock_zh_index_daily_df.loc[today.strftime('%Y-%m-%d'), 'close'] /
        stock_zh_index_daily_df.shift(1).loc[today.strftime('%Y-%m-%d'), 'close']
        ) - 1 # 忽略分红的影响
    
    fund_etf_hist_sina_df = ak.fund_etf_hist_sina(symbol=etf)
    etf_pct = (
        fund_etf_hist_sina_df.loc[fund_etf_hist_sina_df['date']==today.date(), 'close'].values[0] /
        fund_etf_hist_sina_df.shift(1).loc[fund_etf_hist_sina_df['date']==today.date(), 'close'].values[-1]
        ) - 1 # 会有分红带来的偏差，目前akshare不提供基金分红数据
    
    if fut_type == '':
        future_pct = np.nan
    else:
        # 期货需要解决交割日当日主力合约与当月合约不一致的问题
        futures_today = get_futures_daily_df = ak.get_futures_daily(
            start_date=today.strftime('%Y%m%d'),
            end_date=today.strftime('%Y%m%d'), market="CFFEX")
        day_delta = 1
        futures_yester = pd.DataFrame()
        while futures_yester.shape[0] == 0:
            futures_yester = get_futures_daily_df = ak.get_futures_daily(
                start_date=(today-datetime.timedelta(days=day_delta)).strftime('%Y%m%d'),
                end_date=(today-datetime.timedelta(days=day_delta)).strftime('%Y%m%d'), market="CFFEX")
            day_delta += 1
        future = futures_today.loc[futures_today['symbol'].apply(lambda x: fut_type in x), :].sort_values(by=['turnover']).iloc[-1, :]
        future_pre = futures_yester.loc[futures_yester['symbol']==future['symbol'], :].iloc[0, :]
        future_pct = future['close'] / future_pre['close'] - 1

    result_dict[name] = [index_pct, etf_pct, future_pct]

result = pd.DataFrame(result_dict, index=['指数涨跌幅','ETF涨跌幅','期货涨跌幅']).T

# 作图
fig, ax =plt.subplots(1,1)
data = [list(x) for x in list(result.values)]
columns = tuple(result.columns)
rows = list(result.index)
n_rows = len(data)
cell_text = []
for row in range(n_rows):
    cell_text.append(['%.3f%%' % (x * 100.0) if not np.isnan(x) else '' for x in data[row]])
# Add a table at the bottom of the axes
ax.table(cellText=cell_text,
         rowLabels=rows,
         colLabels=columns,
         loc='center')
ax.axis('tight')
ax.axis('off')
#plt.show()
save_dir = './report_daily/%s/' % today.strftime('%Y%m%d')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
plt.savefig('%smainindex_%s.jpg' % (save_dir, today.strftime('%Y%m%d')))
plt.close()