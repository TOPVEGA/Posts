from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import re
import logging
from datetime import datetime, timedelta
import json
import os
import time

"""
• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ ₂₀₁₅  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
"""


API_ID = 1846213  
API_HASH = "c545c613b78f18a30744970910124d53"  
BOT_TOKEN = "812267267xxxxxxxxxxx"  #توكن الجديد
CHANNEL_USERNAME = "@Python2015" #قناه مخصصه الاعلانات 
OWNER_ID = 7654641648 #ايدي مالك

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if not os.path.exists("topvega"):
    os.makedirs("topvega")
topvega_FILE = "topvega/ads_topvega.json"


PRICE_LIST = {
    1: {"price": 5, "label": "1 ساعة - 5 جنيه"},
    2: {"price": 8, "label": "2 ساعات - 8 جنيه"},
    3: {"price": 10, "label": "3 ساعات - 10 جنيه"},
    4: {"price": 12, "label": "4 ساعات - 12 جنيه"},
    5: {"price": 15, "label": "5 ساعات - 15 جنيه"},
    10: {"price": 25, "label": "10 ساعات - 25 جنيه"},
    24: {"price": 40, "label": "24 ساعة - 40 جنيه"},
    48: {"price": 70, "label": "48 ساعة - 70 جنيه"}
}
def load_topvega():
    try:
        with open(topvega_FILE, "r", encoding="utf-8") as f:
            topvega = json.load(f)
            if "stats" not in topvega:
                topvega["stats"] = {"total_ads": 0, "approved_ads": 0, "rejected_ads": 0}
            if "pending_ads" not in topvega:
                topvega["pending_ads"] = {}
            if "active_ads" not in topvega:
                topvega["active_ads"] = {}
            if "user_states" not in topvega:
                topvega["user_states"] = {}
            return topvega
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pending_ads": {}, "active_ads": {}, "user_states": {}, "stats": {"total_ads": 0, "approved_ads": 0, "rejected_ads": 0}}
def save_topvega(topvega):
    with open(topvega_FILE, "w", encoding="utf-8") as f:
        json.dump(topvega, f, ensure_ascii=False, indent=4)

app = Client("adbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: types.Message):
    user_id = message.from_user.id
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["left", "kicked"]:
         
            await message.reply_text(
                "⚠️ يجب عليك الاشتراك في قناتنا أولاً لاستخدام البوت:\n"
                f"{CHANNEL_USERNAME}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                    [InlineKeyboardButton("تحقق من الاشتراك", callback_topvega="check_subscription")]
                ])
            )
            return
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
    await message.reply_text(
        "✨ **مرحبًا بك في بوت الإعلانات** ✨\n\n"
        "يمكنك نشر إعلانك في قناتنا عن طريق هذا البوت.\n\n"
        "اختر نوع الإعلان الذي تريد نشره:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(" إعلان نصي", callback_topvega="ad_text")],
            [InlineKeyboardButton(" إعلان بصورة", callback_topvega="ad_photo")],
            [InlineKeyboardButton(" إعلان بملف", callback_topvega="ad_document")],
            [InlineKeyboardButton(" قائمة الأسعار", callback_topvega="price_list")],
            [InlineKeyboardButton(" الإحصائيات", callback_topvega="stats")],
            [InlineKeyboardButton(" معلومات", callback_topvega="info")]
        ])
    )


@app.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client: Client, callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["left", "kicked"]:
            await callback_query.answer("لم تشترك بعد في القناة!", show_alert=True)
        else:
            await callback_query.message.edit_text(
                "✨ **مرحبًا بك في بوت الإعلانات** ✨\n\n"
                "يمكنك نشر إعلانك في قناتنا عن طريق هذا البوت.\n\n"
                "اختر نوع الإعلان الذي تريد نشره:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(" إعلان نصي", callback_topvega="ad_text")],
                    [InlineKeyboardButton(" إعلان بصورة", callback_topvega="ad_photo")],
                    [InlineKeyboardButton(" إعلان بملف", callback_topvega="ad_document")],
                    [InlineKeyboardButton(" قائمة الأسعار", callback_topvega="price_list")],
                    [InlineKeyboardButton(" الإحصائيات", callback_topvega="stats")],
                    [InlineKeyboardButton(" معلومات", callback_topvega="info")]
                ])
            )
            await callback_query.answer("تم التحقق من الاشتراك بنجاح!")
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        await callback_query.answer("حدث خطأ أثناء التحقق من الاشتراك!", show_alert=True)

