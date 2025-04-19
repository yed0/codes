from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import psycopg2
from datetime import datetime

TOKEN = "7627802768:AAFMZhBAcfcD_CbhoAsULPW-QOJzx3BllNM"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATABASE_URL = "postgresql://postgres.jmujxtsvrbhlvthkkbiq:dbanMcmX9oxJyQlE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    return conn, cursor


def add_cafe(name, location, working_hours, is_active=True):
    conn, cursor = connect_to_db()
    try:
        query = '''
        INSERT INTO cafes (name, location, working_hours, is_active)
        VALUES (%s, %s, %s, %s) RETURNING cafe_id;
        '''
        cursor.execute(query, (name, location, working_hours, is_active))
        cafe_id = cursor.fetchone()[0]
        conn.commit()
        return cafe_id
    except Exception as e:
        print(f"Error adding cafe: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_cafe(cafe_id):
    conn, cursor = connect_to_db()
    try:
        query = "DELETE FROM cafes WHERE cafe_id = %s;"
        cursor.execute(query, (cafe_id,))
        conn.commit()
        return cafe_id
    except Exception as e:
        print(f"Error deleting cafe: {e}")
    finally:
        cursor.close()
        conn.close()

def update_cafe(cafe_id, name=None, location=None, working_hours=None, is_active=None):
    conn, cursor = connect_to_db()
    try:
        # Start building the query with dynamic fields
        query = "UPDATE cafes SET "
        values = []
        updates = []

        # Append each field if it is provided
        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if location is not None:
            updates.append("location = %s")
            values.append(location)
        if working_hours is not None:
            updates.append("working_hours = %s")
            values.append(working_hours)
        if is_active is not None:
            updates.append("is_active = %s")
            values.append(is_active)

        # Ensure there are fields to update
        if not updates:
            return None

        # Complete the query
        query += ", ".join(updates) + " WHERE cafe_id = %s RETURNING cafe_id;"
        values.append(cafe_id)

        # Execute the update query
        cursor.execute(query, tuple(values))
        updated_cafe_id = cursor.fetchone()
        conn.commit()

        # Return the updated cafe ID if successful
        return updated_cafe_id[0] if updated_cafe_id else None
    except Exception as e:
        print(f"Error updating cafe: {e}")
    finally:
        cursor.close()
        conn.close()
            
def show_statistics():
    conn, cursor = connect_to_db()
    try:
        query = '''
        SELECT stat_id, user_id, cafe_id, order_date, subscription_status 
        FROM statistics;
        '''
        cursor.execute(query)
        stats = cursor.fetchall()
        return stats
    except Exception as e:
        print(f"Error fetching statistics: {e}")
    finally:
        cursor.close()
        conn.close()

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    add_cafe_button =  KeyboardButton("Add a cafe")
    delete_cafe_button = KeyboardButton("Delete a cafe")
    update_cafe_button = KeyboardButton("Update a cafe information")
    kb.add(add_cafe_button, delete_cafe_button, update_cafe_button)
    return kb


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Hello! How can I help You?", reply_markup= main_kb())


@dp.message_handler(lambda message: message.text == "Add a cafe")
async def add_cafe_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Add Cafe", callback_data="start_add_cafe")
    )
    await message.answer("Click to add a new cafe:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "start_add_cafe")
async def start_add_cafe(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id) 
    await bot.send_message(callback_query.from_user.id, "Please provide the cafe details in this format:\nName, Location, Working Hours, Active (True/False)")

@dp.message_handler(lambda message: ',' in message.text)
async def handle_cafe_details(message: types.Message):
    try:
        name, location, working_hours, is_active = [x.strip() for x in message.text.split(',')]
        is_active = is_active.lower() == 'true'
        cafe_id = add_cafe(name, location, working_hours, is_active)
        await message.reply(f"Cafe '{name}' added with ID: {cafe_id}")
    except Exception as e:
        await message.reply(f"Error adding cafe: {e}")

@dp.message_handler(lambda message: message.text == "Delete a cafe")
async def delete_cafe_command(message: types.Message):
    await message.reply("Please provide the Cafe ID to delete.")

@dp.message_handler(lambda message: message.text.startswith("Id:"))
async def handle_delete_cafe(message: types.Message):
    cafe_id = int(message.text)
    rows_deleted = delete_cafe(cafe_id)
    if rows_deleted > 0:
        await message.reply(f"Cafe with ID {cafe_id} has been deleted.")
    else:
        await message.reply(f"No cafe found with ID {cafe_id}.")

@dp.message_handler(lambda message: message.text == "Update a cafe information")  
async def update_cafe_command(message: types.Message):
    await message.reply("Please provide the Cafe ID and updated details in this format:\nCafe ID, Name, Location, Working Hours, Active (True/False)")

@dp.message_handler(lambda message: message.text.startswith("Update:"))
async def handle_update_cafe(message: types.Message):
    try:
        # Remove "update:" prefix and split by comma
        details = message.text[7:].strip().split(',')

        # Validate Cafe ID
        if len(details) < 1 or not details[0].strip().isdigit():
            await message.reply("Please provide a valid Cafe ID.")
            return

        # Parse inputs and set defaults to None for optional fields
        cafe_id = int(details[0].strip())
        name = details[1].strip() if len(details) > 1 and details[1].strip() else None
        location = details[2].strip() if len(details) > 2 and details[2].strip() else None
        working_hours = details[3].strip() if len(details) > 3 and details[3].strip() else None
        is_active = details[4].strip().lower() == 'true' if len(details) > 4 and details[4].strip() else None

        # Call the update_cafe function
        updated_cafe_id = update_cafe(cafe_id, name=name, location=location, working_hours=working_hours, is_active=is_active)
        
        # Provide feedback based on the result
        if updated_cafe_id:
            await message.reply(f"Cafe with ID {cafe_id} has been successfully updated.")
        else:
            await message.reply(f"No cafe found with ID {cafe_id} or no changes were made.")
    except Exception as e:
        await message.reply(f"Error updating cafe: {e}")

@dp.message_handler(commands=['show_statistics'])
async def show_statistics_command(message: types.Message):
    stats = show_statistics()
    if not stats:
        await message.reply("No statistics available.")
    else:
        response = "Statistics:\n"
        for stat_id, user_id, cafe_id, order_date, subscription_status in stats:
            response += f"Stat ID: {stat_id}, User ID: {user_id}, Cafe ID: {cafe_id}, Order Date: {order_date}, Subscription Status: {subscription_status}\n"
        await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)