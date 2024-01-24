import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import requests
import json
import pandas as pd
import csv

CHANNEL_ID = 'YOUR_CHANNEL_ID'
IGURL =range(1)
OWNER_ID = 'BOT_OWNER_ID'


JoinMSG = "Joining message"
StartMSG = "Start message"


EndMSG = "Ending message"

WaitMSG = "Waiting message"



async def startcommand(update, context):
    user_id = update.message.chat_id
    CHID = CHANNEL_ID
    user_id = update.message.chat_id
    check = await context.bot.getChatMember(CHID, user_id)
    if check.status in ['creator','administrator','member']:
        da=pd.read_csv("users.csv")
        listusers = da["user"].tolist()
        if user_id not in listusers:
            user=[user_id]
            with open(r'users.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(user)
        await update.message.reply_text(StartMSG)
        return IGURL
    else:
        await update.message.reply_text(JoinMSG)
        return ConversationHandler.END

async def igdown(update, context):
    CID = CHANNEL_ID
    user_id = update.message.chat_id
    check = await context.bot.getChatMember(CHID, user_id)
    if check.status in ['creator','administrator','member']:
        X = update.message.text
        if X == "/cancel":
            await update.message.reply_text(EndMSG)
            return ConversationHandler.END
        if "/stories" in X :
            url1 = "https://instagram-media-downloader.p.rapidapi.com/rapid/stories.php"
        else:
            url1 = "https://instagram-media-downloader.p.rapidapi.com/rapid/post.php"
        url = url1
        querystring = {"url":X}
        headers = {
    	"X-RapidAPI-Key': 'YOUR_RAPID_API_TOKEN",
    	"X-RapidAPI-Host': 'instagram-media-downloader.p.rapidapi.com"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        textToJson = json.loads(response.text)
        try:

            for i in textToJson:
                try:

                    if ".mp4?" in textToJson[i]:
                        must_del = await update.message.reply_text(WaitMSG)

                        req=requests.get(textToJson[i])
                        filename = "video.mp4"
                        with req as rq:
                            with open(filename, 'wb') as file:
                                file.write(rq.content)
                            await context.bot.deleteMessage (message_id = must_del.message_id,
                               chat_id = update.message.chat_id)

                            await update.message.reply_video(video=open(filename, "rb"))
                            return IGURL

                    elif ".jpg?" in textToJson[i]:
                        must_del = await update.message.reply_text(WaitMSG)

                        req=requests.get(textToJson[i])
                        filename ="pic.jpg"
                        with req as rq:
                            with open(filename, "wb") as file:
                                file.write(rq.content)
                            await context.bot.deleteMessage (message_id = must_del.message_id,
                               chat_id = update.message.chat_id)
                            await context.bot.send_photo(chat_id=update.message.chat_id,
                                photo=open(filename,'rb'), caption="")

                    else:
                        print("Error")

                except:
                    
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="")
                    await context.bot.send_message(chat_id=OWNER_ID, text="")



        except:
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text="")
            await context.bot.send_message(chat_id=OWNER_ID, text="")
            return IGURL
        return IGURL
    else:
        await update.message.reply_text(JoinMSG)
        return ConversationHandler.END

async def Cancelcommand(update, context):
    await update.message.reply_text(EndMSG)
    return ConversationHandler.END



def main():

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',startcommand)],
        states =
        {
            IGURL: [MessageHandler(filters.TEXT, igdown)]
        },
        fallbacks=[CommandHandler('cancel', Cancelcommand)]
        )
    

    application = Application.builder().token("YOUR_TOKEN").build()

    application.add_handler(conv_handler)
    
    application.run_polling()
if __name__ == '__main__':
    main()
