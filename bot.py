import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
SAVE_PATH = r'\\10.10.1.175\shared\AmbilFoto'

def get_next_file_number():
    try:
        today = datetime.now().strftime("%Y%m%d")
        existing_files = [f for f in os.listdir(SAVE_PATH) if f.startswith(f"astari_{today}")]
        if not existing_files:
            return 1
        numbers = [int(f.split('_')[2].split('.')[0]) for f in existing_files]
        return max(numbers) + 1
    except Exception:
        return 1

async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Ensure directory exists
        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH, exist_ok=True)
        
        # Get current date and next number
        current_date = datetime.now().strftime("%Y%m%d")
        file_number = get_next_file_number()
        
        # Generate filename: astari_YYYYMMDD_XX.jpg
        filename = f"astari_{current_date}_{file_number:02d}.jpg"
        file_path = os.path.join(SAVE_PATH, filename)
        
        # Get and save photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(custom_path=file_path)
        
        logger.info(f"Saving photo to: {file_path}")
        await update.message.reply_text(f"✅ Photo saved as: {filename}")
        
    except Exception as e:
        logger.error(f"Error saving photo: {str(e)}")
        await update.message.reply_text("❌ Sorry, couldn't save your photo. Please try again.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('👋 Hello! Send me a photo and I will save it.')

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, save_photo))
    print("Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()