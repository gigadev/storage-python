from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId
from functools import wraps
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

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

def get_user_id():
    user = session.get('user')
    if not user:
        return None
    # Use sub (Google ID) if available, else email
    return user.get('sub') or user.get('email')

@app.before_request
def ensure_user_in_db():
    if app.config.get('USE_AUTH', True):
        user = session.get('user')
        if user:
            user_id = get_user_id()
            g.user_id = user_id
            # Upsert user in users collection
            mongo.db.users.update_one(
                {'_id': user_id},
                {'$set': {'email': user.get('email'), 'name': user.get('name', user.get('email'))}},
                upsert=True
            )
        else:
            g.user_id = None
    else:
        g.user_id = 'demo-user'

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
    locations = mongo.db.locations.find({'user_id': g.user_id})
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
@login_required
def add_location():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        mongo.db.locations.insert_one({'name': name, 'description': description, 'user_id': g.user_id})
        flash('Location added!')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', action='Add')

@app.route('/locations/<location_id>')
@login_required
def view_location(location_id):
    loc = mongo.db.locations.find_one({'_id': ObjectId(location_id), 'user_id': g.user_id})
    return render_template('location_view.html', loc=loc)

@app.route('/locations/<location_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    loc = mongo.db.locations.find_one({'_id': ObjectId(location_id), 'user_id': g.user_id})
    if not loc:
        flash('Location not found.', 'danger')
        return redirect(url_for('list_locations'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        mongo.db.locations.update_one({'_id': ObjectId(location_id), 'user_id': g.user_id}, {'$set': {'name': name, 'description': description}})
        flash('Location updated!')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', action='Edit', loc=loc)

@app.route('/locations/<location_id>/delete')
@login_required
def delete_location(location_id):
    mongo.db.locations.delete_one({'_id': ObjectId(location_id), 'user_id': g.user_id})
    flash('Location deleted!')
    return redirect(url_for('list_locations'))

@app.route('/items')
@login_required
def list_items():
    items = list(mongo.db.storage_items.find({'user_id': g.user_id}))
    locations = {str(loc['_id']): loc['name'] for loc in mongo.db.locations.find({'user_id': g.user_id})}
    for item in items:
        item['location_name'] = locations.get(item.get('location_id', ''), 'Unknown')
    return render_template('items.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    locations = list(mongo.db.locations.find({'user_id': g.user_id}))
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'brand': request.form.get('brand', ''),
            'manufacturer': request.form.get('manufacturer', ''),
            'size': request.form.get('size', ''),
            'quantity': request.form.get('quantity', ''),
            'units': request.form.get('units', ''),
            'servings_per': request.form.get('servings_per', ''),
            'nutritional_info': request.form.get('nutritional_info', ''),
            'date_purchased': request.form.get('date_purchased', ''),
            'manufactured_date': request.form.get('manufactured_date', ''),
            'expiration_date': request.form.get('expiration_date', ''),
            'ingredients': request.form.get('ingredients', ''),
            'other_info': request.form.get('other_info', ''),
            'upc': request.form.get('upc', ''),
            'box': request.form.get('box', ''),
            'location_id': request.form['location_id'],
            'user_id': g.user_id
        }
        mongo.db.storage_items.insert_one(data)
        flash('Item added!')
        return redirect(url_for('list_items'))
    return render_template('item_form.html', action='Add', locations=locations, item=None)

@app.route('/items/<item_id>')
@login_required
def view_item(item_id):
    item = mongo.db.storage_items.find_one({'_id': ObjectId(item_id), 'user_id': g.user_id})
    location = mongo.db.locations.find_one({'_id': ObjectId(item['location_id']), 'user_id': g.user_id}) if item and 'location_id' in item else None
    return render_template('item_view.html', item=item, location=location)

@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = mongo.db.storage_items.find_one({'_id': ObjectId(item_id), 'user_id': g.user_id})
    locations = list(mongo.db.locations.find({'user_id': g.user_id}))
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('list_items'))
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'brand': request.form.get('brand', ''),
            'manufacturer': request.form.get('manufacturer', ''),
            'size': request.form.get('size', ''),
            'quantity': request.form.get('quantity', ''),
            'units': request.form.get('units', ''),
            'servings_per': request.form.get('servings_per', ''),
            'nutritional_info': request.form.get('nutritional_info', ''),
            'date_purchased': request.form.get('date_purchased', ''),
            'manufactured_date': request.form.get('manufactured_date', ''),
            'expiration_date': request.form.get('expiration_date', ''),
            'ingredients': request.form.get('ingredients', ''),
            'other_info': request.form.get('other_info', ''),
            'upc': request.form.get('upc', ''),
            'box': request.form.get('box', ''),
            'location_id': request.form['location_id']
        }
        mongo.db.storage_items.update_one({'_id': ObjectId(item_id), 'user_id': g.user_id}, {'$set': data})
        flash('Item updated!')
        return redirect(url_for('list_items'))
    return render_template('item_form.html', action='Edit', locations=locations, item=item)

@app.route('/items/<item_id>/delete')
@login_required
def delete_item(item_id):
    mongo.db.storage_items.delete_one({'_id': ObjectId(item_id), 'user_id': g.user_id})
    flash('Item deleted!')
    return redirect(url_for('list_items'))

@app.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(url_for('import_csv'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('import_csv'))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file.', 'danger')
            return redirect(url_for('import_csv'))
        
        try:
            # Read CSV file
            df = pd.read_csv(file)
            
            # Expected columns (based on the sample CSV)
            required_columns = ['ItemName', 'ItemLocation']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
                return redirect(url_for('import_csv'))
            
            # Track import statistics
            locations_created = 0
            items_imported = 0
            errors = []
            
            # Get or create locations
            location_map = {}  # Map location names to ObjectIds
            
            for index, row in df.iterrows():
                try:
                    # Get or create location
                    location_name = str(row['ItemLocation']).strip()
                    
                    if location_name not in location_map:
                        # Check if location exists for this user
                        existing_loc = mongo.db.locations.find_one({
                            'name': location_name,
                            'user_id': g.user_id
                        })
                        
                        if existing_loc:
                            location_map[location_name] = existing_loc['_id']
                        else:
                            # Create new location
                            new_loc = mongo.db.locations.insert_one({
                                'name': location_name,
                                'description': f'Auto-created from CSV import',
                                'user_id': g.user_id
                            })
                            location_map[location_name] = new_loc.inserted_id
                            locations_created += 1
                    
                    # Parse dates
                    expiration_date = None
                    if pd.notna(row.get('ExpirationDate')):
                        try:
                            expiration_date = pd.to_datetime(row['ExpirationDate']).strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    manufactured_date = None
                    if pd.notna(row.get('Manufactured Date')):
                        try:
                            manufactured_date = pd.to_datetime(row['Manufactured Date']).strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    # Create item document
                    item_data = {
                        'name': str(row['ItemName']).strip(),
                        'location_id': str(location_map[location_name]),
                        'user_id': g.user_id,
                        'brand': str(row.get('Manufacturer', '')).strip() if pd.notna(row.get('Manufacturer')) else '',
                        'quantity': str(row.get('Quantity', '')).strip() if pd.notna(row.get('Quantity')) else '',
                        'servings_per': str(row.get('Servings Per', '')).strip() if pd.notna(row.get('Servings Per')) else '',
                        'size': str(row.get('Servings Size', '')).strip() if pd.notna(row.get('Servings Size')) else '',
                        'units': str(row.get('Units', '')).strip() if pd.notna(row.get('Units')) else '',
                        'expiration_date': expiration_date or '',
                        'box': str(row.get('Box', '')).strip() if pd.notna(row.get('Box')) else '',
                        'manufactured_date': manufactured_date or '',
                        'upc': str(row.get('UPC', '')).strip() if pd.notna(row.get('UPC')) else '',
                        'nutritional_info': str(row.get('Servings', '')).strip() if pd.notna(row.get('Servings')) else '',
                        'other_info': str(row.get('Damaged', '')).strip() if pd.notna(row.get('Damaged')) else '',
                        'date_purchased': '',  # Not in the CSV
                        'ingredients': ''  # Not in the CSV
                    }
                    
                    # Insert item
                    mongo.db.storage_items.insert_one(item_data)
                    items_imported += 1
                    
                except Exception as e:
                    errors.append(f'Row {index + 2}: {str(e)}')
            
            # Display results
            success_msg = f'Import completed! {items_imported} items imported'
            if locations_created > 0:
                success_msg += f', {locations_created} locations created'
            
            flash(success_msg, 'success')
            
            if errors:
                flash(f'Errors encountered: {len(errors)} rows failed. First few errors: {"; ".join(errors[:5])}', 'warning')
            
            return redirect(url_for('list_items'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            return redirect(url_for('import_csv'))
    
    # GET request - show the upload form
    return render_template('import_csv.html')

@app.context_processor
def inject_config():
    return dict(config=app.config)

@app.before_request
def set_demo_user_if_no_auth():
    if not app.config.get('USE_AUTH', True):
        session['user'] = {'name': 'Demo User', 'email': 'demo@example.com'}

if __name__ == '__main__':
    app.run(debug=True)
