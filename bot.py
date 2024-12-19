from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai import Ai
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


class Bot:
    def __init__(self):
        # Initialize AI model or logic
        self.ai = Ai()
        self.download_dir = "downloads"  # Directory to save files
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    # Start command handler
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Welcome to the bot! Send a message, photo, or video to interact."
        )

    # Text message handler
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text.lower()  # Extract user message
        try:
            # Get AI response
            res = self.ai.ai_resopnse(user_message)
            await update.message.reply_text(res)  # Send AI response to user
        except Exception as e:
            # Handle any unexpected errors
            await update.message.reply_text(f"An error occurred: {str(e)}")

    # Photo handler
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # Extract caption and photo details
            caption = update.message.caption
            photo = update.message.photo[-1]  # Get the largest photo (highest resolution)
            file_id = photo.file_id

            # Get the file information and download it
            file_info = await context.bot.get_file(file_id)
            downloaded_path = f"./downloads/{file_id}.jpg"
            await file_info.download_to_drive(downloaded_path)

            # Upload the photo to Gemini
            res = self.ai.upload_to_gemini(downloaded_path, mime_type="image/jpg")

            # Prepare the message for the AI model
            if res and caption:
                new_message = {
                    "role": "user",
                    "parts": [res, caption],
                }
            elif res:
                new_message = {
                    "role": "user",
                    "parts": [res, "Describe this image"],
                }
            else:
                raise ValueError("Failed to upload the image to Gemini.")

            # Get AI response
            replay = self.ai.ai_resopnse(new_message)

            # Send the AI response back to the user
            await update.message.reply_text(replay)

            file_path = '/download/i.png'

            try:
                os.remove(downloaded_path)
            except Exception as e:
                await update.message.reply_text("Error deleting file: {e}")



        except Exception as e:
            # Handle any exceptions and notify the user
            await update.message.reply_text(f"Failed to process the photo: {str(e)}")


    # Main function to set up and run the bot
    def main(self):
        # Replace 'YOUR_BOT_TOKEN' with your bot's API token (consider using environment variables for security)
        BOT_TOKEN = TELEGRAM_TOKEN

        # Build application with token
        application = Application.builder().token(BOT_TOKEN).build()

        # Register command and message handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        # Start the bot using polling
        application.run_polling()


# Run the bot
if __name__ == "__main__":
    bot = Bot()
    bot.main()
