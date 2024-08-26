from flask import Flask, render_template, session, redirect, url_for, request,flash
import os
import db
import re
import strong_password

app = Flask(__name__)

app.secret_key = 'NotHacker' # for using sessions

app.config['UPLOAD_FOLDER'] = 'static/uploads'
userdb_connection = db.connect_to_database('users.db')
productdb_connection = db.connect_to_database('products.db')
wishlistdb_connection = db.connect_to_database('wishlist.db')



valid_extension = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in valid_extension

@app.route('/')
def index():
    if 'username' in session:
        print(session['username'])
        products = db.get_products(productdb_connection) # array of tuples
        print(products)
        # send data from python to html
        return render_template('index.html', products=products)

    return redirect(url_for('login'))
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if not 'username' in session: return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(userdb_connection, username)
        # already nor exist
        if password == "" or username == "":
            if strong_password.is_strong(password):   
                flash("Please enter all the required fields!","error")
                return redirect(url_for('register'))

        if user is None:
            db.add_user(userdb_connection, username, password)
            return redirect(url_for('index'))
        else:
            return "User already exists"
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(userdb_connection, username)
        # already nor exist
        if user:
            pwd = db.get_user_password(userdb_connection, username)
            if password == pwd[0]:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Incorrect username or password"
        else:
            return "User does not exist"

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if not 'username' in session: return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('addProduct.html')
    elif request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        product_image = request.files.get("image-upload")
        print(product_image)
        
        if title and price and product_image:
            if allowed_file(product_image.filename):
                db.add_product(productdb_connection, title, price,product_image.filename)
                product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], product_image.filename))
                return redirect(url_for('index'))
            else:
                return "file not allowed"
        
        return "write all your data"
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'username' in session: return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if not 'username' in session: return redirect(url_for('login'))
    username = session.get('username')
    
    userid = db.get_userid_by_name(userdb_connection, username)
    if request.method == 'POST':
        productid = request.form['product_id']        
        # add it to wishlist connected to user id
        db.add_product_to_wishlist(wishlistdb_connection, userid, productid)

    elif request.method == 'GET':
        products = db.get_product_from_wishlist(wishlistdb_connection, productid)
        print(products)
        return render_template('wishlist.html', products=products)



if __name__ == "__main__":
    db.make_user_table(userdb_connection)
    db.make_product_table(productdb_connection)
    db.make_wishlist_table(productdb_connection)
    app.run(debug=True)
