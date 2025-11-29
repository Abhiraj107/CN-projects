from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import functools

app = Flask(__name__)
app.secret_key = "supersecretkey123"

app.config["MONGO_URI"] = "mongodb://localhost:27017/bookstore"
mongo = PyMongo(app)

# ========================= PREMIUM TEMPLATES =========================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}BookHub{% endblock %} - Premium Bookstore</title>
    
    <!-- Bootstrap 5 + Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts: Playfair Display (headings) + Inter (body) -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3f37c9;
            --accent: #f72585;
            --text: #240046;
            --light: #f8f9fa;
            --gray: #6c757d;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f5f7ff 0%, #e0e7ff 100%);
            color: var(--text);
            min-height: 100vh;
        }
        h1, h2, h3, h4, h5 { font-family: 'Playfair Display', serif; }
        
        .navbar {
            background: rgba(67, 97, 238, 0.95) !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(67, 97, 238, 0.3);
        }
        .navbar-brand {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .hero {
            background: linear-gradient(rgba(67, 97, 238, 0.8), rgba(247, 37, 133, 0.7)), url('https://images.unsplash.com/photo-1497633765639-5f052b08d49e?q=80&w=2070') center/cover no-repeat;
            height: 90vh;
            min-height: 500px;
            display: flex;
            align-items: center;
            color: white;
            text-align: center;
        }
        
        .book-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            height: 100%;
        }
        .book-card:hover {
            transform: translateY(-15px) scale(1.02);
            box-shadow: 0 20px 40px rgba(67, 97, 238, 0.25);
        }
        .book-cover-placeholder {
            height: 280px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
            font-weight: bold;
        }
        .price-tag {
            background: var(--accent);
            color: white;
            padding: 8px 16px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1.1rem;
        }
        .btn-primary {
            background: var(--primary);
            border: none;
            padding: 12px 32px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(67,97,238,0.4);
        }
        .form-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        footer {
            background: #240046;
            color: #a29bfe;
            padding: 60px 0 30px;
            margin-top: 100px;
        }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">
                <i class="fas fa-book-open-reader me-2"></i>BookHub
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    {% if session['user'] %}
                        <li class="nav-item mx-2">
                            <span class="nav-link"><i class="fas fa-user-circle"></i> {{ session['user'] }}</span>
                        </li>
                        <li class="nav-item"><a class="nav-link" href="{{ url_for('catalogue') }}">Catalogue</a></li>
                        <li class="nav-item"><a class="nav-link text-warning" href="{{ url_for('logout') }}">Logout</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Login</a></li>
                        <li class="nav-item"><a class="nav-link btn btn-outline-light px-4 ms-2" href="{{ url_for('register') }}">Sign Up</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container mt-5 pt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, msg in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        <strong>{{ msg }}</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    {% block content %}{% endblock %}

    <!-- Footer -->
    <footer class="text-center">
        <div class="container">
            <p class="fs-3 fw-bold mb-3" style="color: #a29bfe;">BookHub</p>
            <p>Discover stories that change your world.</p>
            <p class="text-muted">&copy; 2025 BookHub. Made with ❤️ for book lovers.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

HOME_TEMPLATE = BASE_TEMPLATE.replace(
    "{% block content %}{% endblock %}",
    """
    {% block content %}
    <div class="hero">
        <div class="container">
            <h1 class="display-1 fw-bold mb-4">Welcome to BookHub</h1>
            <p class="lead fs-3 mb-5 opacity-90">Discover your next favorite book from thousands of titles</p>
            <a href="{{ url_for('catalogue') }}" class="btn btn-light btn-lg px-5 py-3 fs-4">
                <i class="fas fa-search me-3"></i>Explore Books
            </a>
        </div>
    </div>

    <div class="container my-5 py-5">
        <div class="row text-center">
            <div class="col-md-4 mb-4">
                <i class="fas fa-shipping-fast fa-3x text-primary mb-3"></i>
                <h5>Fast Delivery</h5>
                <p class="text-muted">Get books delivered in 2-3 days</p>
            </div>
            <div class="col-md-4 mb-4">
                <i class="fas fa-headset fa-3x text-primary mb-3"></i>
                <h5>24/7 Support</h5>
                <p class="text-muted">We're always here to help</p>
            </div>
            <div class="col-md-4 mb-4">
                <i class="fas fa-shield-alt fa-3x text-primary mb-3"></i>
                <h5>Secure Payment</h5>
                <p class="text-muted">100% secure transactions</p>
            </div>
        </div>
    </div>
    {% endblock %}
    """
).replace("{% block title %}BookHub{% endblock %}", "Home")

