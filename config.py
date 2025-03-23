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
    "cookie": "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W51sIyEX2_8CMB9OkYILWgJ5NHD95QE1K50S05ESo2NWs4Dqcj.i--ciKL8iKLhi--Xi-zRiKy2i--Ri-2RiKn7i--Xi-zRi-82; _T_WM=57438471825; WEIBOCN_FROM=1110106030; MLOGIN=1; SCF=Al1elmDhgVPzcbnnSPaqCqtsZh4SH3AysshDgIGzj8qk3W3fiYoLF5bkJCjFR_OJS_nNEYz7-xKf63jUzZau3K8.; SUB=_2A25K29wzDeRhGeRH61EW8CzKyjuIHXVpmVH7rDV6PUJbktAbLU32kW1NTa16RQq94u9YY6HpuC4TYGHtmX3C6yIr; SSOLoginState=1742711908; ALF=1745303908; M_WEIBOCN_PARAMS=oid%3D5146730350250605%26lfid%3D231016_-_selffans%26luicode%3D20000174%26uicode%3D20000174; XSRF-TOKEN=6dcb03"          # 替换为实际Cookie
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