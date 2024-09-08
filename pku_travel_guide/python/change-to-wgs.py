import coordTransform as ct
import pandas as pd

# 读取CSV文件
df = pd.read_csv('../data/restaurant.csv',encoding='utf-8')

# 定义转换函数
def gcj02_to_wgs84(lon, lat):
    return ct.gcj02_to_wgs84(lon, lat)

# 应用转换函数到每一行
df['wgs_lon'], df['wgs_lat'] = zip(*df.apply(lambda row: gcj02_to_wgs84(row['lon'], row['lat']), axis=1))

# 保存转换后的坐标到新的CSV文件
df.to_csv('../data/restaurant_84.csv', index=False,encoding='utf-8-sig')

print("转换完成，结果已保存到 'restaurant_84.csv'")