LOGIN_TEMPLATE = BASE_TEMPLATE.replace(
    "{% block content %}{% endblock %}",
    """
    {% block content %}
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="form-card p-5">
                    <div class="text-center mb-5">
                        <i class="fas fa-book-open-reader fa-4x text-primary"></i>
                        <h2 class="mt-4">Welcome Back</h2>
                        <p class="text-muted">Login to continue your reading journey</p>
                    </div>
                    <form method="POST">
                        <div class="mb-4">
                            <label class="form-label fw-600">Email Address</label>
                            <input type="email" name="email" class="form-control form-control-lg" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-600">Password</label>
                            <input type="password" name="password" class="form-control form-control-lg" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 py-3 fs-5">Login Now</button>
                    </form>
                    <p class="text-center mt-4">
                        New here? <a href="{{ url_for('register') }}" class="text-decoration-none fw-bold">Create an account</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
).replace("{% block title %}BookHub{% endblock %}", "Login")

REGISTER_TEMPLATE = BASE_TEMPLATE.replace(
    "{% block content %}{% endblock %}",
    """
    {% block content %}
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="form-card p-5">
                    <div class="text-center mb-5">
                        <i class="fas fa-user-plus fa-4x text-success"></i>
                        <h2 class="mt-4">Join BookHub</h2>
                        <p class="text-muted">Create your account and start reading</p>
                    </div>
                    <form method="POST">
                        <div class="mb-4">
                            <label class="form-label fw-600">Full Name</label>
                            <input type="text" name="name" class="form-control form-control-lg" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-600">Email Address</label>
                            <input type="email" name="email" class="form-control form-control-lg" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-600">Password</label>
                            <input type="password" name="password" class="form-control form-control-lg" required>
                        </div>
                        <button type="submit" class="btn btn-success w-100 py-3 fs-5">Create Account</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
).replace("{% block title %}BookHub{% endblock %}", "Register")

CATALOGUE_TEMPLATE = BASE_TEMPLATE.replace(
    "{% block content %}{% endblock %}",
    """
    {% block content %}
    <div class="container py-5">
        <div class="d-flex justify-content-between align-items-center mb-5">
            <h1 class="display-5 fw-bold">Our Collection</h1>
            <span class="badge bg-primary fs-5 px-4 py-3">{{ books|length }} Books</span>
        </div>

        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4">
            {% for b in books %}
            <div class="col">
                <div class="book-card">
                    <div class="book-cover-placeholder">
                        <i class="fas fa-book fa-2x"></i>
                    </div>
                    <div class="p-4">
                        <h5 class="fw-bold">{{ b.title }}</h5>
                        <p class="text-muted mb-2">by {{ b.author }}</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹{{ b.price }}</span>
                            <button class="btn btn-outline-primary rounded-pill px-4">
                                <i class="fas fa-shopping-cart"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """
).replace("{% block title %}BookHub{% endblock %}", "Catalogue")

# ========================= ROUTES =========================
@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = mongo.db.users.find_one({"email": request.form["email"], "password": request.form["password"]})
        if user:
            session["user"] = user["name"]
            flash("Welcome back, " + user["name"] + "!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials!", "error")
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if mongo.db.users.find_one({"email": request.form["email"]}):
            flash("Email already exists!", "error")
        else:
            mongo.db.users.insert_one({
                "name": request.form["name"],
                "email": request.form["email"],
                "password": request.form["password"]
            })
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
    return render_template_string(REGISTER_TEMPLATE)

@app.route("/catalogue")
def catalogue():
    books = list(mongo.db.books.find())
    return render_template_string(CATALOGUE_TEMPLATE, books=books)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("home"))

# ========================= SAMPLE DATA =========================
def insert_sample_books():
    if mongo.db.books.count_documents({}) == 0:
        sample_books = [
            {"title": "1984", "author": "George Orwell", "price": 299},
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": 349},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "price": 399},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "price": 279},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "price": 499},
            {"title": "Atomic Habits", "author": "James Clear", "price": 599},
            {"title": "Sapiens", "author": "Yuval Noah Harari", "price": 650},
            {"title": "The Alchemist", "author": "Paulo Coelho", "price": 320},
        ]
        mongo.db.books.insert_many(sample_books)
        print("Premium sample books added!")

with app.app_context():
    insert_sample_books()

if __name__ == "__main__":
    app.run(debug=True)