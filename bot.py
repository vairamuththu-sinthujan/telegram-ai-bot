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
        self.ai_sessions = {}  # Dictionary to store AI sessions per user
        self.download_dir = "downloads"  # Directory to save files
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    # Start command handler
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id not in self.ai_sessions:
            self.ai_sessions[user_id] = Ai() # Create a new AI instance for the user
        await update.message.reply_text(
            "Welcome to the bot! Send a message, photo, or video to interact."
        )

    # Text message handler
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        user_message = update.message.text.lower()  # Extract user message

        if user_id not in self.ai_sessions:
            self.ai_sessions[user_id] = Ai()  # Ensure session exists for this user

        try:
            # Get AI response
            res = self.ai_sessions[user_id].ai_resopnse(user_message)
            await update.message.reply_text(res)  # Send AI response to user
        except Exception as e:
            # Handle any unexpected errors
            await update.message.reply_text(f"An error occurred: {str(e)}")

    # Photo handler
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id

        if user_id not in self.ai_sessions:
            self.ai_sessions[user_id] = Ai()  # Ensure session exists for this user

        try:
            # Extract caption and photo details
            caption = update.message.caption
            photo = update.message.photo[-1]  # Get the largest photo (highest resolution)
            file_id = photo.file_id

            # Check if the 'downloads' folder exists, if not, create it
            downloads_folder = './downloads'
            if not os.path.exists(downloads_folder):
                os.makedirs(downloads_folder)

            # Get the file information and download it
            file_info = await context.bot.get_file(file_id)
            downloaded_path = os.path.join(downloads_folder, f"{file_id}.jpg")

            # Download the image to the 'downloads' folder
            await file_info.download_to_drive(downloaded_path)

            # Upload the photo to Gemini
            res = self.ai_sessions[user_id].upload_to_gemini(downloaded_path, mime_type="image/jpg")

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
            replay = self.ai_sessions[user_id].ai_resopnse(new_message)

            # Send the AI response back to the user
            await update.message.reply_text(replay)

            # Delete the downloaded image after processing
            try:
                os.remove(downloaded_path)
            except Exception as e:
                await update.message.reply_text(f"Error deleting file: {str(e)}")

        except Exception as e:
            # Handle any exceptions and notify the user
            await update.message.reply_text(f"Failed to process the photo: {str(e)}")
            
    # Delete command handler
    async def delete_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id

        if user_id in self.ai_sessions:
            del self.ai_sessions[user_id]  # Remove user's session
            await update.message.reply_text("Your chat history and session have been deleted.")
        else:
            await update.message.reply_text("No active session found to delete.")


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
        application.add_handler(CommandHandler("restart", self.delete_chat))
        # Start the bot using polling
        application.run_polling()


