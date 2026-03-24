import oracledb
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

from db_config import get_connection

app = Flask(
    __name__,
    template_folder='../frontend',   # path from backend/app.py to frontend/templates

)

app.secret_key = "supersecretkey"

@app.route("/about")
def aboutsite():
    return render_template("about.html")  # your HTML file name

# Home page: list all recipe

@app.route('/')
def welcome():
    return render_template("welcome.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id FROM users WHERE username = :u AND password = :p
        """, {"u": username, "p": password})
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            session['user_id'] = row[0]   # ✅ Save logged-in user’s ID
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('signin.html')

@app.route('/signout', methods=['POST'])
def signout():
    session.clear()
    return redirect(url_for('welcome'))  # must point to your welcome.html page route


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # ✅ Check if passwords match
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (:u, :p)
            """, {"u": username, "p": password})
            conn.commit()
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for('signin'))

        except oracledb.IntegrityError:
            flash("Username already exists.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

@app.route('/recipes')
def index():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all recipes
    cursor.execute("""
        SELECT recipe_id, recipe_name, description
        FROM recipes
        ORDER BY recipe_id
    """)
    recipes = cursor.fetchall()

    recipe_list = []
    for recipe in recipes:
        recipe_id, name, description = recipe

        # Fetch ingredients with quantities
        cursor.execute("""
            SELECT
            COALESCE(i.ingredient_name, ri.ingredient_name) AS name,
            ri.quantity
            FROM recipe_ingredients ri
            LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
            WHERE ri.recipe_id = :id
        """, {"id": recipe_id})

        ingredients = [{"name": row[0], "quantity": row[1]} for row in cursor.fetchall()]


        # Fetch steps
        cursor.execute("""
            SELECT step_description
            FROM recipe_steps
            WHERE recipe_id = :id
            ORDER BY step_number
        """, {"id": recipe_id})
        steps = [row[0] for row in cursor.fetchall()]

        # Optionally, fetch likes count
        cursor.execute("""
            SELECT COUNT(*) FROM favorites
            WHERE recipe_id = :id
        """, {"id": recipe_id})
        likes = cursor.fetchone()[0]

        recipe_list.append({
            "id": recipe_id,
            "name": name,
            "description": description,
            "ingredients": ingredients,
            "steps": steps,
            "likes": likes
        })

    cursor.close()
    conn.close()

    # Debug print to check quantities
    # for r in recipe_list:
    #     print(r["name"], r["ingredients"])

    return render_template("index.html", recipes=recipe_list)


# Add recipe
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        # 1️⃣ Get main recipe details
        name = request.form['name']
        desc = request.form['description']

        # 2️⃣ Get ingredients and quantities from form
        ingredient_names = request.form.getlist('ingredient_name[]')
        ingredient_qtys = request.form.getlist('ingredient_qty[]')

        if not ingredient_names or not ingredient_qtys or len(ingredient_names) != len(ingredient_qtys):
            flash("Please provide ingredients and quantities properly.", "danger")
            return redirect(url_for('add_recipe'))

        # Format ingredients as "Tomato:2 cups, Salt:1 tsp"
        ingredients_str = ', '.join(f"{n.strip()}:{q.strip()}" for n, q in zip(ingredient_names, ingredient_qtys))

        # 3️⃣ Get instructions
        instructions_text = request.form['instructions']
        # Split by new lines, remove empty lines, join with comma
        steps_str = ', '.join([s.strip() for s in instructions_text.split("\n") if s.strip()])

        # 4️⃣ Call stored procedure
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.callproc("add_recipe", [name, desc, ingredients_str, steps_str])
            conn.commit()  # VERY IMPORTANT! Without this, nothing is saved.
            flash("Recipe added successfully!", "success")
        except Exception as e:
            flash(f"Error adding recipe: {e}", "danger")
        finally:
            cur.close()
            conn.close()

        # 5️⃣ Redirect to home page (index.html) where recipe is listed
        return redirect(url_for('index'))

    # GET request → show the form
    return render_template('add_recipe.html')



# Top 5 recipes# Top 5 recipes
@app.route('/top_recipes')
def top_recipes():
    conn = get_connection()
    top5 = []
    if conn:
        cur = conn.cursor()
        top5_cursor = cur.callfunc("get_top_5_recipes", oracledb.CURSOR, [])
        top5 = top5_cursor.fetchall()
        cur.close()
        conn.close()

    # Preprocess ingredients: split by comma, strip spaces
    top5_processed = []
    for r in top5:
        ingredients_list = []
        if r[3]:  # ensure it's not None
            ingredients_list = [(i.strip(), '') for i in r[3].split(',')]
            # the second value is '' because you don’t have separate quantity

        top5_processed.append((r[0], r[1], r[2], ingredients_list, r[4]))

    return render_template('top_recipes.html', top5=top5_processed)






# Search by ingredient
@app.route('/search', methods=['GET', 'POST'])
def search():
    recipes = []
    if request.method == 'POST':
        search_term = request.form['ingredient']  # the input from search box
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            # call the updated Oracle function
            rc = cur.var(oracledb.CURSOR)
            recipes_cursor = cur.callfunc("search_by_ingredient", oracledb.CURSOR, [search_term])
            # fetch all rows as dictionaries for easier template access
            columns = [col[0].lower() for col in recipes_cursor.description]
            for row in recipes_cursor:
                recipes.append({columns[i]: row[i] for i in range(len(row))})
            cur.close()
            conn.close()

    return render_template('search.html', recipes=recipes)




from flask import jsonify, session

@app.route('/like/<int:recipe_id>', methods=['POST'])
def like_recipe(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in.'})

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Call your Oracle procedure to toggle like/unlike
        cur.callproc("add_favorite", [user_id, recipe_id])
        conn.commit()

        # Get updated like count
        cur.execute("SELECT COUNT(*) FROM favorites WHERE recipe_id = :r", {"r": recipe_id})
        likes = cur.fetchone()[0]

        return jsonify({'status': 'success', 'likes': likes})

    except Exception as e:
        print("Error in like_recipe:", e)
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
