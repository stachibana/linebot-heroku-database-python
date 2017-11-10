# -*- coding: utf-8 -*-
import sys
sys.path.append('./vendor')

import os

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)

from urllib import parse
import psycopg2
import psycopg2.extras

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

#@app.route("/callback", methods=['POST'])
@app.route("/", methods=['POST'])
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
    if event.type == "message":
        if event.message.type == "text":
            profile = line_bot_api.get_profile(event.source.user_id)
            displayName = profile.display_name
            if event.message.text == "last":
                conn = getDBConnection()
                cur = conn.cursor()
                result = get_dict_resultset(conn, "select * from users;")
                row = result[0]
                if row:
                    print(row)
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(text=row["lastmessage"])
                        ]
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(text="no history")
                        ]
                    )
            else:
                conn = getDBConnection()
                cur = conn.cursor()
                cur.execute("insert into users (userid, lastmessage) values(%s, %s) on conflict on constraint users_pkey do update set lastmessage = %s;", (event.source.user_id, event.message.text, event.message.text))
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text="Message saved. Send \'last\' to show."),
                    ]
                )
                conn.commit()
                cur.close()

def get_dict_resultset(conn, sql):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute (sql)
    resultset = cur.fetchall()
    dict_result = []
    for row in resultset:
        dict_result.append(dict(row))
    return dict_result

def getDBConnection():
    parse.uses_netloc.append("postgres")
    url = parse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

if __name__ == "__main__":
    app.debug = True;
    app.run()
