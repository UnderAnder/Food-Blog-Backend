import sqlite3
from sys import argv


class DB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS recipes('
                    'recipe_id INTEGER PRIMARY KEY,'
                    'recipe_name TEXT NOT NULL,'
                    'recipe_description TEXT)'
                    ';')
        cur.execute('CREATE TABLE IF NOT EXISTS meals('
                    'meal_id INTEGER PRIMARY KEY,'
                    'meal_name TEXT UNIQUE NOT NULL)'
                    ';')
        cur.execute('CREATE TABLE IF NOT EXISTS ingredients('
                    'ingredient_id INTEGER PRIMARY KEY,'
                    'ingredient_name TEXT UNIQUE NOT NULL)'
                    ';')
        cur.execute('CREATE TABLE IF NOT EXISTS measures('
                    'measure_id INTEGER PRIMARY KEY,'
                    'measure_name TEXT UNIQUE)'
                    ';')
        self.conn.commit()

    def populate_tables(self, data: dict):
        cur = self.conn.cursor()
        for k in data.keys():
            for v in data[k]:
                cur.execute(f'INSERT INTO {k}({k[:-1]}_name) VALUES (?);', (v,))
        self.conn.commit()

    def add_recipe(self, recipe):
        cur = self.conn.cursor()
        print(recipe)
        cur.execute('INSERT INTO recipes(recipe_name, recipe_description) VALUES (?, ?);', recipe)
        self.conn.commit()

    def close(self):
        self.conn.close()


def main():
    db_name = argv[1] if len(argv) == 2 else 'food_blog.db'
    db = DB(db_name)
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    db.populate_tables(data)
    while True:
        recipe_name = input('Recipe name: ')
        if not recipe_name:
            db.close()
            exit()
        recipe_description = input('Recipe description: ')
        db.add_recipe((recipe_name, recipe_description))


if __name__ == '__main__':
    main()
