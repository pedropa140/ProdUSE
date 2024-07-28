import sqlite3

class User:
    def __init__(self, discord_name, discord_id, time_preference):
        self.discord_name = discord_name
        self.discord_id = discord_id
        self.time_preference = time_preference

class UserDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (discord_name TEXT, discord_id TEXT PRIMARY KEY, time_preference TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_tasks
                            (discord_id TEXT, task_name TEXT KEY, start_time TEXT, end_time TEXT, completed BOOLEAN)''')

        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user.discord_name, user.discord_id, user.time_preference))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT discord_name, discord_id, time_preference FROM users")
        return self.cursor.fetchall()

    def get_user_by_id(self, discord_id):
        self.cursor.execute("SELECT * FROM users WHERE discord_id=?", (discord_id,))
        return self.cursor.fetchone()

    def update_time_preference(self, discord_id, new_time_preference):
        self.cursor.execute("UPDATE users SET time_preference=? WHERE discord_id=?", (new_time_preference, discord_id))
        self.conn.commit()

    def delete_user(self, discord_id):
        self.cursor.execute("DELETE FROM users WHERE discord_id=?", (discord_id,))
        self.conn.commit()

    def user_exists(self, discord_id):
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE discord_id=?", (discord_id,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def add_task(self, discord_id, task_name, start_time, end_time, completed=False):
        self.cursor.execute("INSERT INTO user_tasks VALUES (?, ?, ?, ?, ?)", (discord_id, task_name, start_time, end_time, completed))
        self.conn.commit()

    def get_task_by_name(self, task_name):
        self.cursor.execute("SELECT * FROM user_tasks WHERE task_name=?", (task_name,))
        return self.cursor.fetchone()

    def get_task_names_by_id(self, discord_id):
        self.cursor.execute("SELECT task_name FROM user_tasks WHERE discord_id=?", (discord_id,))
        task_names = self.cursor.fetchall()
        return [task[0] for task in task_names]
    
    def get_tasks_by_id(self, discord_id):
        self.cursor.execute("SELECT * FROM user_tasks WHERE discord_id=?", (discord_id,))
        return self.cursor.fetchall()

    def update_task_completion(self, discord_id, task_name, completed):
        self.cursor.execute("UPDATE user_tasks SET completed=? WHERE discord_id=? AND task_name=?", 
                            (completed, discord_id, task_name))
        self.conn.commit()

    def delete_task(self, discord_id, task_name):
        self.cursor.execute("DELETE FROM user_tasks WHERE discord_id=? AND task_name=?", 
                            (discord_id, task_name))
        self.conn.commit()

    def close(self):
        self.conn.close()

# if __name__ == '__main__':
#     for i in 