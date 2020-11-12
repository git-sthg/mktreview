# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:26:09 2020

@author: FTAsset
"""

import os
import datetime
import akshare as ak
import pandas as pd
import numpy as np
#from scipy import stats
import matplotlib.pyplot as plt

today = datetime.datetime.today() - datetime.timedelta(days=0)
stock_zh_a_spot_df = ak.stock_zh_a_spot()

x = stock_zh_a_spot_df['changepercent'].apply(lambda x: max(x, 100)) # 为了避免极端值影响观感，超过100%的涨幅按100%计
y = stock_zh_a_spot_df['turnoverratio']

def scatter_hist(x, y, ax, ax_histx, ax_histy):
    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histx.minorticks_on()
    ax_histy.tick_params(axis="y", labelleft=False)
    ax_histy.minorticks_on()
    # the scatter plot:
    ax.scatter(x, y, alpha=0.3)
    # now determine nice limits by hand:
    x_bins = np.arange(-20, 20, 40/200)
    y_bins = np.arange(0, 30, 30/200)
    ax_histx.hist(x, bins=x_bins)
    ax_histy.hist(y, bins=y_bins, orientation='horizontal')
    # 辅助线
    med = x.median()
    color = 'red' if med >= 0 else 'green'
    ax.axvline(x=x.median() , color=color , linestyle='--')

left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
spacing = 0.005
rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom + height + spacing, width, 0.2]
rect_histy = [left + width + spacing, bottom, 0.2, height]

# 作图
fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes(rect_scatter)
ax_histx = fig.add_axes(rect_histx, sharex=ax)
ax_histy = fig.add_axes(rect_histy, sharey=ax)

# 添加坐标轴标签
scatter_hist(x, y, ax, ax_histx, ax_histy)
ax.set_xlabel('涨跌幅(%)', fontsize=15)
ax.set_ylabel("换手率(%)", fontsize=15)
ax.set_title('涨跌幅与换手率频次统计%s' % today.strftime('%Y%m%d'))
#plt.show()
save_dir = './report_daily/%s/' % today.strftime('%Y%m%d')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
plt.savefig('%sindividual_%s.jpg' % (save_dir, today.strftime('%Y%m%d')))
plt.close()