import datetime
import aiosqlite

async def new_users(user_id, username, balance_user):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS balances (id PRIMARY KEY, username CHAR(30), balance FLOAT AUTO_INCRIMENT, date TEXT)""")
        cursor = await db.execute('SELECT * FROM balances WHERE id = ?', (user_id,))
        data = await cursor.fetchone()
        if data is not None:
            return 'Пользователь уже существует'
    date_user = f'{datetime.date.today()}'
    async with aiosqlite.connect("users.db") as db:
        await db.execute("INSERT INTO balances (id, username, balance, date) VALUES (?, ?, ?, ?)",
                         (user_id, username, balance_user, date_user))
        await db.commit()
        return None

async def get_users(username):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS balances (id PRIMARY KEY, username CHAR(30), balance FLOAT AUTO_INCRIMENT, date TEXT)""")
        result = await db.execute("SELECT * FROM balances WHERE username = ?", (username,))
        data = await result.fetchall()
        if not data:
            return "Ничего не найдено"
        else:
            return data[0][2]

async def get_id(username):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("CREATE TABLE IF NOT EXISTS balances(id PRIMARY KEY, username CHAR(30), balance FLOAT AUTO_INCRIMENT, date TEXT)")
        result = await db.execute("SELECT * FROM balances WHERE username = ?", (username,))
        data = await result.fetchall()
        if not data:
            return "Ничего не найдено"
        else:
            return data[0][0]

async def change_balance_bal(summ, username):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("UPDATE balances SET balance = ? WHERE username = ?",
                         (summ, username))
        await db.commit()

async def delete_user(username):
    async with aiosqlite.connect('users.db') as db:
        await db.execute("DELETE FROM balances WHERE username = ?", (username,))
        await db.commit()
