from sqlalchemy import create_engine, func
from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'michelle123'


db_path = "sqlite:///C:/Users/rosem/OneDrive/Desktop/Michelle/IITM/MAD_proj/Product.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Category(db.Model):
    __tablename__ = 'CategoryT'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), unique=True)
    products = db.relationship('Product', backref='category', cascade='all, delete-orphan', lazy=True)

class Product(db.Model):
    __tablename__ = 'Product'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Category = db.Column(db.String(100))
    Category_ID = db.Column(db.Integer, db.ForeignKey('CategoryT.ID'), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Manager(db.Model):
    __tablename__ = 'manager'
    Mid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Mname = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    Memail = db.Column(db.String(255), unique=True, nullable=False)
    Mpassword = db.Column(db.String(255), nullable=False)

class CartItem(db.Model):
    __tablename__ = 'Cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ID'), nullable=False)
    product = db.relationship('Product', backref='cart_items')
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

engine = create_engine(db_path)

@app.route("/", methods =["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/logIn", methods=["GET", "POST"])
def logIn():
    if request.method == "POST":
        # Handle the login form submission
        user_name = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database and the provided password is correct
        user = User.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            # You can add logic for successful login, e.g., setting session variables
            return redirect(url_for('product'))

        else:
            return "Invalid username or password!"

    # For GET request, simply render the login template
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # Handle the registration form submission
        user_name = request.form['username']
        user_email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.user_name == user_name) | (User.user_email == user_email)).first()
        if existing_user:
            return "Username or Email already exists!"

        # Create a new user and add it to the database
        new_user = User(user_name=user_name, user_email=user_email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return render_template("product.html")

    return render_template("index.html")

#-----------------------------------------------------------------------------

@app.route("/MlogIn", methods=["GET", "POST"])
def MlogIn():
    if request.method == "POST":
        #  login form submission
        Mname = request.form['username']
        Mpassword = request.form['password']

        # Check if manager exists in database
        manager = Manager.query.filter_by(Mname=Mname).first()

        if manager and manager.Mpassword == Mpassword:
            return redirect(url_for('manager_home'))
        else:
            # Invalid username or password
            return "Invalid username or password!"
    else:
        return render_template("Mindex.html")

@app.route('/Mregister', methods=['GET', 'POST'])
def Mregister():
    if request.method == "POST":
        # registration form submission
        Mname = request.form['username']
        Memail = request.form['email']
        Mpassword = request.form['password']

        # already exists in the database
        existing_user = User.query.filter((Manager.Mname == Mname) | (Manager.Memail == Memail)).first()
        if existing_user:
            return "Username or Email already exists!"

        # Create a new user and add it to the database
        new_user = Manager(Mname=Mname, Memail=Memail, Mpassword=Mpassword)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('manager_home'))

    return render_template("Mindex.html")

#-------------------------------
@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/user_login')
def user_login():
    return render_template('index.html')

@app.route('/admin_login')
def admin_login():
    return render_template('Mindex.html')


@app.route("/fruits", methods =["GET", "POST"])
def fruits():
    products = Product.query.all()
    return render_template("fruit.html", products = products)

