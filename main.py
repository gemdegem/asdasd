import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Updater
from telegram.error import BadRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

TOKEN = '6438787858:AAGbro59kS8NWAMFugtuuWuQj4YBPxEAz1M'
BASE_URL = "https://t.me/techtokenbot?start="
TELEGRAM_GROUP = "@supremtoken"
user_data = {}

def generate_referral_link(user_id):
    return BASE_URL + str(user_id)

def is_user_member(update, context):
    user_id = update.effective_user.id
    try:
        chat_member = context.bot.get_chat_member(TELEGRAM_GROUP, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except BadRequest as e:
        logger.error(f"Error checking membership: {e.message}")
        return False

def start(update: Update, context: CallbackContext) -> None:
    referral_code = context.args[0] if context.args else None
    if referral_code:
        logger.info(f"User {update.effective_user.id} was referred by {referral_code}")

    try:
        logger.info("Start command received")
        message = """ Welcome to the SUPREM Airdrop bot! 🤖 SUPREM Bot is your next-generation trading companion, designed to optimize decision-making in the dynamic cryptocurrency market through financial derivatives. With an integration of Machine Learning and AI, we deliver precise trading signals, allowing for strategic executions in both bullish and bearish market scenarios. 📈📉

Our bot seamlessly integrates with major trading platforms (binance etc..), elevating your trading experience by automating or tailoring your strategies to your preferences. 🔄

Please complete the required tasks to be eligible to receive airdrop tokens. ✅ 

For Joining, Get - 10  $Tech points 👥 For each referral, Get - 20 $Tech points!

•By engaging, you acknowledge the terms of the SUPREM (Airdrop) Program. For more details, refer to the pinned post. 📌 """

        user_id = update.effective_user.id
        user_data[user_id] = {'stage': 'discord'}

        keyboard = [[InlineKeyboardButton("Next", callback_data='next')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in start: {e}")

def button(update: Update, context: CallbackContext) -> None:
    try:
        logger.info("Button callback received")
        query = update.callback_query
        query.answer()
        user_id = update.effective_user.id

        if user_data[user_id]['stage'] == 'discord':
            # Ask the user to join the Telegram group
            message = f"Please join our Telegram group at [{TELEGRAM_GROUP}]. Once you've joined, press Next."
            user_data[user_id]['stage'] = 'join_tg'
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data='next')]])
            query.edit_message_text(text=message, reply_markup=reply_markup)

        elif user_data[user_id]['stage'] == 'join_tg':
            if is_user_member(update, context):
                message = """
                🔹 Follow our Twitter page <link> ...
    Submit your Twitter ID in the specified format (Example: @username) 📩
                """
                user_data[user_id]['stage'] = 'twitter'
                query.edit_message_text(text=message)
            else:
                message = f"It seems you haven't joined our Telegram group at {TELEGRAM_GROUP} yet. Please join and then press Next."
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data='next')]])
                query.edit_message_text(text=message, reply_markup=reply_markup)

        elif user_data[user_id]['stage'] == 'twitter':
            message = "Please submit your Ethereum wallet address below. 📬 \n\n❌ Do not submit an exchange wallet address ❌"
            user_data[user_id]['stage'] = 'wallet'
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data='next')]])
            query.edit_message_text(text=message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in button: {e}")

def handle_text(update: Update, context: CallbackContext) -> None:
    try:
        logger.info("Text received")
        user_id = update.effective_user.id

        if user_data[user_id]['stage'] == 'twitter':
            user_data[user_id]['twitter'] = update.message.text
            user_data[user_id]['stage'] = 'wallet'
            message = "Please submit your Ethereum wallet address below. 📬 \n\n❌ Do not submit an exchange wallet address ❌"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data='next')]])
            update.message.reply_text(message, reply_markup=reply_markup)

        elif user_data[user_id]['stage'] == 'wallet':
            eth_address = update.message.text

            if len(eth_address) == 42 and eth_address.startswith("0x"):
                user_data[user_id]['wallet'] = eth_address
                twitter_handle = user_data[user_id]['twitter']

                referral_link = generate_referral_link(user_id)

                message = f"""
                Congratulations! You’ve successfully completed the airdrop tasks.

Your current score is 10 XP. Invite more people to increase your chances of winning. 

Your Provided Data
Twitter: {twitter_handle}
ETH Address: {eth_address}

Balance updates every 1 hour.
$ The top 20 referrers will each receive additional $TECH tokens.
Referral link: {referral_link}
                """
                keyboard = [
                    [
                        InlineKeyboardButton("🌐 Website", url="https://yourwebsite.com"),
                        InlineKeyboardButton("🐦 Twitter", url="https://twitter.com/yourpage"),
                        InlineKeyboardButton("📱 Suprem TG", url="https://t.me/supremtoken")
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(message, reply_markup=reply_markup)
            else:
                update.message.reply_text("Invalid Ethereum address. Please enter a valid address.")

    except Exception as e:
        logger.error(f"Error in handle_text: {e}")

def main() -> None:
    try:
        updater = Updater(token=TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start, pass_args=True))
        dp.add_handler(CallbackQueryHandler(button))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

        logger.info("Starting the bot...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()

