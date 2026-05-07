import os
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 6891209179
broadcast_mode = {}

bot = telebot.TeleBot(TOKEN)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء جدول المستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    username TEXT,
    balance INTEGER DEFAULT 0
)
""")

conn.commit()

# إضافة أعمدة الإحالة
try:
    cursor.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN referrals_count INTEGER DEFAULT 0")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN referral_earnings INTEGER DEFAULT 0")
except:
    pass

conn.commit()


# القائمة الرئيسية (أزرار كبيرة)
def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton("🏆 ichancy", callback_data="ichancy")
    )

    markup.add(
        InlineKeyboardButton("💰 شحن البوت", callback_data="charge_bot")
    )

    markup.add(
        InlineKeyboardButton("🏧 السحب من البوت", callback_data="withdraw_bot")
    )

    markup.add(
        InlineKeyboardButton("🔁 الإحالات", callback_data="referrals")
    )

    markup.add(
        InlineKeyboardButton("🆘 الدعم", callback_data="support")
    )

    markup.add(
        InlineKeyboardButton("📘 الشروحات", callback_data="tutorials")
    )

    markup.add(
        InlineKeyboardButton("🛠 لوحة الأدمن", callback_data="admin_panel")
    )

    return markup


# قائمة ichancy
def ichancy_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton("💰 رصيد الحساب", callback_data="balance")
    )

    markup.add(
        InlineKeyboardButton("🌐 الشحن إلى الموقع", callback_data="charge_site")
    )

    markup.add(
        InlineKeyboardButton("🏧 السحب من الموقع", callback_data="withdraw_site")
    )

    markup.add(
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )

    return markup


def admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton("👥 عدد المستخدمين", callback_data="admin_users")
    )

    markup.add(
        InlineKeyboardButton("💰 إجمالي الأرصدة", callback_data="admin_balances")
    )

    markup.add(
        InlineKeyboardButton("🔁 الإحالات", callback_data="admin_referrals")
    )

    markup.add(
        InlineKeyboardButton("📢 رسالة جماعية", callback_data="admin_broadcast")
    )

    markup.add(
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )

    return markup


# رسالة البداية
WELCOME_TEXT = """
━━━━━━━━━━━━━━━━━━
🏆 مرحباً بك في بوت الأسطورة CR7 🏆
━━━━━━━━━━━━━━━━━━

🔥 المكان الأقوى للشحن والسحب والخدمات  
⚡ تنفيذ سريع وآمن  
💎 تجربة احترافية بأفضل مستوى  

🚀 اختر من القائمة وابدأ الآن
"""


# أمر start
@bot.message_handler(commands=['start'])
def start(message):

    telegram_id = message.from_user.id
    username = message.from_user.username

    referrer_id = None

    parts = message.text.split()

    if len(parts) > 1:
        referrer_id = parts[1]

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cursor.fetchone()

    if not user:

        cursor.execute(
            "INSERT INTO users (telegram_id, username, referrer_id) VALUES (?, ?, ?)",
            (telegram_id, username, referrer_id)
        )

        conn.commit()

        if referrer_id:

            referral_bonus = 100

            cursor.execute(
                """
                UPDATE users
                SET referrals_count = referrals_count + 1,
                    balance = balance + ?,
                    referral_earnings = referral_earnings + ?
                WHERE telegram_id=?
                """,
                (referral_bonus, referral_bonus, referrer_id)
            )

            conn.commit()

    bot.send_message(
        message.chat.id,
        WELCOME_TEXT,
        reply_markup=main_menu()
    )


# معالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    # قسم ichancy
    if call.data == "ichancy":
        bot.edit_message_text(
            text="🏆 قسم ichancy",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=ichancy_menu()
        )

    # الرجوع للرئيسية مع عبارة الترحيب
    elif call.data == "back_main":
        bot.edit_message_text(
            text=WELCOME_TEXT,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

    # الرصيد
    elif call.data == "balance":

        telegram_id = call.from_user.id

        cursor.execute(
            "SELECT balance FROM users WHERE telegram_id=?",
            (telegram_id,)
        )

        result = cursor.fetchone()

        if result:
            balance = result[0]
        else:
            balance = 0

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            f"💰 رصيد حسابك الحالي: {balance}"
        )

    # شحن الموقع
    elif call.data == "charge_site":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🌐 قسم الشحن إلى الموقع"
        )

    # سحب الموقع
    elif call.data == "withdraw_site":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🏧 قسم السحب من الموقع"
        )

    # شحن البوت
    elif call.data == "charge_bot":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "💰 قسم شحن البوت"
        )

    # سحب البوت
    elif call.data == "withdraw_bot":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🏧 قسم السحب من البوت"
        )

    # الإحالات
    elif call.data == "referrals":

        user_id = call.from_user.id

        cursor.execute(
            "SELECT referrals_count, referral_earnings FROM users WHERE telegram_id=?",
            (user_id,)
        )

        result = cursor.fetchone()

        if result:
            referrals_count = result[0]
            referral_profit = result[1]
        else:
            referrals_count = 0
            referral_profit = 0

        referral_link = f"https://t.me/footballpredict_bot?start={user_id}"

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            f"""🔁 قسم الإحالات

📎 رابط الإحالة الخاص بك:
{referral_link}

👥 عدد الإحالات:
{referrals_count}

💰 أرباح الإحالات:
{referral_profit}"""
        )

    # لوحة الأدمن
    elif call.data == "admin_panel":

        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(
                call.id,
                "⛔ ليس لديك صلاحية"
            )
            return

        bot.edit_message_text(
            text="🛠 لوحة تحكم الأدمن",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=admin_menu()
        )

    elif call.data == "admin_users":

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        bot.send_message(
            call.message.chat.id,
            f"👥 عدد المستخدمين: {total_users}"
        )

    elif call.data == "admin_balances":

        cursor.execute("SELECT SUM(balance) FROM users")
        total_balance = cursor.fetchone()[0]

        if total_balance is None:
            total_balance = 0

        bot.send_message(
            call.message.chat.id,
            f"💰 إجمالي الأرصدة: {total_balance}"
        )

    elif call.data == "admin_referrals":

        cursor.execute("SELECT SUM(referrals_count) FROM users")
        total_referrals = cursor.fetchone()[0]

        if total_referrals is None:
            total_referrals = 0

        bot.send_message(
            call.message.chat.id,
            f"🔁 إجمالي الإحالات: {total_referrals}"
        )

    elif call.data == "admin_broadcast":

        if call.from_user.id != ADMIN_ID:
            return

        broadcast_mode[call.from_user.id] = True

        bot.send_message(
            call.message.chat.id,
            "📢 أرسل الآن الرسالة التي تريد إرسالها لكل المستخدمين"
        )

    # الدعم
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🆘 تواصل مع الدعم:\n@support"
        )

    # الشروحات
    elif call.data == "tutorials":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "📘 قسم الشروحات:\nسيتم إضافة الشروحات هنا"
        )


@bot.message_handler(commands=['addbalance'])
def add_balance(message):

    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ ليس لديك صلاحية")
        return

    parts = message.text.split()

    user_id = int(parts[1])
    amount = int(parts[2])

    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE telegram_id=?",
        (amount, user_id)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "✅ تمت إضافة الرصيد"
    )


@bot.message_handler(commands=['deleteuser'])
def delete_user(message):

    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ ليس لديك صلاحية")
        return

    parts = message.text.split()

    user_id = int(parts[1])

    cursor.execute(
        "DELETE FROM users WHERE telegram_id=?",
        (user_id,)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "✅ تم حذف المستخدم"
    )


print("Bot is running...")

bot.infinity_polling()
