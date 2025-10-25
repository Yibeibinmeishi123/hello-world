import re
import time
import requests
import csv
from lxml import etree


# 提取出版年函数（完全保留你的代码）
def extract_year(date_str):
    # 清理字符串，保留数字、横线和点
    cleaned = re.sub(r'[^\d.-]', '', date_str)
    # 提取年份（匹配开头的4位数字）
    match = re.match(r'\d{4}', cleaned)
    if match:
        return int(match.group())
    # 处理特殊情况
    return None


# 封装页面请求函数（对应你原来的requests部分）
def get_page_html(p):
    url = 'https://www.douban.com/doulist/1364866/?'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/139.0.0.0 Safari/537.36',
        'referer': 'https://www.douban.com/doulist/1364866/?start=25&sort=seq&playable=0&sub_type='
    }
    param = {
        'start': p,
        'sort': 'seq',
        'playable': 0,
        'sub_type': ''
    }
    try:
        response = requests.get(url, headers=header, params=param, timeout=10)
        if response.status_code == 200:
            print(f"=====================正在采集第{int(p / 25) + 1}页面数据====================")
            return response.text
        else:
            print(f"第{int(p / 25) + 1}页请求失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"第{int(p / 25) + 1}页请求出错：{str(e)}")
        return None


# 封装单页数据解析函数（完全保留你的提取逻辑）
def parse_html_to_data(html):
    result_data = etree.HTML(html).xpath('//div[@id="content"]/div/div/div[@class="doulist-item"]')
    page_books = []
    for data in result_data:
        try:
            # 书名
            book_name = data.xpath('./div/div[2]/div[3]/a/text()')[0].strip()
            # 评分
            book_rate = data.xpath('./div/div[2]/div[4]/span[2]/text()')
            book_rate_result = book_rate[0] if len(book_rate) > 0 else None
            # 评价数量
            number_of_evaluations = data.xpath('./div/div[2]/div[4]/span[3]/text()')[0]
            evaluations_result = int(re.search(r'\d+', number_of_evaluations).group())
            # 作者
            author = data.xpath('./div/div[2]/div[5]/text()')[0]
            author_result = author.split(":")[1].strip()
            # 出版社
            publication_house = data.xpath('./div/div[2]/div[5]/text()')[1]
            publication_house_data = publication_house.split(":")[1].strip()
            # 出版年
            publication_year = data.xpath('./div/div[2]/div[5]/text()')[2]
            publication_year_raw = publication_year.split(":")[1].strip()
            publication_year_result = extract_year(publication_year_raw)
            # 评语
            comment = data.xpath('./div/div[3]/div/blockquote/text()')[1].strip()

            # 保存单本书数据
            page_books.append({
                "书名": book_name,
                "评分": book_rate_result,
                "评价数量": evaluations_result,
                "作者": author_result,
                "出版社": publication_house_data,
                "出版年": publication_year_result,
                "评语": comment
            })
            print(book_name)  # 保留你原来的打印书名逻辑
        except Exception as e:
            print(f"解析单本书籍出错：{str(e)}")
            continue  # 出错不中断，继续解析下一本
    return page_books


# 封装CSV保存函数
def save_data_to_csv(all_data, filename="douban_books.csv"):
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ["书名", "评分", "评价数量", "作者", "出版社", "出版年", "评语"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"所有数据已保存到{filename}，共{len(all_data)}条")
    except Exception as e:
        print(f"保存CSV出错：{str(e)}")


# 主函数：按你的原始循环逻辑执行
def main():
    all_books = []
    # 完全保留你原来的循环范围：0到925，步长25
    for p in range(0, 925, 25):
        # 获取页面HTML
        html = get_page_html(p)
        if not html:
            time.sleep(2)  # 失败后稍等再继续
            continue
        # 解析页面数据
        page_data = parse_html_to_data(html)
        all_books.extend(page_data)
        # 控制爬取速度
        time.sleep(1.5)
    # 保存所有数据
    save_data_to_csv(all_books)


if __name__ == "__main__":
    main()
