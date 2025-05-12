import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional, Union

from app.core.config import settings

# 设置日志
logger = logging.getLogger(__name__)

async def send_email(
    to_email: Union[str, List[str]],
    subject: str,
    body: str,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    is_html: bool = False,
) -> bool:
    """
    发送电子邮件
    
    参数:
        to_email: 收件人邮箱，可以是单个邮箱或邮箱列表
        subject: 邮件主题
        body: 邮件正文
        cc: 抄送，可以是单个邮箱或邮箱列表
        bcc: 密送，可以是单个邮箱或邮箱列表
        is_html: 是否为HTML格式
    
    返回:
        发送结果
    """
    # 确保收件人是列表
    recipients = [to_email] if isinstance(to_email, str) else to_email
    
    # 处理抄送和密送
    cc_list = []
    if cc:
        cc_list = [cc] if isinstance(cc, str) else cc
    
    bcc_list = []
    if bcc:
        bcc_list = [bcc] if isinstance(bcc, str) else bcc
    
    # 开发环境模拟发送邮件
    if settings.APP_ENV == "development" and not settings.SMTP_PASSWORD:
        logger.info("开发环境，模拟发送邮件")
        logger.info(f"收件人: {', '.join(recipients)}")
        if cc_list:
            logger.info(f"抄送: {', '.join(cc_list)}")
        if bcc_list:
            logger.info(f"密送: {', '.join(bcc_list)}")
        logger.info(f"主题: {subject}")
        logger.info(f"内容类型: {'HTML' if is_html else '纯文本'}")
        logger.info(f"内容: \n{body}")
        
        # 将模拟邮件保存到文件，方便开发测试
        try:
            dev_mail_dir = Path("logs/dev_emails")
            dev_mail_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = dev_mail_dir / f"email_{timestamp}.txt"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"收件人: {', '.join(recipients)}\n")
                if cc_list:
                    f.write(f"抄送: {', '.join(cc_list)}\n")
                if bcc_list:
                    f.write(f"密送: {', '.join(bcc_list)}\n")
                f.write(f"主题: {subject}\n")
                f.write(f"内容类型: {'HTML' if is_html else '纯文本'}\n")
                f.write(f"内容: \n{body}\n")
            
            logger.info(f"模拟邮件已保存到: {file_path}")
        except Exception as e:
            logger.warning(f"保存模拟邮件失败: {str(e)}")
        
        return True
    
    try:
        # 创建邮件消息
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["Subject"] = subject
        
        # 设置收件人、抄送和密送
        msg["To"] = ", ".join(recipients)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        
        # 所有收件人列表，用于实际发送
        all_recipients = recipients + cc_list + bcc_list
        
        # 添加邮件正文
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))
        
        logger.info(f"准备发送邮件到: {', '.join(recipients)}")
        
        # 连接到SMTP服务器并发送邮件
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg, from_addr=settings.SMTP_USER, to_addrs=all_recipients)
            
            logger.info(f"邮件发送成功: 收件人={', '.join(recipients)}, 主题={subject}")
            return True
            
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        # 在生产环境中可能需要通过其他方式通知管理员
        if settings.APP_ENV == "production":
            # 这里可以添加生产环境中的错误处理，如通知管理员
            pass
        return False 