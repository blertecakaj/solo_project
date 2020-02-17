from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
import os

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


app = Flask(__name__)
app.secret_key = "noice"
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    is_valid = True

    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("First name must be at least 2 characters long!")
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("Last name must be at least 2 characters long!")
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Password must be at least 8 characters long!")
    if request.form['c_password'] != request.form['password']:
        is_valid = False
        flash("Passwords must match!")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please use a valid email address!")

    if not is_valid:
        return redirect('/')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "INSERT into users (first_name, last_name, email, password, user_level, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, 1, NOW(), NOW())"
        data = {
            'fn': request.form['first_name'],
            'ln': request.form['last_name'],
            'em': request.form['email'],
            'pw': bcrypt.generate_password_hash(request.form['password'])
        }
        user_id = mysql.query_db(query, data)
        session['user_id'] = user_id
        session['user_level'] = 1

        return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login_user():

    is_valid = True

    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter your email!")
    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter your password!")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid email address!")

    if not is_valid:
        return redirect('/')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT * from users where users.email = %(em)s"
        data = {
            'em': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['user_id'] = user[0]['user_id']
                session['user_level'] = user[0]['user_level']
                return redirect('/dashboard')
            else:
                flash("Invalid password!")
                return redirect('/')

        else:
            flash("Please use a valid email address!")
            return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    mysql = connectToMySQL('e_nutrition')
    query = "SELECT * from users where users.user_id = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    user = mysql.query_db(query, data)

    if user:
        mysql = connectToMySQL('e_nutrition')
        query = "select users.user_id, posts.post_id, posts.author, users.first_name, posts.created_at, posts.post_name, posts.post_content, COUNT(posts_id) as times_liked FROM posts left JOIN liked_posts ON posts.post_id = liked_posts.posts_id JOIN users ON posts.author = users.user_id GROUP BY posts.post_id"
        posts = mysql.query_db(query)

        mysql = connectToMySQL('e_nutrition')
        query = "SELECT posts_id from liked_posts where users_id=%(uid)s"
        data = {
            'uid': session['user_id']
        }
        liked_posts_ids = [data['posts_id'] for data in mysql.query_db(query, data)]

        return render_template('dashboard.html', user=user[0], posts=posts, liked_posts_ids=liked_posts_ids)

    else:
        return render_template('dashboard.html', user=user[0], posts=[])

@app.route('/posts/add')
def add_post():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        return render_template("add_post.html")

@app.route('/posts/create', methods=['POST'])
def save_post():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:

        is_valid = True

        if len(request.form['post_content']) < 5:
            is_valid = False
            flash("Your post must contain at least 5 characters!")
        if len(request.form['post_name']) < 1:
            is_valid = False
            flash("Your post name cannot be blank!")
        if len(request.form['post_name']) > 150:
            is_valid = False
            flash("Your post name cannot be more than 150 characters!")

        if is_valid:
            mysql = connectToMySQL('e_nutrition')
            query = "INSERT into posts (post_name, post_content, author, created_at, updated_at) VALUES (%(pname)s, %(pcon)s, %(uid)s, NOW(), NOW())"
            data = {
                'pname': request.form['post_name'],
                'pcon': request.form['post_content'],
                'uid': session['user_id']
            }
            post = mysql.query_db(query, data)
            return redirect('/dashboard')

        return redirect('/posts/add')


@app.route('/edit_post/<post_id>')
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect('/')

    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT * from posts where post_id = %(pid)s"
        data = {
            'pid': post_id
        }
        post_data = mysql.query_db(query,data)
        return render_template('edit_post.html', post_data=post_data[0])

@app.route('/update_post/<post_id>', methods=['POST'])
def update_tweet(post_id):
    if 'user_id' not in session:
        return redirect('/')

    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        is_valid = True

        if len(request.form['post_content']) < 5:
            is_valid = False
            flash("Your post must contain at least 5 characters!")
        if len(request.form['post_name']) < 1:
            is_valid = False
            flash("Your post name cannot be blank!")
        if len(request.form['post_name']) > 150:
            is_valid = False
            flash("Your post name cannot be more than 150 characters!")

        if is_valid:
            mysql = connectToMySQL("e_nutrition")
            query = "UPDATE posts SET posts.post_name=%(pname)s, posts.post_content=%(pcon)s, posts.updated_at=NOW() WHERE posts.post_id = %(pid)s"
            data = {
                'pname': request.form['post_name'],
                'pcon': request.form['post_content'],
                'pid': post_id
            }
            mysql.query_db(query,data)
            return redirect("/dashboard")

        return redirect("/edit_post/{}".format(post_id))

@app.route('/delete/<post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "DELETE from liked_posts where posts_id=%(pid)s"
        data = {
            'pid': post_id
        }
        mysql.query_db(query, data)

        mysql = connectToMySQL('e_nutrition')
        query = "DELETE from posts where post_id = %(pid)s"
        mysql.query_db(query, data)
        return redirect('/dashboard')

@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT users.user_id, users.first_name, users.last_name, users.email, users.user_level from users"
        users = mysql.query_db(query)
        return render_template('users.html', users=users)

@app.route('/make_admin/<user_id>')
def make_admin(user_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "UPDATE users SET users.user_level = 9 where users.user_level=1 and users.user_id=%(uid)s"
        data = {
            'uid': user_id
        }
        mysql.query_db(query, data)
        return redirect('/users')

@app.route('/remove_admin/<user_id>')
def remove_admin(user_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "UPDATE users SET users.user_level = 1 where users.user_level=9 and users.user_id=%(uid)s"
        data = {
            'uid': user_id
        }
        mysql.query_db(query, data)
        if session['user_level'] != 9:
            return redirect('/dashboard')
        return redirect('/users')

@app.route('/needed_calories')
def needed_calories():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 1:
        return redirect('/dashboard')
    return render_template('needed_calories.html')

@app.route('/daily_intake')
def daily_intake():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 1:
        return redirect('/dashboard')
    return render_template('daily_intake.html')

@app.route('/food/add')
def add_food():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        return render_template("add_food.html")

@app.route('/create/food', methods=['POST'])
def create_food():
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        is_valid = True
        if len(request.form['food_name']) < 1:
            is_valid = False
            flash("Food name cannot be empty!")
        if len(request.form['food_calories']) < 1:
            is_valid = False
            flash("Food calories cannot be empty!")
        if is_valid:
            mysql = connectToMySQL('e_nutrition')
            query = "INSERT into food (food_name, food_calories, created_at, updated_at) values (%(fn)s, %(fc)s, NOW(), NOW())"
            data = {
                'fn': request.form['food_name'],
                'fc': request.form['food_calories']
            }
            mysql.query_db(query, data)
            return redirect('/food')
        else:
            return redirect('/food/add')

@app.route('/edit_food/<food_id>')
def edit_food(food_id):
    if 'user_id' not in session:
        return redirect('/')

    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT * from food where food_id = %(fid)s"
        data = {
            'fid': food_id
        }
        food_data = mysql.query_db(query,data)
        return render_template('edit_food.html', food_data=food_data[0])

@app.route('/update_food/<food_id>', methods=['POST'])
def update_food(food_id):
    if 'user_id' not in session:
        return redirect('/')

    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        is_valid = True

        if len(request.form['food_name']) < 1:
            is_valid = False
            flash("Food name cannot be blank!")
        if len(request.form['food_calories']) < 1:
            is_valid = False
            flash("Food calories cannot be blank!")

        if is_valid:
            mysql = connectToMySQL("e_nutrition")
            query = "UPDATE food SET food.food_name=%(fname)s, food.food_calories=%(fcal)s, food.updated_at=NOW() WHERE food.food_id = %(fid)s"
            data = {
                'fname': request.form['food_name'],
                'fcal': request.form['food_calories'],
                'fid': food_id
            }
            mysql.query_db(query,data)
            return redirect("/food")

        return redirect("/edit_food/{}".format(post_id))

@app.route('/delete_food/<food_id>')
def delete_food(food_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL("e_nutrition")
        query = "DELETE FROM food WHERE food.food_id = %(fid)s"
        data = {
            'fid': food_id
        }
        mysql.query_db(query,data)
        return redirect('/food')

@app.route('/food')
def food():
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT food.food_id, food.food_name, food.food_calories from food"
        food = mysql.query_db(query)
        return render_template('food.html', food=food)

@app.route('/on_search', methods=['POST'])
def on_search():
    mysql = connectToMySQL('e_nutrition')
    query = "SELECT food.food_name, food.food_calories from food where food.food_name LIKE %%(fname)s;"
    print(request.form['search_term'])
    data = {
        'fname': request.form['search_term'] + '%'
    }
    results = mysql.query_db(query, data)
    return render_template('partials/search_results.html', results=results)

@app.route('/posts/<post_id>/like')
def like_post(post_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] == 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "INSERT into liked_posts (users_id, posts_id) VALUES (%(uid)s, %(pid)s)"
        data = {
            'uid': session['user_id'],
            'pid': post_id
        }
        mysql.query_db(query, data)
        return redirect('/dashboard')

@app.route('/posts/<post_id>/unlike')
def unlike_post(post_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] == 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "DELETE from liked_posts where users_id=%(uid)s and posts_id=%(pid)s"
        data = {
            'uid': session['user_id'],
            'pid': post_id
        }
        mysql.query_db(query, data)
        return redirect('/dashboard')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route('/user_profile/<user_id>')
def user_profile(user_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] == 9:
        return redirect('/dashboard')
    else:
        mysql = connectToMySQL('e_nutrition')
        query = "SELECT * from users where user_id=%(uid)s"
        data = {
            'uid': user_id,
        }
        user = mysql.query_db(query, data)

        return render_template('user_profile.html', user=user[0])

@app.route('/upload/<user_id>', methods=['POST'])
def upload(user_id):

    target = os.path.join(APP_ROOT, 'static')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)
    else:
        print("Could not create specified directory")
    for upload in request.files.getlist("file"):
        print(upload)
        filename = upload.filename
        destination = "/".join([target, filename])
        print(destination)
        upload.save(destination)
        mysql = connectToMySQL('e_nutrition')
        query = "UPDATE users set file_path=%(fp)s where users.user_id=%(uid)s"
        data = {
            'fp': filename,
            'uid': user_id
        }
        mysql.query_db(query, data)

        return redirect("/user_profile/{}".format(user_id))

@app.route('/post_details/<post_id>')
def post_details(post_id):
    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 1:
        return redirect('/dashboard')

    mysql = connectToMySQL('e_nutrition')
    query = "SELECT posts.post_id, posts.post_name, posts.post_content, users.first_name from posts join users on posts.author = users.user_id where posts.post_id=%(pid)s"
    data = {
        'pid': post_id
    }
    result = mysql.query_db(query, data)

    if result:

        mysql = connectToMySQL('e_nutrition')
        query = "SELECT users.first_name, users.last_name, posts.author, users.user_id from liked_posts join users on liked_posts.users_id = users.user_id join posts on liked_posts.posts_id = posts.post_id where liked_posts.posts_id=%(pid)s"
        data = {
            'pid': post_id
        }
        users_who_liked_post = mysql.query_db(query, data)

        return render_template('post_details.html', result=result[0], users_who_liked_post=users_who_liked_post)

    return redirect('/dashboard')

@app.route('/edit_user/<user_id>')
def edit_user(user_id):

    if 'user_id' not in session:
        return redirect('/')
    if session['user_level'] != 1:
        return redirect('/dashboard')

    mysql = connectToMySQL('e_nutrition')
    query = "SELECT * from users where user_id = %(uid)s"
    data = {
        'uid': user_id
    }
    user_data = mysql.query_db(query,data)
    return render_template('edit_user.html', user_data=user_data[0])

@app.route('/update_user/<user_id>', methods=['POST'])
def update_user(user_id):
    if 'user_id' not in session:
        return redirect('/')
    else:
        is_valid = True

        if len(request.form['first_name']) < 1:
            is_valid = False
            flash("First name cannot be blank!")
        if len(request.form['last_name']) < 1:
            is_valid = False
            flash("Last name cannot be blank!")
        if not EMAIL_REGEX.match(request.form['email']):
            is_valid = False
            flash("Please enter a valid email address!")
        if len(request.form['password']) < 8:
            is_valid = False
            flash("Password must be at least 8 characters long!")
        if request.form['c_password'] != request.form['password']:
            is_valid = False
            flash("Passwords must match!")


        if is_valid:
            mysql = connectToMySQL("e_nutrition")
            query = "UPDATE users SET users.first_name=%(fn)s, users.last_name=%(ln)s, users.email=%(em)s, users.password=%(pw)s, users.updated_at=NOW() WHERE users.user_id = %(uid)s"
            data = {
                'fn': request.form['first_name'],
                'ln': request.form['last_name'],
                'em': request.form['email'],
                'pw': bcrypt.generate_password_hash(request.form['password']),
                'uid': user_id
            }
            mysql.query_db(query,data)
            return redirect("/user_profile/{}".format(user_id))

        return redirect("/edit_user/{}".format(user_id))


if __name__ == "__main__":
    app.run(debug=True)
