import asyncio
from gemini_pro_bot.llm import model, img_model
from google.generativeai.types.generation_types import (
    StopCandidateException,
    BlockedPromptException,
)
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from telegram.error import NetworkError, BadRequest
from telegram.constants import ChatAction, ParseMode
from gemini_pro_bot.html_format import format_message
import PIL.Image as load_image
from io import BytesIO


def new_chat(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["chat"] = model.start_chat()


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """当接收到 /start 命令时响应："""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n快来和我聊天吧！\n\n发送 /new 开始新的聊天会话",
        # reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """当接收到 /help 命令时响应："""
    help_text = """
命令提示:

/start - 开始聊天
/help - 获得帮助
/new - 开始新的聊天会话（并清理之前生成的消息）

请向机器人发送消息以获得回答.
"""
    await update.message.reply_text(help_text)


async def newchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """开始新的聊天会话"""
    init_msg = await update.message.reply_text(
        text="正在初始化...",
        reply_to_message_id=update.message.message_id,
    )
    new_chat(context)
    await init_msg.edit_text("新的对话已生成！")


# Define the function that will handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理来自用户的传入信息。

     检查用户是否存在聊天会话，如果不存在则初始化新会话。
     将用户的消息发送到聊天会话以生成响应。
     将响应流式传输回用户，处理任何错误。
    """
    if context.chat_data.get("chat") is None:
        new_chat(context)
    text = update.message.text
    init_msg = await update.message.reply_text(
        text="请稍候...", reply_to_message_id=update.message.message_id
    )
    await update.message.chat.send_action(ChatAction.TYPING)
    # Generate a response using the text-generation pipeline
    chat = context.chat_data.get("chat")  # Get the chat session for this chat
    response = None
    try:
        response = await chat.send_message_async(
            text, stream=True
        )  # Generate a response
    except StopCandidateException as sce:
        print("提示：", text, " 停止！用户: ", update.message.from_user)
        print(sce)
        await init_msg.edit_text("连接意外中断！")
        chat.rewind()  # Rewind the chat session to prevent the bot from getting stuck
        return
    except BlockedPromptException as bpe:
        print("提示：", text, " 停止！用户: ", update.message.from_user)
        print(bpe)
        await init_msg.edit_text("可能是出于安全考虑而被阻止。")
        if response:
            # Resolve the response to prevent the chat session from getting stuck
            await response.resolve()
        return
    full_plain_message = ""
    # Stream the responses
    async for chunk in response:
        try:
            if chunk.text:
                full_plain_message += chunk.text
                message = format_message(full_plain_message)
                init_msg = await init_msg.edit_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        except StopCandidateException as sce:
            await init_msg.edit_text("连接意外中断！")
            chat.rewind()  # Rewind the chat session to prevent the bot from getting stuck
            continue
        except BadRequest:
            await response.resolve()  # Resolve the response to prevent the chat session from getting stuck
            continue
        except NetworkError:
            raise NetworkError(
                "网络错误，请稍候再试！"
            )
        except IndexError:
            await init_msg.reply_text(
                "发生一些索引错误，无法响应！"
            )
            await response.resolve()
            continue
        except Exception as e:
            print(e)
            if chunk.text:
                full_plain_message = chunk.text
                message = format_message(full_plain_message)
                init_msg = await update.message.reply_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=init_msg.message_id,
                    disable_web_page_preview=True,
                )
        # Sleep for a bit to prevent the bot from getting rate-limited
        await asyncio.sleep(0.1)


async def handle_image(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """处理带有标题的传入图像并生成响应。"""
    init_msg = await update.message.reply_text(
        text="请稍候...", reply_to_message_id=update.message.message_id
    )
    images = update.message.photo
    unique_images: dict = {}
    for img in images:
        file_id = img.file_id[:-7]
        if file_id not in unique_images:
            unique_images[file_id] = img
        elif img.file_size > unique_images[file_id].file_size:
            unique_images[file_id] = img
    file_list = list(unique_images.values())
    file = await file_list[0].get_file()
    a_img = load_image.open(BytesIO(await file.download_as_bytearray()))
    prompt = None
    if update.message.caption:
        prompt = update.message.caption
    else:
        prompt = "正在分析图像并生成回复..."
    response = await img_model.generate_content_async([prompt, a_img], stream=True)
    full_plain_message = ""
    async for chunk in response:
        try:
            if chunk.text:
                full_plain_message += chunk.text
                message = format_message(full_plain_message)
                init_msg = await init_msg.edit_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        except StopCandidateException:
            await init_msg.edit_text("连接意外中断！")
        except BadRequest:
            await response.resolve()
            continue
        except NetworkError:
            raise NetworkError(
                "网络错误，请稍候再试！"
            )
        except IndexError:
            await init_msg.reply_text(
                "发生一些索引错误，无法响应！"
            )
            await response.resolve()
            continue
        except Exception as e:
            print(e)
            if chunk.text:
                full_plain_message = chunk.text
                message = format_message(full_plain_message)
                init_msg = await update.message.reply_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=init_msg.message_id,
                    disable_web_page_preview=True,
                )
        await asyncio.sleep(0.1)
