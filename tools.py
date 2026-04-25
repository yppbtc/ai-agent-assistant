"""
工单处理工具模块
包含工单保存和邮件发送功能
"""

from crewai.tools import tool
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import json

# 发件人配置（从环境变量读取，不要硬编码）
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "客服中心")
FROM_ADDR = os.getenv("EMAIL_FROM_ADDR", "your_email@qq.com")
FROM_PWD = os.getenv("EMAIL_PWD")  # 在 .env 文件中配置
@tool("保存工单到文件")
def save_ticket_to_file(ticket_content: str) -> str:
    """
    将处理后的工单内容保存到本地文件中
    """
    try:
        # 创建目录（如果不存在）
        os.makedirs("./tickets", exist_ok=True)
        # 用时间戳作为文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./tickets/ticket_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(ticket_content)
        return f"工单已保存到 {filename}"
    except Exception as e:
        return f"保存失败: {str(e)}"

@tool("发送工单处理结果到邮箱")
def send_ticket_result(ticket_info: str) -> str:
    """
    将工单处理结果发送到客户邮箱
    参数 ticket_info 应该包含客户邮箱和处理结果
    """
    srv = None
    try:
        # 解析传入的工单信息（期望是JSON格式）
        info = json.loads(ticket_info) if isinstance(ticket_info, str) else ticket_info
        # 发件人配置（请改成你自己的）
        from_name = "客服中心"
        from_addr = "2514686093@qq.com"
        from_pwd = "rfgmdjttygurecha"
        to_addr = info.get("customer_email", "你自己的邮箱2514686093@qq.com")
        ticket_result = info.get("result", "处理结果")
        # 邮件标题
        my_title = f"工单处理结果 - {datetime.datetime.now().strftime('%Y-%m-%d')}"
        # 邮件正文
        my_msg = f"""
        尊敬的客户：

        您的工单已处理完成。

        处理结果：
        {ticket_result}

        感谢您的反馈，祝您生活愉快！

        客服中心
        {datetime.datetime.now().strftime('%Y-%m-%d')}
        """

        msg = MIMEText(my_msg, 'plain', 'utf-8')
        msg['From'] = formataddr([from_name, from_addr])
        msg['Subject'] = my_title

        smtp_srv = "smtp.qq.com"
        srv = smtplib.SMTP_SSL(smtp_srv.encode(), 465, timeout=30)
        srv.login(from_addr, from_pwd)
        srv.sendmail(from_addr, [to_addr], msg.as_string())
        srv.quit()

        return f"工单结果已发送至 {to_addr}"
    except Exception as e:
        return f"发送失败: {str(e)}"
    finally:
        if srv is not None:
            try:
                srv.quit()
            except Exception:
                pass
