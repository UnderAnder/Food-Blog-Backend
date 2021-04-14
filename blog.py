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
                    'FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id),'
                    'FOREIGN KEY (meal_id) REFERENCES meals (meal_id)'
                    ');')
        cur.execute('CREATE TABLE IF NOT EXISTS quantity('
                    'quantity_id INTEGER PRIMARY KEY,'
                    'measure_id INTEGER NOT NULL,'
                    'ingredient_id INTEGER NOT NULL,'
                    'recipe_id INTEGER NOT NULL,'
                    'quantity INTEGER NOT NULL,'
                    'FOREIGN KEY (measure_id) REFERENCES measures (measure_id),'
                    'FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id),'
                    'FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id)'
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

    def print_meals(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM meals;')
        all_meals = cur.fetchall()
        for meal in all_meals:
            print(f'{meal[0]}) {meal[1]}', end='  ')
        print()

    def mealtime(self, recipe_id: int):
        cur = self.conn.cursor()
        meals_ids = map(int, input('Enter proposed meals separated by a space: ').split())
        for i in meals_ids:
            cur.execute(f'INSERT INTO serve(recipe_id, meal_id) VALUES (?, ?);', (recipe_id, i))
        self.conn.commit()

    def ingredients_quantity(self, recipe_id: int):
        cur = self.conn.cursor()
        while True:
            user_input = input('Input quantity of ingredient <press enter to stop> ')
            if not user_input:
                return False
            if len(user_input.split()) == 3:
                quantity, measure, ingredient = user_input.split()
            else:
                quantity, ingredient = user_input.split()
                measure = "" #cur.execute('SELECT (measure_id) FROM measures WHERE measure_name = "";').fetchone()

            if self.find_in_table(measure, 'measure'):
                measure_id = self.find_in_table(measure, 'measure')
            else:
                print('The measure is not conclusive!')
                continue
            if self.find_in_table(ingredient, 'ingredient'):
                ingredient_id = self.find_in_table(ingredient, 'ingredient')
            else:
                print('The ingredient is not conclusive!')
                continue

            cur.execute('INSERT INTO quantity(measure_id, ingredient_id, recipe_id, quantity) '
                        'VALUES (?, ?, ?, ?);', (measure_id, ingredient_id, recipe_id, quantity))
            self.conn.commit()

    def find_in_table(self, q, field):
        cur = self.conn.cursor()
        if q == '' and field == 'measure':
            result = cur.execute('SELECT (measure_id) FROM measures WHERE measure_name = "";').fetchall()
        else:
            result = cur.execute(f"SELECT {field}_id FROM {field}s WHERE {field}_name LIKE '%'||?||'%';", (q,)).fetchall()
        print(q, result)
        if len(result) == 1:
            return result[0][0]
        else:
            return False

    def close(self):
        self.conn.close()


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
        db.mealtime(recipe_id)
        db.ingredients_quantity(recipe_id)


if __name__ == '__main__':
    main()
