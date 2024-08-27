import telebot
from telebot import types
import json
import os
import time
from telebot import types
from telebot.apihelper import ApiTelegramException

API_TOKEN = '6113047995:AAEqYQQHcdEdSPp3EYmTAFL091SvgHa6GFI'
bot = telebot.TeleBot(API_TOKEN)

CHANNEL_USERNAME = '@keysgen'
ADMIN_ID = 554130002
USER_DATA_FILE = 'user_data.json'

# Load user data
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'r') as file:
        user_data = json.load(file)
else:
    user_data = {}

# Save user data
def save_user_data():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

# Function to check subscription status
def is_user_subscribed(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to calculate time remaining
def get_time_remaining(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours)} hours and {int(minutes)} minutes"

# Function to get and remove codes from a file
def get_and_remove_codes(filename, num_codes=4):
    try:
        with open(filename, 'r') as file:
            codes = file.read().splitlines()

        if len(codes) < num_codes:
            return None

        selected_codes = codes[:num_codes]

        with open(filename, 'w') as file:
            file.write("\n".join(codes[num_codes:]))

        return selected_codes
    except FileNotFoundError:
        return None

# Function to format codes for messaging
def format_codes(codes):
    return "\n".join([f"`{code}`" for code in codes])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.from_user.id

    if not is_user_subscribed(chat_id):
        bot.send_message(chat_id, f"Please subscribe to {CHANNEL_USERNAME} to use this bot.")
        return

    if str(chat_id) not in user_data:
        user_data[str(chat_id)] = {"joined": time.time()}
        save_user_data()

    # Create inline keyboard with a single button
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Jugar en 1 clic 🐹", url="https://t.me/mkfubot?startapp")
    markup.add(button)

    welcome_message = (
        "👋 Welcome! I'm a bot that provides promo codes.\n\n"
        "Use the button below to play instantly!"
    )

    bot.send_message(chat_id, welcome_message, reply_markup=markup)

    # Create the regular keyboard
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [
        types.KeyboardButton("🔄 Get All"),
        types.KeyboardButton("📊 Total"),
        types.KeyboardButton("🚴‍♂️ Bike"),
        types.KeyboardButton("🎲 Cube"),
        types.KeyboardButton("🎨 Poly"),
        types.KeyboardButton("🚂 Train"),
        types.KeyboardButton("🔄 Merge"),
        types.KeyboardButton("🍑 Twerk"),
        types.KeyboardButton("🚀 Trim"),
        types.KeyboardButton("🏁 Race")
    ]

    # Add Admin button if user is the admin
    if chat_id == ADMIN_ID:
        buttons.append(types.KeyboardButton("👥 Total Users"))
        buttons.append(types.KeyboardButton("✏️ Add Codes"))

    markup.add(*buttons)


# Handle messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.from_user.id
    text = message.text

    if not is_user_subscribed(chat_id):
        bot.send_message(chat_id, f"Please subscribe to {CHANNEL_USERNAME} to use this bot.")
        return

    if text == "🔄 Get All":
        send_all_game_codes(chat_id)
    elif text == "📊 Total":
        send_total_codes(chat_id)
    elif text == "👥 Total Users" and chat_id == ADMIN_ID:
        send_total_users(chat_id)
    elif text == "✏️ Add Codes" and chat_id == ADMIN_ID:
        show_game_selection(chat_id)
    elif text == "🔙 Back":
        send_welcome(message)
    else:
        game_buttons = ["🚴‍♂️ Bike", "🎲 Cube", "🎨 Poly", "🚂 Train", "🔄 Merge", "🍑 Twerk", "🚀 Trim", "🏁 Race"]
        if text in game_buttons:
            game = text.split(" ")[-1].lower()  # Extract game name from button text
            send_game_codes(chat_id, game)
        else:
            bot.send_message(chat_id, "Invalid option. Please use the buttons below.")


