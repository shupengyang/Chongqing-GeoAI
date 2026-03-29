import csv
import math
import os

# 定义椭球体参数 (Ellipsoid Parameters)
pi = 3.1415926535897932384626
a = 6378245.0  # 半长轴
ee = 0.00669342162296594323  # 偏心率平方

def gcj02_to_wgs84(lng, lat):
    """
    将 GCJ-02 (高德/腾讯坐标) 转换为 WGS-84 (标准地理坐标)
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return lng * 2 - mglng, lat * 2 - mglat

def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    # 粗略判断是否在国内，如果在国外则不需要转换
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)

def process_csv(input_file, output_file):
    print(f"🔄 正在读取并清洗数据 (Processing data): {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8-sig') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
         
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 读取并写入表头，增加两个新字段
        headers = next(reader)
        headers.extend(['WGS84_Lng', 'WGS84_Lat'])
        writer.writerow(headers)
        
        count = 0
        for row in reader:
            # 假设第4列是经度，第5列是纬度 (索引从0开始: 3=Lng, 4=Lat)
            try:
                lng = float(row[3])
                lat = float(row[4])
                
                # 执行坐标转换算法
                wgs_lng, wgs_lat = gcj02_to_wgs84(lng, lat)
                
                # 将转换后的坐标追加到行尾
                row.extend([round(wgs_lng, 6), round(wgs_lat, 6)])
                writer.writerow(row)
                count += 1
            except ValueError:
                # 跳过没有坐标的空行
                continue
                
    print(f"✅ 数据清洗完毕！成功转换 {count} 条数据 (Successfully converted {count} records).")
    print(f"💾 已保存为新文件: {output_file}")

if __name__ == "__main__":
    # 设置输入输出路径 (相对于 scripts 文件夹)
    input_csv = os.path.join("..", "data", "轻轨站_poi.csv")
    output_csv = os.path.join("..", "data", "轻轨站_poi_wgs84.csv")
    
    if os.path.exists(input_csv):
        process_csv(input_csv, output_csv)
    else:
        print(f"❌ 找不到输入文件 (File not found): {input_csv}")