@app.route("/products", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        search_keyword = request.form["search_keyword"]
        categories = Category.query.filter(Category.Name.ilike(f"%{search_keyword}%")).all()
    else:
        categories = Category.query.all()

    return render_template("product.html", categories=categories)


@app.route('/manager_home', methods =["GET", "POST"])
def manager_home():
    categories = Category.query.all()
    return render_template('manager_home.html', categories = categories)


@app.route("/all_products")
def all_products():
    return render_template("all_products.html")

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        try:
            # add the category to the database
            new_category = request.form['category_name']
            existing_category = Category.query.filter(func.lower(Category.Name) == func.lower(new_category)).first()
            if existing_category:
                return "Category already exists!"
            else:
                # Insert the new category into the database
                new_category = Category(Name=new_category)
                db.session.add(new_category)
                db.session.commit()
                # Redirect to the page showing all categories or a success page
                categories = Category.query.all()
                return render_template("manager_home.html", categories = categories)
            
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred. Please try again later.",500
    else:
        return render_template('category_form.html')


@app.route('/delete_category/<int:category_id>/<string:category_name>', methods=['GET', 'POST'])
def delete_category(category_id, category_name):
    if request.method == 'POST':
        existing_category = Category.query.filter_by(ID=category_id).first()
        if not existing_category:
            return "Category does not exist!"
        else:
            # Delete the category from the database
            db.session.delete(existing_category)
            db.session.commit()
    
            categories = Category.query.all()
            return render_template("manager_home.html", categories=categories)

    else:
        return render_template('delete_category.html', category_id=category_id, category_name=category_name)


    
@app.route('/edit_category/<int:category_id>/<string:category_name>', methods=['GET', 'POST'])
def edit_category(category_id, category_name):
    if request.method == 'POST':
        new_category_name = request.form['new_category_name']

        # Check if the new category name already exists in the database
        existing_category = Category.query.filter(func.lower(Category.Name) == func.lower(new_category_name)).first()
        if existing_category:
            return "Category already exists!"
        else:
            # Update the category name
            category_to_edit = Category.query.filter_by(ID=category_id).first()
            category_to_edit.Name = new_category_name
            db.session.commit()

            # Redirect to the page showing all categories 
            categories = Category.query.all()
            return render_template('manager_home.html', categories=categories)

    else:
        return render_template('edit_category.html', category_id=category_id, category_name=category_name)


@app.route('/add_products/<int:category_id>/<string:category_name>', methods=['GET', 'POST'])
def add_products(category_id, category_name):
    if request.method == 'POST':
        Name = request.form['Name']
        Category = category_name  # Use the provided category_name
        Category_ID = category_id  # Use the provided category_id 
        Price = float(request.form['Price'])
        Quantity = int(request.form['Quantity'])
        Description = request.form['Description']

        # Check if the product already exists in the database
        existing_product = Product.query.filter(func.lower(Product.Name) == func.lower(Name)).first()

        if existing_product:
            # Update the quantity of the existing product
            existing_product.Quantity += Quantity
            db.session.commit()
            return "Product Exists, Quantity of Product Updated"
        else:
            # Insert a new product into the database
            new_product = Product(Name=Name, Category=Category, Category_ID=Category_ID, Price=Price, Quantity=Quantity, Description=Description)
            db.session.add(new_product)

        db.session.commit()
        products = Product.query.all()
        return render_template('fruit.html', products=products)
    else:
        return render_template('add_products.html', category_id=category_id, category_name=category_name)



@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if request.method == 'POST':
        # Query the database for the product with the given ID
        product = Product.query.get(product_id)

        if not product:
            return "Product not found!"

        try:
            # Delete the product from the database
            db.session.delete(product)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return "An error occurred. Please try again later.", 500

        products = Product.query.all()
        return render_template('fruit.html',products = products)

    else:
        # If it's not a POST request, return a method not allowed message
        return "Method not allowed", 405

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        
        description = request.form['description']

        # Update the product attributes
        product.Name = name
        product.Price = price
        product.Description = description

        db.session.commit()

        return redirect(url_for('fruits', product_id=product_id))

    return render_template('edit_product.html', product=product)


@app.route('/view_products/<int:category_id>/<string:category_name>')
def view_products(category_id, category_name):
    category = Category.query.filter_by(ID=category_id).first()

    products = Product.query.filter_by(Category_ID=category_id).all()
    return render_template('view_products.html', category=category, products=products)


@app.route('/buy_products/<int:category_id>/<string:category_name>', methods=['GET', 'POST'])
def buy_products(category_id, category_name):
    category = Category.query.filter_by(ID=category_id).first()
    if not category:
        return "Category does not exist!"
    
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword", "")
        
        products = Product.query.filter(
            (Product.Category_ID == category_id) &
            (
                (Product.Name.ilike(f"%{search_keyword}%")) |
                (Product.Price.ilike(f"%{search_keyword}%"))
            )
        ).all()
    else:
        products = Product.query.filter_by(Category_ID=category_id).all()
    
    return render_template('buy_products.html', category=category, products=products)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Product not found!", 404

    quantity = int(request.form['quantity'])

    if quantity > product.Quantity:
        return "Cannot add more than {} items for {}".format(product.Quantity, product.Name)

    total_price = product.Price * quantity

    cart_item = CartItem.query.filter_by(product_id=product_id).first()

    if cart_item:
        # Check if the total quantity in the cart + the new quantity exceeds the available product quantity
        if cart_item.quantity + quantity > product.Quantity:
            return "Cannot add more than {} items for {}".format(product.Quantity, product.Name)

        cart_item.quantity += quantity
        cart_item.total_price += total_price
    else:
        cart_item = CartItem(product_id=product_id, name=product.Name, quantity=quantity, total_price=total_price)
        db.session.add(cart_item)

    db.session.commit()

    return redirect(url_for('product'))

@app.route('/view_cart', methods=['GET', 'POST'])
def view_cart():
    cart_items = CartItem.query.options(db.joinedload(CartItem.product)).all()
    total_amount = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        action = request.form.get('action')
        item_id = int(request.form.get('item_id'))

        if action == 'update':
            new_quantity = int(request.form.get('new_quantity'))
            if new_quantity <= 0:
                return "Invalid quantity"

            cart_item = CartItem.query.get(item_id)
            if cart_item:
                cart_item.quantity = new_quantity
                cart_item.total_price = cart_item.product.Price * new_quantity
                total_amount = sum(item.total_price for item in cart_items)
                db.session.commit()

        elif action == 'delete':
            cart_item = CartItem.query.get(item_id)
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()

    return render_template('view_cart.html', cart_items=cart_items, total_amount=total_amount)


# from flask import session

@app.route('/logout')
def logout():
    # Clear the cart items associated with the current session
    CartItem.query.delete()
    db.session.commit()

    # # Clear the session data 
    # session.clear()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)


 