# Show game selection to admin
def show_game_selection(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    game_buttons = [
        types.KeyboardButton("🚴‍♂️ Bike"),
        types.KeyboardButton("🎲 Cube"),
        types.KeyboardButton("🎨 Poly"),
        types.KeyboardButton("🚂 Train"),
        types.KeyboardButton("🔄 Merge"),
        types.KeyboardButton("🍑 Twerk"),
        types.KeyboardButton("🚀 Trim"),
        types.KeyboardButton("🏁 Race"),
        types.KeyboardButton("🔙 Back")  # Back button
    ]
    markup.add(*game_buttons)
    bot.send_message(chat_id, "Please choose a game to add codes to:", reply_markup=markup)

    # Register the next step handler to process game selection
    bot.register_next_step_handler_by_chat_id(chat_id, process_game_selection)

# Process game selection
def process_game_selection(message):
    chat_id = message.from_user.id
    text = message.text

    if text == "🔙 Back":
        send_welcome(message)
        return

    game = text.split(" ")[-1].lower()  # Extract game name from button text

    if game in ["bike", "cube", "poly", "train", "merge", "twerk", "trim", "race"]:
        bot.send_message(chat_id, f"Please send the codes for {game} separated by commas.")
        bot.register_next_step_handler(message, lambda msg: add_codes_to_game(game, msg))
    else:
        bot.send_message(chat_id, "Invalid game selected. Please choose a valid game.")
        show_game_selection(chat_id)


# Add codes to the selected game
def add_codes_to_game(game, message):
    chat_id = message.from_user.id
    codes_str = message.text

    filename = f"{game}.txt"
    codes = [code.strip() for code in codes_str.split(",") if code.strip()]

    # Read existing codes to avoid duplicates (optional)
    existing_codes = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_codes = set(line.strip() for line in file)

    # Add new codes ensuring each code is on a new line
    try:
        with open(filename, 'a') as file:
            for code in codes:
                if code and code not in existing_codes:
                    file.write("\n"+code)

        bot.send_message(chat_id, f"Codes added successfully to {game}.")
    except Exception as e:
        bot.send_message(chat_id, "There was an error processing your request. Please try again.")
        print(f"Error: {e}")



# Function to send codes for a specific game
def send_game_codes(chat_id, game):
    filename = f"{game}.txt"
    current_time = time.time()
    user_id = str(chat_id)

    if user_id in user_data and game in user_data[user_id]:
        last_request_time = user_data[user_id][game]
        time_elapsed = current_time - last_request_time
        time_remaining = 86400 - time_elapsed

        if time_remaining > 0:
            remaining_time_formatted = get_time_remaining(time_remaining)
            bot.send_message(chat_id, f"You have already received codes for this game. Please try again in {remaining_time_formatted}.")
            return

    codes = get_and_remove_codes(filename)

    if codes:
        codes_message = format_codes(codes)
        bot.send_message(chat_id, f"Codes for {game}:\n\n{codes_message}\n\nGo to @keysgen 🐹", parse_mode='MarkdownV2')

        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id][game] = current_time
        save_user_data()
    else:
        bot.send_message(chat_id, "Sorry, there are not enough codes for this game or all codes have been used up.")

# Function to send all game codes at once
def send_all_game_codes(chat_id):
    games = ['bike', 'cube', 'train', 'merge', 'twerk', 'poly', 'trim', 'race']
    all_codes_message = ""
    current_time = time.time()
    user_id = str(chat_id)

    for game in games:
        if user_id in user_data and game in user_data[user_id]:
            last_request_time = user_data[user_id][game]
            time_elapsed = current_time - last_request_time
            time_remaining = 86400 - time_elapsed

            if time_remaining > 0:
                remaining_time_formatted = get_time_remaining(time_remaining)
                bot.send_message(chat_id, f"You have already received codes for {game}. Please try again in {remaining_time_formatted}.")
                return

    for game in games:
        filename = f"{game}.txt"
        codes = get_and_remove_codes(filename)

        if codes:
            all_codes_message += f"Codes for {game}:\n" + format_codes(codes) + "\n\n"
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id][game] = current_time
        else:
            all_codes_message += f"Sorry, there are not enough codes for {game} or all codes have been used up.\n\n"

    if all_codes_message:
        save_user_data()
        bot.send_message(chat_id, all_codes_message + "Go to @keysgen 🐹", parse_mode='MarkdownV2')

# Function to send the total number of available codes for each game
def send_total_codes(chat_id):
    games = ['bike', 'cube', 'train', 'merge', 'twerk', 'poly', 'trim', 'race']
    total_message = "Remaining codes for each game:\n\n"

    for game in games:
        filename = f"{game}.txt"
        count = get_codes_count(filename)
        total_message += f"{game} : {count} codes\n"

    bot.send_message(chat_id, total_message)

# Function to count available codes in a file
def get_codes_count(filename):
    try:
        with open(filename, 'r') as file:
            codes = file.read().splitlines()
        return len(codes)
    except FileNotFoundError:
        return 0

# Function to send the total number of bot users (Admin only)
def send_total_users(chat_id):
    total_users = len(user_data)
    bot.send_message(chat_id, f"Total number of users: {total_users}")

# Run bot with retry mechanism
while True:
    try:
        bot.polling(none_stop=True, interval=5)
    except ApiTelegramException as e:
        if e.result == 'Forbidden: bot was blocked by the user':
            # Handle blocked user
            print(f"Bot was blocked by a user. Ignoring this user.")
        else:
            # Handle other Telegram API exceptions
            print(f"An error occurred: {e}")
        time.sleep(15)  # Wait for 15 seconds before retrying
    except Exception as e:
        # Handle other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        time.sleep(15)  # Wait for 15 seconds before retrying
