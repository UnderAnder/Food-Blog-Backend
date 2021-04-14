import sqlite3
from sys import argv


class DB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('PRAGMA foreign_keys = ON;')
        cur.execute('CREATE TABLE IF NOT EXISTS recipes('
                    'recipe_id INTEGER PRIMARY KEY,'
                    'recipe_name TEXT NOT NULL,'
                    'recipe_description TEXT'
                    ');')
        cur.execute('CREATE TABLE IF NOT EXISTS meals('
                    'meal_id INTEGER PRIMARY KEY,'
                    'meal_name TEXT UNIQUE NOT NULL'
                    ');')
        cur.execute('CREATE TABLE IF NOT EXISTS ingredients('
                    'ingredient_id INTEGER PRIMARY KEY,'
                    'ingredient_name TEXT UNIQUE NOT NULL'
                    ');')
        cur.execute('CREATE TABLE IF NOT EXISTS measures('
                    'measure_id INTEGER PRIMARY KEY,'
                    'measure_name TEXT UNIQUE'
                    ');')
        cur.execute('CREATE TABLE IF NOT EXISTS serve('
                    'serve_id INTEGER PRIMARY KEY,'
                    'recipe_id INTEGER NOT NULL,'
                    'meal_id INTEGER NOT NULL,'
                    'FOREIGN KEY (recipe_id)'
                    'REFERENCES recipes (recipe_id)'
                    'FOREIGN KEY (meal_id)'
                    'REFERENCES meals (meal_id)' 
                    ');')
        self.conn.commit()

    def populate_tables(self, data: dict):
        cur = self.conn.cursor()
        for k in data.keys():
            for v in data[k]:
                cur.execute(f'INSERT INTO {k}({k[:-1]}_name) VALUES (?);', (v,))
        self.conn.commit()

    def add_recipe(self, recipe) -> int:
        cur = self.conn.cursor()
        result = cur.execute('INSERT INTO recipes(recipe_name, recipe_description) VALUES (?, ?);', recipe).lastrowid
        self.conn.commit()
        return result

    def close(self):
        self.conn.close()

    def print_meals(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM meals;')
        all_meals = cur.fetchall()
        for meal in all_meals:
            print(f'{meal[0]}) {meal[1]}', end='  ')
        print()

    def serve_time(self, recipe_id: int):
        cur = self.conn.cursor()
        meals_ids = map(int, input('When the dish can be served: ').split())
        for i in meals_ids:
            cur.execute(f'INSERT INTO serve(recipe_id, meal_id) VALUES (?, ?);', (recipe_id, i))
        self.conn.commit()


def main():
    db_name = argv[1] if len(argv) == 2 else 'food_blog.db'
    db = DB(db_name)
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    db.populate_tables(data)
    print('Pass the empty recipe name to exit.')
    while True:
        recipe_name = input('Recipe name: ')
        if not recipe_name:
            db.close()
            exit()
        recipe_description = input('Recipe description: ')
        recipe_id = db.add_recipe((recipe_name, recipe_description))
        db.print_meals()
        db.serve_time(recipe_id)


if __name__ == '__main__':
    main()
