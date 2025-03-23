import requests
from datetime import datetime, timedelta
import logging
import sys
from config import WEIBO_CONFIG
from lxml import etree
import json
import math
from time import sleep
import random

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weibo_monitor")

DTFORMAT = "%Y-%m-%dT%H:%M:%S"

class WeiboMonitor:
    def __init__(self, since_date=WEIBO_CONFIG["since_date"], user_id_list=None):
        self.validate_config(WEIBO_CONFIG)
        self.only_crawl_original = WEIBO_CONFIG["only_crawl_original"]
        self.remove_html_tag = WEIBO_CONFIG["remove_html_tag"]
        self.since_date = self.standardize_date_format(since_date)
        self.start_page = WEIBO_CONFIG.get("start_page", 1)
        self.page_weibo_count = WEIBO_CONFIG.get("page_weibo_count", 10)
        self.user_map = WEIBO_CONFIG["user_id_list"]  # {中文名: ID}
        self.user_id_list = user_id_list if user_id_list is not None else list(self.user_map.values())
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Cookie": WEIBO_CONFIG["cookie"],
            # "Referer": "https://m.weibo.cn/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6,ja;q=0.5",
        }
        self.weibo_data = []  # 存储爬取到的微博数据（不写入文件，直接返回）
        self.weibo_id_set = set()  # 用于去重

    def validate_config(self, config):
        """验证配置是否正确（复用 weibo-crawler 逻辑）"""
        argument_list = [
            "only_crawl_original",
            # "original_pic_download", "retweet_pic_download",
            # "original_video_download", "retweet_video_download", "download_comment",
            # "download_repost"
        ]
        for argument in argument_list:
            if config[argument] not in [0, 1]:
                logger.error(f"{argument} 值应为 0 或 1")
                sys.exit()

    def standardize_date_format(self, since_date):
        """标准化日期格式（复用 weibo-crawler 逻辑）"""
        if isinstance(since_date, int):
            since_date = (datetime.today() - timedelta(days=since_date)).strftime(DTFORMAT)
        elif self.is_date(since_date):
            since_date = f"{since_date}T00:00:00"
        elif self.is_datetime(since_date):
            pass
        else:
            logger.error("since_date 格式不正确，应为 yyyy-mm-dd 或 yyyy-mm-ddTHH:MM:SS")
            sys.exit()
        return since_date

    def is_date(self, since_date):
        try:
            datetime.strptime(since_date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def is_datetime(self, since_date):
        try:
            datetime.strptime(since_date, DTFORMAT)
            return True
        except ValueError:
            return False

    def get_json(self, params):
        """获取网页中的 JSON 数据（复用 weibo-crawler）"""
        url = "https://m.weibo.cn/api/container/getIndex?"
        try:
            r = requests.get(url, params=params, headers=self.headers, verify=False, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return {}

    def get_long_weibo(self, weibo_id):
        """获取长微博完整内容（复用 weibo-crawler 逻辑）"""
        for _ in range(5):  # 重试5次
            url = f"https://m.weibo.cn/detail/{weibo_id}"
            try:
                html = requests.get(url, headers=self.headers, verify=False, timeout=10).text
                html = html[html.find('"status":'):]
                html = html[:html.rfind('"call"')]
                html = html[:html.rfind(",")]
                html = "{" + html + "}"
                js = json.loads(html, strict=False)
                weibo_info = js.get("status")
                if weibo_info:
                    return self.parse_weibo(weibo_info)
                # sleep(random.randint(6, 10))  # 失败后随机等待
            except Exception as e:
                logger.error(f"获取长微博 {weibo_id} 失败: {e}")
        logger.warning(f"无法获取长微博 {weibo_id} 的完整内容")
        return None

    def standardize_date(self, created_at):
        """标准化微博发布时间（复用 weibo-crawler 并修复）"""
        if "刚刚" in created_at:
            ts = datetime.now()
        elif "分钟" in created_at:
            minute = int(created_at.split("分钟")[0])
            ts = datetime.now() - timedelta(minutes=minute)
        elif "小时" in created_at:
            hour = int(created_at.split("小时")[0])
            ts = datetime.now() - timedelta(hours=hour)
        elif "昨天" in created_at:
            ts = datetime.now() - timedelta(days=1)
        else:
            created_at = created_at.replace("+0800 ", "")
            try:
                ts = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                ts = datetime.strptime(created_at, "%a %b %d %H:%M:%S %Y")
        return ts.strftime(DTFORMAT)

    def parse_weibo(self, weibo_info):
        """解析单条微博（添加 URL）"""
        weibo = {}
        weibo["id"] = weibo_info["id"]
        weibo["url"] = f"https://m.weibo.cn/detail/{weibo_info['id']}"  # 添加微博 URL
        text_body = weibo_info["text"]
        selector = etree.HTML(f"{text_body}<hr>" if text_body.isspace() else text_body)
        if self.remove_html_tag:
            text_list = selector.xpath("//text()")
            text_list_modified = []
            for i in range(len(text_list)):
                if i > 0 and (text_list[i-1].startswith(('@', '#')) or text_list[i].startswith(('@', '#'))):
                    text_list_modified[-1] += text_list[i]
                else:
                    text_list_modified.append(text_list[i])
            weibo["text"] = "\n".join(text_list_modified)
        else:
            weibo["text"] = text_body
        weibo["created_at"] = self.standardize_date(weibo_info["created_at"])
        weibo["user_id"] = weibo_info["user"]["id"] if weibo_info["user"] else ""
        weibo["screen_name"] = weibo_info["user"]["screen_name"] if weibo_info["user"] else ""
        weibo["source"] = weibo_info.get("source", "")
        weibo["attitudes_count"] = int(weibo_info.get("attitudes_count", 0))
        weibo["comments_count"] = int(weibo_info.get("comments_count", 0))
        weibo["reposts_count"] = int(weibo_info.get("reposts_count", 0))
        return weibo

    def get_one_weibo(self, info):
        """获取一条微博的全部信息（复用 weibo-crawler 并支持长微博）"""
        weibo_info = info["mblog"]
        weibo_id = weibo_info["id"]
        is_long = weibo_info.get("isLongText") or weibo_info.get("pic_num", 0) > 9
        if is_long:
            weibo = self.get_long_weibo(weibo_id)
            if not weibo:
                weibo = self.parse_weibo(weibo_info)
        else:
            weibo = self.parse_weibo(weibo_info)

        if "retweeted_status" in weibo_info and not self.only_crawl_original:
            retweet_info = weibo_info["retweeted_status"]
            retweet_id = retweet_info["id"]
            is_long_retweet = retweet_info.get("isLongText")
            if is_long_retweet:
                retweet = self.get_long_weibo(retweet_id) or self.parse_weibo(retweet_info)
            else:
                retweet = self.parse_weibo(retweet_info)
            weibo["retweet"] = retweet
        return weibo

    def get_page_count(self, user_id):
        """获取微博总页数（参考 weibo-crawler）"""
        params = {"containerid": f"100505{user_id}"}
        js = self.get_json(params)
        if js.get("ok") == 1 and "userInfo" in js["data"]:
            weibo_count = int(js["data"]["userInfo"].get("statuses_count", 0))
            return math.ceil(weibo_count / self.page_weibo_count)
        logger.error(f"无法获取用户 {user_id} 的微博总数")
        return 1  # 默认返回1页

    def get_one_page(self, user_id, page):
        """获取一页微博（复用 weibo-crawler 并增强）"""
        params = {
            "containerid": f"107603{user_id}",
            "page": page,
            "count": self.page_weibo_count
        }
        js = self.get_json(params)
        if js.get("ok") == 1:
            weibos = js["data"]["cards"]
            since_date = datetime.strptime(self.since_date, DTFORMAT)
            for w in weibos:
                if w["card_type"] == 9:
                    wb = self.get_one_weibo(w)
                    if wb["id"] in self.weibo_id_set:
                        continue
                    created_at = datetime.strptime(wb["created_at"], DTFORMAT)
                    if created_at < since_date:
                        return True  # 时间超出范围，结束当前用户
                    self.weibo_data.append(wb)
                    self.weibo_id_set.add(wb["id"])
            return False  # 未超出时间范围，继续下一页
        return True  # 数据获取失败，结束当前用户

    def monitor(self):
        """监控微博（返回数据而非存储，爬取所有页）"""
        self.weibo_data = []
        self.weibo_id_set.clear()
        for user_id in self.user_id_list:
            page_count = self.get_page_count(user_id)
            logger.info(f"开始监控用户 {user_id}，共 {page_count} 页")
            for page in range(self.start_page, page_count + 1):
                is_end = self.get_one_page(user_id, page)
                if is_end:
                    break
                # 随机睡眠，避免被限制
                if page % 5 == 0 and page < page_count:
                    sleep(random.randint(6, 10))
            logger.info(f"用户 {user_id} 监控完成，共获取 {len([w for w in self.weibo_data if w['user_id'] == user_id])} 条微博")
        return self.weibo_data

# 示例使用
if __name__ == "__main__":
    monitor = WeiboMonitor()
    weibo_data = monitor.monitor()
    for wb in weibo_data:
        print(f"用户: {wb['screen_name']}, 时间: {wb['created_at']}, 内容: {wb['text']}, URL: {wb['url']}")