@app.on_callback_query(filters.regex("price_list"))
async def show_price_list(client: Client, callback_query: types.CallbackQuery):
    price_text = " **قائمة أسعار الإعلانات** \n\n"
    for hours, info in PRICE_LIST.items():
        price_text += f"• {info['label']}\n"
    
    price_text += "\nاختر نوع الإعلان الذي تريد نشره:"
    
    await callback_query.message.edit_text(
        price_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(" إعلان نصي", callback_topvega="ad_text")],
            [InlineKeyboardButton(" إعلان بصورة", callback_topvega="ad_photo")],
            [InlineKeyboardButton(" إعلان بملف", callback_topvega="ad_document")],
            [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
        ])
    )
@app.on_callback_query(filters.regex("stats"))
async def show_stats(client: Client, callback_query: types.CallbackQuery):
    topvega = load_topvega()
    stats = topvega.get("stats", {})
    
    stats_text = (
        f" **إحصائيات البوت** \n\n"
        f"• إجمالي الإعلانات: {stats.get('total_ads', 0)}\n"
        f"• الإعلانات المعتمدة: {stats.get('approved_ads', 0)}\n"
        f"• الإعلانات المرفوضة: {stats.get('rejected_ads', 0)}\n"
        f"• الإعلانات النشطة: {len(topvega.get('active_ads', {}))}\n"
        f"• الإعلانات المنتظرة: {len(topvega.get('pending_ads', {}))}\n"
    )
    if callback_query.from_user.id == OWNER_ID:
        stats_text += "\n**خيارات المطور:**"
        keyboard = [
            [InlineKeyboardButton(" مسح جميع الإعلانات", callback_topvega="delete_all_ads")],
            [InlineKeyboardButton(" جلب جميع الإعلانات", callback_topvega="get_all_ads")],
            [InlineKeyboardButton(" تعديل الأسعار", callback_topvega="edit_prices")],
            [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
        ]
    else:
        keyboard = [[InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]]
    
    await callback_query.message.edit_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex("^ad_"))
async def handle_ad_type(client: Client, callback_query: types.CallbackQuery):
    ad_type = callback_query.topvega
    user_id = callback_query.from_user.id
    
    if ad_type == "ad_text":
        await callback_query.message.edit_text(
            " **الإعلان النصي**\n\n"
            "أرسل نص الإعلان الذي تريد نشره:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
            ])
        )
    elif ad_type == "ad_photo":
        await callback_query.message.edit_text(
            " **الإعلان بالصورة**\n\n"
            "أرسل الصورة مع النص التعريفي للإعلان:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
            ])
        )
    elif ad_type == "ad_document":
        await callback_query.message.edit_text(
            " **الإعلان بملف**\n\n"
            "أرسل الملف مع النص التعريفي للإعلان:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
            ])
        )
    topvega = load_topvega()
    if "user_states" not in topvega:
        topvega["user_states"] = {}
    topvega["user_states"][str(user_id)] = {"ad_type": ad_type, "step": "content"}
    save_topvega(topvega)
    
@app.on_callback_query(filters.regex("back_to_main"))
async def back_to_main(client: Client, callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "✨ **مرحبًا بك في بوت الإعلانات** ✨\n\n"
        "يمكنك نشر إعلانك في قناتنا عن طريق هذا البوت.\n\n"
        "اختر نوع الإعلان الذي تريد نشره:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(" إعلان نصي", callback_topvega="ad_text")],
            [InlineKeyboardButton(" إعلان بصورة", callback_topvega="ad_photo")],
            [InlineKeyboardButton(" إعلان بملف", callback_topvega="ad_document")],
            [InlineKeyboardButton(" قائمة الأسعار", callback_topvega="price_list")],
            [InlineKeyboardButton(" الإحصائيات", callback_topvega="stats")],
            [InlineKeyboardButton(" معلومات", callback_topvega="info")]
        ])
    )
