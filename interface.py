import gradio as gr
from monitor.weibo import WeiboMonitor
from content_rewriter import ContentRewriter
from publisher.publisher import Publisher
from config import WEIBO_CONFIG

rewriter = ContentRewriter()
publisher = Publisher()

def update_content(since_date, selected_users):
    # 从配置文件中获取用户映射
    user_map = WEIBO_CONFIG["user_id_list"]
    # 将选中的中文名转换为 ID 列表
    if not selected_users:  # 如果未选择，则爬取所有用户
        user_id_list = list(user_map.values())
    else:
        user_id_list = [user_map[user] for user in selected_users if user in user_map]

    # 初始化 WeiboMonitor，传入动态的 user_id_list
    monitor = WeiboMonitor(since_date=since_date, user_id_list=user_id_list)
    weibo_data = monitor.monitor()
    original_output = []
    rewritten_output = []
    for wb in weibo_data:
        rewritten = rewriter.rewrite(wb["text"])
        original_output.append(
            f"用户ID: {wb['user_id']}\n昵称: {wb['screen_name']}\n时间: {wb['created_at']}\n原文: {wb['text']}\nURL: {wb['url']}"
        )
        rewritten_output.append(
            f"用户ID: {wb['user_id']}\n昵称: {wb['screen_name']}\n时间: {wb['created_at']}\n改写: {rewritten}\nURL: {wb['url']}"
        )
    original_text = "\n\n".join(original_output) if original_output else "暂无新内容"
    rewritten_text = "\n\n".join(rewritten_output) if rewritten_output else "暂无新内容"
    return original_text, rewritten_text

def publish_content(platform, content):
    if platform == "微博":
        return publisher.publish_to_weibo(content)
    elif platform == "今日头条":
        return publisher.publish_to_toutiao(content)
    return "请选择平台"

with gr.Blocks(title="微博监控与发布") as demo:
    gr.Markdown("# 微博监控与内容发布系统")

    # 第一行：微博平台用户选择（多选）
    user_names = list(WEIBO_CONFIG["user_id_list"].keys())
    # with gr.Row():
    #     gr.Markdown("## 微博平台用户选择")
    with gr.Row():
        user_selector = gr.CheckboxGroup(
            choices=user_names,
            label="微博监控博主",
            value="每天学点保险知识"
        )

    # 第二行：起始时间输入
    with gr.Row():
        since_date_input = gr.Textbox(
            label="起始时间 (YYYY-MM-DD)",
            value="2025-03-21",
            placeholder="输入起始时间，例如 2025-03-21"
        )

    # 第三行：两列布局（原始内容和改写内容）
    with gr.Row():
        with gr.Column(scale=1):
            original_output = gr.Textbox(label="爬取的原始内容", lines=15, max_lines=20)
        with gr.Column(scale=1):
            rewritten_output = gr.Textbox(label="改写后的内容", lines=15, max_lines=20)

    # 刷新按钮
    refresh_btn = gr.Button("刷新监控")

    # 最后一行：发布平台和内容
    with gr.Row():
        platform = gr.Dropdown(["微博", "今日头条"], label="发布平台", value=None)
        publish_content_input = gr.Textbox(label="待发布内容", lines=5)
    with gr.Row():
        publish_btn = gr.Button("发布")
        publish_result = gr.Textbox(label="发布结果")

    # 事件绑定
    refresh_btn.click(
        fn=update_content,
        inputs=[since_date_input, user_selector],
        outputs=[original_output, rewritten_output]
    )
    publish_btn.click(
        fn=publish_content,
        inputs=[platform, publish_content_input],
        outputs=publish_result
    )

def start_interface():
    demo.launch()

if __name__ == "__main__":
    start_interface()