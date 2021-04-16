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

    def add_recipe(self, recipe: tuple) -> int:
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
            cur.execute('INSERT INTO serve(recipe_id, meal_id) VALUES (?, ?);', (recipe_id, i))
        self.conn.commit()

    def ingredients_quantity(self, recipe_id: int):
        cur = self.conn.cursor()
        while user_input := input('Input quantity of ingredient <press enter to stop> ').split():
            if len(user_input) == 3:
                quantity, measure, ingredient = user_input
            elif len(user_input) == 2:
                quantity, ingredient = user_input
                measure = ""
            else:
                print('Wrong lenght of ingredients!')
                continue

            if x := self.get_from_table(measure, 'measure'):
                measure_id = x
            else:
                print('The measure is not conclusive!')
                continue
            if x := self.get_from_table(ingredient, 'ingredient'):
                ingredient_id = x
            else:
                print('Wrong lenght!')
                continue
            cur.execute('INSERT INTO quantity(measure_id, ingredient_id, recipe_id, quantity) '
                        'VALUES (?, ?, ?, ?);', (measure_id, ingredient_id, recipe_id, int(quantity)))
            self.conn.commit()

    def get_from_table(self, q: str, field: str):
        cur = self.conn.cursor()
        if q == '' and field == 'measure':
            res = cur.execute('SELECT measure_id FROM measures WHERE measure_name = "";').fetchall()
        else:
            res = cur.execute(f"SELECT {field}_id FROM {field}s WHERE {field}_name LIKE '%'||?||'%';", (q,)).fetchall()
        return res[0][0] if len(res) == 1 else False

    def find_recipe(self, ingredients: tuple, meals: tuple):
        cur = self.conn.cursor()
        recipe_stmt = f"""SELECT r.recipe_id, recipe_name
            FROM (SELECT * FROM ingredients WHERE ingredient_name IN ({','.join('?'*len(ingredients))})) i
            INNER JOIN quantity q ON i.ingredient_id = q.ingredient_id
            INNER JOIN recipes r ON q.recipe_id = r.recipe_id
            INNER JOIN serve s ON s.recipe_id = r.recipe_id
            INNER JOIN (SELECT * FROM meals WHERE meal_name IN ({','.join('?'*len(meals))})) m
            ON m.meal_id = s.meal_id
            GROUP BY r.recipe_id 
            HAVING COUNT(DISTINCT i.ingredient_id) = ?
        """
        res = cur.execute(recipe_stmt, (*ingredients, *meals, len(ingredients))).fetchall()
        if not res:
            print('no such recipes')
        else:
            output = ', '.join([el[1] for el in res])
            print(output)


def main():
    db_name = argv[1] if len(argv) >= 2 else 'food_blog.db'
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    db = DB(db_name)
    if len(argv) == 4:
        ingredients = tuple(argv[2].split('=')[1].strip('"').split(','))
        meals = tuple(argv[3].split('=')[1].strip('"').split(','))
        print(ingredients, meals)
        db.find_recipe(ingredients, meals)
    else:
        db.populate_tables(data)
        print('Pass the empty recipe name to exit.')
        while recipe_name := input('Recipe name: '):
            recipe_description = input('Recipe description: ')
            recipe_id = db.add_recipe((recipe_name, recipe_description))
            db.print_meals()
            db.mealtime(recipe_id)
            db.ingredients_quantity(recipe_id)
    db.conn.close()


if __name__ == '__main__':
    main()
