import re
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters

# 配置日志格式
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义默认配置
DEFAULT_CONFIG = {
    'bot_token': '机器人API',
    'start_message': '欢迎使用消息处理机器人!我将自动处理所有加入的群组和频道中的消息。',
    'edit_empty_message': '.',
    'ignore_message_types': ['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact', 'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message']
}

# 处理 /start 命令
async def start(update: Update, context: Application):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=context.bot_data['config']['start_message'])

# 处理消息
async def process_message(update: Update, context: Application):
    message = update.message or update.channel_post
    if not message:
        return

    # 忽略非文本消息
    if message.content_type in context.bot_data['config']['ignore_message_types']:
        logger.info(f"Ignoring message of type {message.content_type}")
        return

    logger.info(f"Received message: {message}")

    text = message.text or message.caption
    if text:
        # 根据正则表达式替换文本
        new_text = re.sub(r'输入正则表达式（也就是你要删除的内容）', '', text).strip()
        if not new_text:
            new_text = context.bot_data['config']['edit_empty_message']
        if new_text != text:
            logger.info(f"Editing message: {message.message_id}")
            if message.text:
                await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=new_text)
            else:
                await context.bot.edit_message_caption(chat_id=message.chat_id, message_id=message.message_id, caption=new_text)
        else:
            logger.info("No change in message text, not editing")

# 主函数
def main():
    # 从默认配置创建配置字典
    config = DEFAULT_CONFIG.copy()

    application = Application.builder().token(config['bot_token']).build()
    
    # 将配置存储在bot_data中
    application.bot_data['config'] = config

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    message_handler = MessageHandler(filters.ChatType.GROUPS | filters.ChatType.CHANNEL, process_message)
    application.add_handler(message_handler)

    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()