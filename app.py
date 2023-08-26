from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,StickerSendMessage,FollowEvent,UnfollowEvent,
)
from linebot.models import *
from database import db_session, init_db
from models.user import Users

app = Flask(__name__)


line_bot_api = LineBotApi('HUuFj/GeLkzih7DL7FNLGEeAf1fJAC9T+rmVhcYoHyy6t+A0u/D3/EGvju5UvNBmBtVqAaOxTrrspTWzSnGC0ATcRXcayIdHUxhUMws/aaEBwe1x44NBfhXLbZ58YPjwdnfUV1KVz8nq4jJAGhs5OAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('83dac60c0a8cee55265f906542bc1e98')


app = Flask(__name__)


#建立或取得user
def get_or_create_user(user_id):
    #從id=user_id先搜尋有沒有這個user，如果有的話就會直接跳到return
    user = db_session.query(Users).filter_by(id=user_id).first()
    #沒有的話就會透過line_bot_api來取得用戶資訊
    if not user:
        profile = line_bot_api.get_profile(user_id)
        #然後再建立user並且存入到資料庫當中
        user = Users(id=user_id, nick_name=profile.display_name, image_url=profile.picture_url)
        db_session.add(user)
        db_session.commit()

    return user


def about_us_event(event):
    emoji = [
            {
                "index": 0,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            },
            {
                "index": 23,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            }
        ]

    text_message = TextSendMessage(text='''$ Super Easy Assistant $
Hello! 您好，歡迎您成為 Super Easy Assistant 的好友！

我是 Your Dear 支付小幫手 

-這裡有超級商場，還可以選購商品喔~
                                   
-直接點選下方各項選單功能

-期待您的光臨！''', emojis=emoji)

    sticker_message = StickerSendMessage(
        package_id='8522',
        sticker_id='16581271'
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message])
    
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
	
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    get_or_create_user(event.source.user_id)
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id
    message_text = str(event.message.text).lower()

##################################使用說明 選單###############################################
    if message_text == '@使用說明':
        about_us_event(event)

    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=''))

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = """  """

if __name__ == "__main__":
    init_db()
    app.run()