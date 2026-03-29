import requests
import time
import csv
import os

# 🚨 记得再次把这里换成你真实的高德 Key
API_KEY = "8813539410d1ce5092ca21c075bc5c45"

def scrape_all_pois(keyword, city="重庆"):
    print(f"🚀 开始全面抓取 {city} 的 '{keyword}' 数据 (Starting full scrape)...")
    
    all_pois = []
    page = 1
    
    # 使用 while 循环实现自动翻页 (While loop for pagination)
    while True:
        print(f"📄 正在抓取第 {page} 页 (Scraping page {page})...")
        # 注意 url 中加入了 page 参数
        url = f"https://restapi.amap.com/v3/place/text?key={API_KEY}&keywords={keyword}&city={city}&output=json&page={page}&offset=20"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    pois = data.get('pois', [])
                    
                    # 如果这一页没有数据了，说明抓取完毕，退出循环
                    if not pois:
                        break 
                    
                    all_pois.extend(pois)
                    page += 1
                    time.sleep(0.5) # 暂停0.5秒，避免请求过快被服务器封禁 (Be polite to the server)
                else:
                    print(f"❌ API 报错: {data.get('info')}")
                    break
            else:
                print("❌ 网络请求失败")
                break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            break

    print(f"✅ 抓取完成！共获取 {len(all_pois)} 条数据 (Total scraped: {len(all_pois)}).")
    return all_pois

def save_to_csv(pois, filename):
    # 构建相对路径，保存到外层的 data 文件夹 (Save to the parent 'data' folder)
    filepath = os.path.join("..", "data", filename)
    print(f"💾 正在保存数据到 (Saving data to) {filepath}...")
    
    # 写入 CSV 文件，注意编码使用 utf-8-sig 以防中文乱码
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头 (Write CSV Headers)
        writer.writerow(['Name', 'Type', 'Address', 'Longitude', 'Latitude'])
        
        for poi in pois:
            name = poi.get('name', '')
            poi_type = poi.get('type', '')
            address = poi.get('address', '')
            
            # 高德返回的 location 格式是 "经度,纬度"，我们需要把它拆开 (Split coordinates)
            location = poi.get('location', '')
            if location:
                lng, lat = location.split(',')
            else:
                lng, lat = '', ''
            
            writer.writerow([name, poi_type, address, lng, lat])
            
    print("🎉 保存成功！(Save complete!)")

if __name__ == "__main__":
    keyword_to_scrape = "轻轨站"
    scraped_data = scrape_all_pois(keyword_to_scrape)
    
    if scraped_data:
        save_to_csv(scraped_data, f"{keyword_to_scrape}_poi.csv")