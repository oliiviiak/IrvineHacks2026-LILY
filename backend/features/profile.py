import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "db", "app.db")

connection = sqlite3.connect(db_path)


class UserCaretaker:
    def __init__(self, user_id, first_name, last_name, pfp):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.pfp = pfp

    def _delete_from_database(self, connection):
        connection.execute("DELETE FROM caretakers WHERE user_id = 123")
        connection.commit()

    def add_to_database(self, connection):
        connection.execute(
            "INSERT INTO caretakers (user_id, first_name, last_name, pfp) VALUES (:user_id, :first_name, :last_name, :pfp)",
            {
                "user_id": self.user_id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "pfp": self.pfp
            }
        )
        connection.commit()

class UserCareneeder:
    def __init__(self, user_id, first_name, last_name, pfp):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.pfp = pfp

    def _delete_from_database(self, connection):
        connection.execute("DELETE FROM careneeders WHERE user_id = 123")
        connection.commit()

    def add_to_database(self, connection):
        connection.execute(
            "INSERT INTO careneeders (user_id, first_name, last_name, pfp) VALUES (:user_id, :first_name, :last_name, :pfp)",
            {
                "user_id": self.user_id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "pfp": self.pfp
            }
        )
        connection.commit()

class Household:
    def __init__(self, *args: UserCaretaker):
        self.household_users = list(args)



c1 = UserCareneeder(123, "Isabel", "Wang", "photo.jpg")
c2 = UserCareneeder(123, "Allison", "Wang", "photo2.jpg")

h = Household(c1, c2)
#c._delete_from_database(connection)
#c.add_to_database(connection)