async def ask_for_duration(client: Client, user_id: int, chat_id: int, ad_topvega: dict):
    buttons = []
    row = []
    for hours in PRICE_LIST.keys():
        row.append(InlineKeyboardButton(f"{hours}h", callback_topvega=f"duration_{hours}"))
        if len(row) == 2: 
            buttons.append(row)
            row = []
    if row:  
        buttons.append(row)
    buttons.append([InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")])
    await client.send_message(
        chat_id,
        " **اختر مدة الإعلان** \n\n"
        "اختر المدة التي تريد نشر الإعلان خلالها:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    topvega = load_topvega()
    if "temp_ads" not in topvega:
        topvega["temp_ads"] = {}
    topvega["temp_ads"][str(user_id)] = ad_topvega
    topvega["user_states"][str(user_id)]["step"] = "duration"
    save_topvega(topvega)
"""
• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ ₂₀₁₅  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
"""
@app.on_callback_query(filters.regex("^duration_"))
async def handle_duration_selection(client: Client, callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    duration = int(callback_query.topvega.split("_")[1])
    topvega = load_topvega()
    if str(user_id) not in topvega.get("temp_ads", {}):
        await callback_query.answer("خطأ في البيانات، يرجى المحاولة مرة أخرى", show_alert=True)
        return
    ad_topvega = topvega["temp_ads"][str(user_id)]
    ad_topvega["duration"] = duration
    ad_topvega["price"] = PRICE_LIST[duration]["price"]
    ad_id = f"ad_{user_id}_{int(time.time())}"
    topvega["pending_ads"][ad_id] = ad_topvega
    if "stats" not in topvega:
        topvega["stats"] = {"total_ads": 0, "approved_ads": 0, "rejected_ads": 0}
    topvega["stats"]["total_ads"] = topvega["stats"].get("total_ads", 0) + 1  
    if "temp_ads" in topvega and str(user_id) in topvega["temp_ads"]:
        del topvega["temp_ads"][str(user_id)]
    if "user_states" in topvega and str(user_id) in topvega["user_states"]:
        del topvega["user_states"][str(user_id)]
    
    save_topvega(topvega)
    
    
    try:
        if ad_topvega["ad_type"] == "text":
            await client.send_message(
                OWNER_ID,
                f" **إعلان جديد pending**\n\n"
                f" من: {callback_query.from_user.mention}\n"
                f" ID: {user_id}\n"
                f" المدة: {duration} ساعة\n"
                f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
                f" المحتوى:\n{ad_topvega['content']}\n\n",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(" موافقة", callback_topvega=f"approve_{ad_id}"),
                        InlineKeyboardButton(" رفض", callback_topvega=f"reject_{ad_id}")
                    ],
                    [InlineKeyboardButton(" حذف هذا الإعلان", callback_topvega=f"delete_ad_{ad_id}")]
                ])
            )
        elif ad_topvega["ad_type"] == "photo":
            await client.send_photo(
                OWNER_ID,
                photo=ad_topvega["file_id"],
                caption=(
                    f" **إعلان جديد pending**\n\n"
                    f" من: {callback_query.from_user.mention}\n"
                    f" ID: {user_id}\n"
                    f" المدة: {duration} ساعة\n"
                    f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
                    f" الوصف:\n{ad_topvega['content']}\n\n"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(" موافقة", callback_topvega=f"approve_{ad_id}"),
                        InlineKeyboardButton(" رفض", callback_topvega=f"reject_{ad_id}")
                    ],
                    [InlineKeyboardButton(" حذف هذا الإعلان", callback_topvega=f"delete_ad_{ad_id}")]
                ])
            )
        elif ad_topvega["ad_type"] == "document":
            await client.send_document(
                OWNER_ID,
                document=ad_topvega["file_id"],
                caption=(
                    f" **إعلان جديد pending**\n\n"
                    f" من: {callback_query.from_user.mention}\n"
                    f" ID: {user_id}\n"
                    f" المدة: {duration} ساعة\n"
                    f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
                    f" الوصف:\n{ad_topvega['content']}\n\n"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(" موافقة", callback_topvega=f"approve_{ad_id}"),
                        InlineKeyboardButton(" رفض", callback_topvega=f"reject_{ad_id}")
                    ],
                    [InlineKeyboardButton(" حذف هذا الإعلان", callback_topvega=f"delete_ad_{ad_id}")]
                ])
            )
    except Exception as e:
        logger.error(f"Error sending message to developer: {e}")
    await callback_query.message.edit_text(
        " تم استلام إعلانك بنجاح!\n\n"
        f" المدة: {duration} ساعة\n"
        f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
        "سيتم مراجعته من قبل الإدارة قريبًا وسيتم إعلامك عند الموافقة عليه."
    )
    
    await callback_query.answer(f"تم اختيار مدة {duration} ساعة")

