import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright

# നിന്റെ Bot Token ഇവിടെ നൽകുക
TOKEN = '8466851965:AAGv7ErsKZ3i1E6lHU_fWxy3g5OT7jv5eJo'

async def check_wa_status(phone):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # WhatsApp Web check URL
        url = f"https://web.whatsapp.com/send?phone={phone}"
        await page.goto(url)
        
        # ലോഗിൻ പേജ് ലോഡ് ആകാൻ കുറച്ചു സമയം നൽകുന്നു
        try:
            # പബ്ലിക് ആയി ചെക്ക് ചെയ്യാൻ പറ്റുന്ന എലമെന്റ് നോക്കുന്നു
            await page.wait_for_selector('canvas', timeout=15000)
            await asyncio.sleep(2) # ചെറിയൊരു ഗ്യാപ്പ്
            
            # 'Invalid' മെസ്സേജ് വരുന്നുണ്ടോ എന്ന് നോക്കുന്നു
            is_invalid = await page.get_by_text("Phone number shared via url is invalid").is_visible()
            
            if is_invalid:
                return f"❌ {phone} : Banned/Invalid"
            else:
                return f"✅ {phone} : Active/Clean"
        except:
            return f"⚠️ {phone} : Timeout/Manual Check Needed"
        finally:
            await browser.close()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    numbers = raw_text.split('\n') # ഓരോ വരിയും ഓരോ നമ്പറായി എടുക്കും
    
    await update.message.reply_text(f"പരിശോധന തുടങ്ങുന്നു... ആകെ {len(numbers)} നമ്പറുകൾ. 🚀")
    
    for num in numbers:
        num = num.strip().replace("+", "")
        if num:
            result = await check_wa_status(num)
            await update.message.reply_text(result)
            await asyncio.sleep(3) # വാട്സാപ്പ് ബ്ലോക്ക് ചെയ്യാതിരിക്കാൻ ചെറിയ ഡിലേ

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("ബോട്ട് റെഡിയാണ് മുത്തേ! 🤝")
    app.run_polling()
