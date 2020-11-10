# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 09:10:20 2020

@author: FTAsset
"""

import os
import datetime
import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

today = datetime.datetime.today() - datetime.timedelta(days=0)
yearsb4 = today - datetime.timedelta(days=365*3+1)
start_str = yearsb4.strftime('%Y-%m-%d')
end_str = today.strftime('%Y-%m-%d')

def get_index_daily(index_code, start_date, end_date):
    """ index_code: str, 6位申万一级行业代码 如：801010
    start_date: str, 开始日期 yyyy-mm-dd
    end_date: str, 结束日期 yyyy-mm-dd
    ----------------------------------------------
    return: pd.DataFrame, 指数名称、涨跌幅（%）、流通市值、换手率分位数（%）、市盈率分位数（%）
    """
    print('\r正在获取指数代码：%s' % index_code, end="")
    sw_index_df = ak.sw_index_daily_indicator(index_code=index_code, start_date=start_date, end_date=end_date, data_type="Day")
    pct = pd.concat([
        sw_index_df.loc[sw_index_df['date']==end_str, ['index_name']], 
        sw_index_df.loc[sw_index_df['date']==end_str, ['chg_pct']].astype(float), 
        sw_index_df.loc[sw_index_df['date']==end_str, 'float_mv'].apply(lambda x: float(x.replace(',',''))), # 流通市值
        sw_index_df[['turn_rate', 'pe']].rank(method='min', pct=True).loc[sw_index_df['date']==end_str]*100 # 换手率和市盈率分位数
        ], axis='columns')
    return(pct)

sw_index_spot_df = ak.sw_index_spot()
index_pct = pd.concat(
    [get_index_daily(code, start_str, end_str) for row, code in enumerate(sw_index_spot_df['指数代码'])],
    ignore_index=True)
print()
# 作图

x = index_pct['chg_pct']
y = index_pct['pe']
c = index_pct['turn_rate']
s = (index_pct['float_mv']/min(index_pct['float_mv']))*10
a = index_pct['index_name']

fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(x, y, c=c, s=s, alpha=0.5, cmap='cool')

# 添加数据点标签
for i in range(index_pct.shape[0]):
    plt.annotate(a.iloc[i], xy = (x[i], y[i]), xytext = (x[i]+0.1, y[i]+0.1)) 
# 添加颜色图例
legend1 = ax.legend(*scatter.legend_elements(num=5),
                    loc="lower right", bbox_to_anchor=(0.87, 0), title='换手率3年分位数(%)')
ax.add_artist(legend1)
# 添加大小图例
kw = dict(prop="sizes", num=6, color=scatter.cmap(0.5),
          func=lambda s: (s/10)*min(index_pct['float_mv']))
legend2 = ax.legend(*scatter.legend_elements(**kw),
                    loc="lower right", bbox_to_anchor=(1, 0), title="行业流通市值(亿元)")

ax.set_xlabel('行业涨跌幅(%)', fontsize=15)
ax.set_ylabel("PE 3年分位数(%)", fontsize=15)
ax.set_title('申万一级行业收益分布')

ax.grid(True)
fig.tight_layout()
save_dir = './report_daily/%s/' % today.strftime('%Y%m%d')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
plt.savefig('%sindustry_%s.jpg' % (save_dir, today.strftime('%Y%m%d')))
#plt.show()
plt.close()