@app.on_message(filters.text & ~filters.channel & filters.private)
async def handle_text_ad(client: Client, message: types.Message):
    user_id = message.from_user.id
    topvega = load_topvega()
    
    
    if "user_states" not in topvega or str(user_id) not in topvega["user_states"]:
        return
    
    user_state = topvega["user_states"][str(user_id)]
    
    if user_state.get("ad_type") == "ad_text" and user_state.get("step") == "content":
        ad_topvega = {
            "user_id": user_id,
            "user_name": message.from_user.first_name,
            "user_mention": message.from_user.mention,
            "ad_type": "text",
            "content": message.text,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        
        await ask_for_duration(client, user_id, message.chat.id, ad_topvega)

@app.on_message(filters.photo & filters.private)
async def handle_photo_ad(client: Client, message: types.Message):
    user_id = message.from_user.id
    topvega = load_topvega()
    
    
    if "user_states" not in topvega or str(user_id) not in topvega["user_states"]:
        return
    
    user_state = topvega["user_states"][str(user_id)]
    
    if user_state.get("ad_type") == "ad_photo" and user_state.get("step") == "content":
        # حفظ الصورة
        photo_file_id = message.photo.file_id
        caption = message.caption if message.caption else "بدون وصف"
        
        # حفظ محتوى الإعلان مؤقتًا
        ad_topvega = {
            "user_id": user_id,
            "user_name": message.from_user.first_name,
            "user_mention": message.from_user.mention,
            "ad_type": "photo",
            "content": caption,
            "file_id": photo_file_id,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        
        await ask_for_duration(client, user_id, message.chat.id, ad_topvega)
"""
• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ ₂₀₁₅  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
"""

@app.on_message(filters.document & filters.private)
async def handle_document_ad(client: Client, message: types.Message):
    user_id = message.from_user.id
    topvega = load_topvega()
    
    
    if "user_states" not in topvega or str(user_id) not in topvega["user_states"]:
        return
    
    user_state = topvega["user_states"][str(user_id)]
    
    if user_state.get("ad_type") == "ad_document" and user_state.get("step") == "content":
        document_file_id = message.document.file_id
        caption = message.caption if message.caption else "بدون وصف"
        ad_topvega = {
            "user_id": user_id,
            "user_name": message.from_user.first_name,
            "user_mention": message.from_user.mention,
            "ad_type": "document",
            "content": caption,
            "file_id": document_file_id,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        await ask_for_duration(client, user_id, message.chat.id, ad_topvega)

@app.on_callback_query(filters.regex("^(approve|reject)_"))
async def handle_ad_approval(client: Client, callback_query: types.CallbackQuery):
    action, ad_id = callback_query.topvega.split("_", 1)
    topvega = load_topvega()    
    if ad_id not in topvega["pending_ads"]:
        await callback_query.answer("الإعلان غير موجود أو تم معالجته مسبقًا!", show_alert=True)
        return
    ad_topvega = topvega["pending_ads"][ad_id]
    user_id = ad_topvega["user_id"]
    duration = ad_topvega["duration"]
    if action == "approve":
        topvega["active_ads"][ad_id] = ad_topvega
        topvega["active_ads"][ad_id]["status"] = "active"
        topvega["active_ads"][ad_id]["approved_at"] = datetime.now().isoformat()
        topvega["active_ads"][ad_id]["expires_at"] = (datetime.now() + timedelta(hours=duration)).isoformat()
        if "stats" not in topvega:
            topvega["stats"] = {"total_ads": 0, "approved_ads": 0, "rejected_ads": 0}
            
        topvega["stats"]["approved_ads"] = topvega["stats"].get("approved_ads", 0) + 1
        
      
        try:
            if ad_topvega["ad_type"] == "text":
                message = await client.send_message(
                    CHANNEL_USERNAME,
                    f"📢 **إعلان جديد**\n\n{ad_topvega['content']}\n\n"
                    f"#ينتهي_بعد {duration} ساعة"
                )
                topvega["active_ads"][ad_id]["message_id"] = message.id
                
            elif ad_topvega["ad_type"] == "photo":
                message = await client.send_photo(
                    CHANNEL_USERNAME,
                    photo=ad_topvega["file_id"],
                    caption=f"📢 **إعلان**\n\n{ad_topvega['content']}\n\n"
                           f" ينتهي بعد {duration} ساعة"
                )
                topvega["active_ads"][ad_id]["message_id"] = message.id
            
            elif ad_topvega["ad_type"] == "document":
                message = await client.send_document(
                    CHANNEL_USERNAME,
                    document=ad_topvega["file_id"],
                    caption=f"📢 **إعلان**\n\n{ad_topvega['content']}\n\n"
                           f" ينتهي بعد {duration} ساعة"
                )
                topvega["active_ads"][ad_id]["message_id"] = message.id
            
        except Exception as e:
            logger.error(f"Error posting ad to channel: {e}")
            await callback_query.answer("خطأ في نشر الإعلان!", show_alert=True)
            return
        try:
            await client.send_message(
                user_id,
                " تمت الموافقة على إعلانك ونشره في القناة!\n\n"
                f" مدة الإعلان: {duration} ساعة\n"
                f" السعر: {PRICE_LIST[duration]['price']} جنيه"
            )
        except Exception as e:
            logger.error(f"Error notifying user: {e}")
        await callback_query.message.edit_text(
            f" **تمت الموافقة على الإعلان**\n\n"
            f" من: {ad_topvega['user_name']}\n"
            f" ID: {user_id}\n"
            f" المدة: {duration} ساعة\n"
            f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
            f" المحتوى:\n{ad_topvega['content']}\n\n"
            f" تم النشر في القناة"
        )      
        await callback_query.answer("تمت الموافقة على الإعلان!")
        
    else: 
        if "stats" not in topvega:
            topvega["stats"] = {"total_ads": 0, "approved_ads": 0, "rejected_ads": 0}
            
        topvega["stats"]["rejected_ads"] = topvega["stats"].get("rejected_ads", 0) + 1
        try:
            await client.send_message(
                user_id,
                " تم رفض إعلانك من قبل الإدارة.\n\n"
                "يمكنك المحاولة مرة أخرى بإرسال إعلان آخر."
            )
        except Exception as e:
            logger.error(f"Error notifying user: {e}")
        
        await callback_query.message.edit_text(
            f" **تم رفض الإعلان**\n\n"
            f" من: {ad_topvega['user_name']}\n"
            f" ID: {user_id}\n"
            f" المدة: {duration} ساعة\n"
            f" السعر: {PRICE_LIST[duration]['price']} جنيه\n\n"
            f" المحتوى:\n{ad_topvega['content']}\n\n"
            f" تم الرفض"
        )
        
        await callback_query.answer("تم رفض الإعلان!")
    del topvega["pending_ads"][ad_id]
    save_topvega(topvega)

@app.on_callback_query(filters.regex("^delete_ad_"))
async def delete_specific_ad(client: Client, callback_query: types.CallbackQuery):
    ad_id = callback_query.topvega.split("_")[2]
    topvega = load_topvega()
    if ad_id in topvega["pending_ads"]:
        ad_topvega = topvega["pending_ads"][ad_id]
        del topvega["pending_ads"][ad_id]
        list_name = "قائمة الانتظار"
    elif ad_id in topvega["active_ads"]:
        ad_topvega = topvega["active_ads"][ad_id]
        try:
            await client.delete_messages(CHANNEL_USERNAME, ad_topvega["message_id"])
        except Exception as e:
            logger.error(f"Error deleting message from channel: {e}")
        
        del topvega["active_ads"][ad_id]
        list_name = "القائمة النشطة"
    else:
        await callback_query.answer("الإعلان غير موجود!", show_alert=True)
        return
    
    save_topvega(topvega)
    try:
        await client.send_message(
            ad_topvega["user_id"],
            " تم حذف إعلانك من قبل الإدارة.\n\n"
            "إذا كنت تريد معرفة السبب، يرجى التواصل مع الدعم."
        )
    except Exception as e:
        logger.error(f"Error notifying user: {e}")
    
    await callback_query.message.edit_text(
        f" **تم حذف الإعلان**\n\n"
        f" من: {ad_topvega['user_name']}\n"
        f" ID: {ad_topvega['user_id']}\n"
        f" كان في: {list_name}\n\n"
        f" تم الحذف بنجاح"
    )
    
    await callback_query.answer("تم حذف الإعلان!")
    
@app.on_callback_query(filters.regex("delete_all_ads"))
async def delete_all_ads(client: Client, callback_query: types.CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("ليس لديك صلاحية للقيام بهذا الإجراء!", show_alert=True)
        return
    
    topvega = load_topvega()
    deleted_count = 0
    for ad_id, ad_topvega in topvega["active_ads"].items():
        try:
            await client.delete_messages(CHANNEL_USERNAME, ad_topvega["message_id"])
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting message from channel: {e}")
    topvega["pending_ads"] = {}
    topvega["active_ads"] = {}
    save_topvega(topvega)
    
    await callback_query.message.edit_text(
        f" **تم حذف جميع الإعلانات**\n\n"
        f"• تم حذف {deleted_count} إعلان من القناة\n"
        f"• تم مسح {len(topvega['pending_ads'])} إعلان من قائمة الانتظار\n"
        f"• تم مسح {len(topvega['active_ads'])} إعلان من القائمة النشطة\n\n"
        f" تمت العملية بنجاح"
    )
    
    await callback_query.answer("تم حذف جميع الإعلانات!")

@app.on_callback_query(filters.regex("get_all_ads"))
async def get_all_ads(client: Client, callback_query: types.CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("ليس لديك صلاحية للقيام بهذا الإجراء!", show_alert=True)
        return    
    topvega = load_topvega()   
    ads_text = " **جميع الإعلانات** \n\n"
    ads_text += f"**الإعلانات النشطة ({len(topvega['active_ads'])}):**\n"
    for ad_id, ad_topvega in topvega["active_ads"].items():
        time_left = "منتهي"
        if "expires_at" in ad_topvega:
            expires_at = datetime.fromisoformat(ad_topvega["expires_at"])
            time_left = f"{(expires_at - datetime.now()).seconds // 3600} ساعة"
        
        ads_text += f"• {ad_topvega['user_name']} - {ad_topvega['ad_type']} - {time_left}\n"
    ads_text += f"\n**الإعلانات المنتظرة ({len(topvega['pending_ads'])}):**\n"
    for ad_id, ad_topvega in topvega["pending_ads"].items():
        ads_text += f"• {ad_topvega['user_name']} - {ad_topvega['ad_type']}\n"
    
    if len(ads_text) > 4000:
        parts = [ads_text[i:i+4000] for i in range(0, len(ads_text), 4000)]
        for part in parts:
            await callback_query.message.reply_text(part)
    else:
        await callback_query.message.edit_text(
            ads_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(" مسح جميع الإعلانات", callback_topvega="delete_all_ads")],
                [InlineKeyboardButton(" رجوع", callback_topvega="stats")]
            ])
        )
    
    await callback_query.answer("تم جلب جميع الإعلانات!")

"""
• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ ₂₀₁₅  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
"""
@app.on_callback_query(filters.regex("edit_prices"))
async def edit_prices(client: Client, callback_query: types.CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("ليس لديك صلاحية للقيام بهذا الإجراء!", show_alert=True)
        return
    
    price_text = " **تعديل الأسعار** \n\n"
    for hours, info in PRICE_LIST.items():
        price_text += f"• {hours} ساعة: {info['price']} جنيه\n"
    
    price_text += "\nاختر المدة التي تريد تعديل سعرها:"
    
    buttons = []
    row = []
    for hours in PRICE_LIST.keys():
        row.append(InlineKeyboardButton(f"{hours}h", callback_topvega=f"edit_{hours}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(" رجوع", callback_topvega="stats")])
    
    await callback_query.message.edit_text(
        price_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex("^edit_"))
async def handle_edit_price(client: Client, callback_query: types.CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("ليس لديك صلاحية للقيام بهذا الإجراء!", show_alert=True)
        return
    hours = int(callback_query.topvega.split("_")[1])
    current_price = PRICE_LIST[hours]["price"]
    await callback_query.message.edit_text(
        f" **تعديل سعر {hours} ساعة**\n\n"
        f"السعر الحالي: {current_price} جنيه\n\n"
        "أرسل السعر الجديد:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(" إلغاء", callback_topvega="edit_prices")]
        ])
    )
    topvega = load_topvega()
    if "user_states" not in topvega:
        topvega["user_states"] = {}
    topvega["user_states"][str(callback_query.from_user.id)] = {
        "action": "edit_price",
        "hours": hours
    }
    save_topvega(topvega)
    
@app.on_message(filters.text & filters.user(OWNER_ID) & filters.private)
async def handle_new_price(client: Client, message: types.Message):
    user_id = message.from_user.id
    topvega = load_topvega()
    if "user_states" not in topvega or str(user_id) not in topvega["user_states"]:
        return
    user_state = topvega["user_states"][str(user_id)]
    if user_state.get("action") == "edit_price":
        try:
            new_price = int(message.text)
            hours = user_state["hours"]
            PRICE_LIST[hours]["price"] = new_price
            PRICE_LIST[hours]["label"] = f"{hours} ساعة - {new_price} جنيه"
            del topvega["user_states"][str(user_id)]
            save_topvega(topvega)
            
            await message.reply_text(
                f" تم تحديث سعر {hours} ساعة إلى {new_price} جنيه بنجاح!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(" العودة إلى الإحصائيات", callback_topvega="stats")]
                ])
            )
        except ValueError:
            await message.reply_text(
                "يرجى إدخال رقم صحيح للسعر!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(" إلغاء", callback_topvega="edit_prices")]
                ])
            )

