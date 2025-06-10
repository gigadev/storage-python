from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/home_storage')
app.config['USE_AUTH'] = os.environ.get('USE_AUTH', 'true').lower() == 'true'
mongo = PyMongo(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config.get('USE_AUTH', True):
            # If auth is disabled, simulate a logged-in user
            if 'user' not in session:
                session['user'] = {'name': 'Demo User', 'email': 'demo@example.com'}
            return f(*args, **kwargs)
        # If auth is enabled, do NOT set demo user
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    user = session.get('user')
    # Only set demo user if USE_AUTH is false
    if not user and not app.config.get('USE_AUTH', True):
        user = {'name': 'Demo User', 'email': 'demo@example.com'}
    return render_template('index.html', user=user)

# Google SSO routes
@app.route('/login')
def login():
    if not app.config.get('USE_AUTH', True):
        # If auth is disabled, skip login and set demo user
        session['user'] = {'name': 'Demo User', 'email': 'demo@example.com'}
        flash('Demo user logged in (authentication disabled).', 'info')
        return redirect(url_for('index'))
    if 'user' in session:
        return redirect(url_for('index'))
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/authorized')
def authorized():
    if not app.config.get('USE_AUTH', True):
        session['user'] = {'name': 'Demo User', 'email': 'demo@example.com'}
        flash('Demo user logged in (authentication disabled).', 'info')
        return redirect(url_for('index'))
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
    user_info = resp.json()
    session['user'] = user_info
    flash('You have been logged in.', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/locations')
@login_required
def list_locations():
    locations = mongo.db.locations.find()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
@login_required
def add_location():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        mongo.db.locations.insert_one({'name': name, 'description': description})
        flash('Location added!')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', action='Add')

@app.route('/locations/<location_id>')
@login_required
def view_location(location_id):
    loc = mongo.db.locations.find_one({'_id': ObjectId(location_id)})
    return render_template('location_view.html', loc=loc)

@app.route('/locations/<location_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    loc = mongo.db.locations.find_one({'_id': ObjectId(location_id)})
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        mongo.db.locations.update_one({'_id': ObjectId(location_id)}, {'$set': {'name': name, 'description': description}})
        flash('Location updated!')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', action='Edit', loc=loc)

@app.route('/locations/<location_id>/delete')
@login_required
def delete_location(location_id):
    mongo.db.locations.delete_one({'_id': ObjectId(location_id)})
    flash('Location deleted!')
    return redirect(url_for('list_locations'))

@app.route('/items')
@login_required
def list_items():
    items = list(mongo.db.storage_items.find())
    # Attach location name for display
    locations = {str(loc['_id']): loc['name'] for loc in mongo.db.locations.find()}
    for item in items:
        item['location_name'] = locations.get(item.get('location_id', ''), 'Unknown')
    return render_template('items.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    locations = list(mongo.db.locations.find())
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'brand': request.form['brand'],
            'size': request.form['size'],
            'nutritional_info': request.form['nutritional_info'],
            'date_purchased': request.form['date_purchased'],
            'expiration_date': request.form['expiration_date'],
            'ingredients': request.form['ingredients'],
            'other_info': request.form['other_info'],
            'location_id': request.form['location_id']
        }
        mongo.db.storage_items.insert_one(data)
        flash('Item added!')
        return redirect(url_for('list_items'))
    return render_template('item_form.html', action='Add', locations=locations, item=None)

@app.route('/items/<item_id>')
@login_required
def view_item(item_id):
    item = mongo.db.storage_items.find_one({'_id': ObjectId(item_id)})
    location = mongo.db.locations.find_one({'_id': ObjectId(item['location_id'])}) if item and 'location_id' in item else None
    return render_template('item_view.html', item=item, location=location)

@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = mongo.db.storage_items.find_one({'_id': ObjectId(item_id)})
    locations = list(mongo.db.locations.find())
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'brand': request.form['brand'],
            'size': request.form['size'],
            'nutritional_info': request.form['nutritional_info'],
            'date_purchased': request.form['date_purchased'],
            'expiration_date': request.form['expiration_date'],
            'ingredients': request.form['ingredients'],
            'other_info': request.form['other_info'],
            'location_id': request.form['location_id']
        }
        mongo.db.storage_items.update_one({'_id': ObjectId(item_id)}, {'$set': data})
        flash('Item updated!')
        return redirect(url_for('list_items'))
    return render_template('item_form.html', action='Edit', locations=locations, item=item)

@app.route('/items/<item_id>/delete')
@login_required
def delete_item(item_id):
    mongo.db.storage_items.delete_one({'_id': ObjectId(item_id)})
    flash('Item deleted!')
    return redirect(url_for('list_items'))

@app.context_processor
def inject_config():
    return dict(config=app.config)

@app.before_request
def set_demo_user_if_no_auth():
    if not app.config.get('USE_AUTH', True):
        session['user'] = {'name': 'Demo User', 'email': 'demo@example.com'}

if __name__ == '__main__':
    app.run(debug=True)
