# 监控的微博ID列表和相关配置
WEIBO_CONFIG = {
    "user_id_list": {
        "新浪保险频道": "2374872491",
        "微博保险": "6575331962",
        "每天学点保险知识":"2277893221",
        "保险前线观察员": "6143266895",
    },  # 要监控的微博ID
    "only_crawl_original": 0,        # 0: 爬取全部微博，1: 只爬原创
    "since_date": "2025-03-22",      # 起始时间
    "start_page": 1,                 # 开始页码
    "page_weibo_count": 10,          # 每页微博数
    "remove_html_tag": 1,            # 移除HTML标签
    "cookie": ""          # 替换为实际Cookie
}

# 发布平台配置
MY_WEIBO_ACCOUNT = {
    "username": "你的微博用户名",
    "password": "你的微博密码"
}
TOUTIAO_ACCOUNT = {
    "username": "你的头条用户名",
    "password": "你的头条密码"
}

# 大语言模型API配置
LLM_API_KEY = "YOUR_API_KEY"  # 替换为实际API密钥
LLM_API_ENDPOINT = "https://api.xai.com/grok3/rewrite"  # 替换为实际API地址
