import pandas as pd
import os
import tempfile
import numpy as np

def main(inputs: dict, context):
  # TODO 支持直传 dataframe
  climate_data = pd.read_pickle(inputs["climate_data"])
  
  # TODO 支持直传 dataframe
  weekly_stats = pd.read_pickle(inputs["weekly_stats"])
  
  # 调整1-4月，10-12月正态分布评估标准的标准差范围，数值越小，灾害越多
  sigma1 = inputs["sigma1"]
  
  # 调整5-9月正态分布评估标准的标准差范围，数值越小，灾害越多
  sigma2 = inputs["sigma2"]
  
  # 将日期列转换为日期格式
  climate_data['日期'] = pd.to_datetime(climate_data['日期'], format='%Y%m%d')
  
  # 添加一个新的列来表示每年的周数
  climate_data['周'] = climate_data['日期'].dt.isocalendar().week

  # 筛选出2010年至2020年的数据
  data = climate_data[(climate_data['日期'].dt.year >= inputs["year_from"]) & (climate_data['日期'].dt.year <= inputs["year_to"])]

  data['分类'] = np.select(
      [
          ((data['周'].map(weekly_stats['mean']) + sigma1 * data['周'].map(weekly_stats['std'])) < data[inputs["indicator"]]) & (((data['日期'].dt.month >= 1) & (data['日期'].dt.month <= 4)) | ((data['日期'].dt.month >= 10) & (data['日期'].dt.month <= 12))),
          ((data['周'].map(weekly_stats['mean']) + sigma2 * data['周'].map(weekly_stats['std'])) < data[inputs["indicator"]]) & ((data['日期'].dt.month >= 5) & (data['日期'].dt.month <= 9)),
          ((data['周'].map(weekly_stats['mean']) - sigma1 * data['周'].map(weekly_stats['std'])) > data[inputs["indicator"]]) & (((data['日期'].dt.month >= 1) & (data['日期'].dt.month <= 4)) | ((data['日期'].dt.month >= 10) & (data['日期'].dt.month <= 12))),
          ((data['周'].map(weekly_stats['mean']) - sigma2 * data['周'].map(weekly_stats['std'])) > data[inputs["indicator"]]) & ((data['日期'].dt.month >= 5) & (data['日期'].dt.month <= 9))
      ], 
      inputs["levels"], 
      default='正常'
  )
  
  data['日期'] = pd.to_datetime(data['日期'],format='%Y%m%d')
  data['周'] = data['日期'].dt.isocalendar().week
  data['月'] = data['日期'].dt.month
  data['年'] = data['日期'].dt.year
  data['周'] = data.groupby(['月'])['周'].transform(lambda x: pd.factorize(x)[0] + 1)
  
  # TODO 支持直传 dataframe
  pkl = os.path.join(tempfile.gettempdir(), "classify_data_{}.pkl".format(hash(inputs["climate_data"] + inputs["weekly_stats"])))
  data.to_pickle(pkl)
  
  # TODO 支持直传 dataframe
  context.output(pkl, "disaster", True)