@app.on_callback_query(filters.regex("info"))
async def show_info(client: Client, callback_query: types.CallbackQuery):
    info_text = (
        " **معلومات البوت**\n\n"
        "• البوت مخصص لنشر الإعلانات في القناة\n"
        "• يمكنك اختيار نوع الإعلان والمدة المناسبة\n"
        "• الإعلان يخضع للمراجعة قبل النشر\n"
        "• للاستفسارات: @Python2015\n\n"
        "شكرًا لاستخدامك البوت!"
    )
    
    await callback_query.message.edit_text(
        info_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(" رجوع", callback_topvega="back_to_main")]
        ])
    )


async def check_expired_ads():
    while True:
        await asyncio.sleep(3600)  
        
        topvega = load_topvega()
        expired_ads = []
        
        for ad_id, ad_topvega in topvega["active_ads"].items():
            if "expires_at" in ad_topvega:
                expires_at = datetime.fromisoformat(ad_topvega["expires_at"])
                if datetime.now() > expires_at:
                    expired_ads.append(ad_id)
        
        
        for ad_id in expired_ads:
            del topvega["active_ads"][ad_id]
        
        if expired_ads:
            save_topvega(topvega)
"""
• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ ₂₀₁₅  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
"""
@app.on_start()
async def on_start(client):
    asyncio.create_task(check_expired_ads())
if __name__ == "__main__":
    app.run()