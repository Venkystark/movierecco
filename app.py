from bson import ObjectId
from flask import Flask, jsonify, render_template,request, redirect, url_for, flash, session,Blueprint
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import requests
#from collections import Counter
#from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
#from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__,static_url_path='/static')
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['userdb']
users_collection = db['users']
api_key= '211288f73144365d5646dbf944e2c255'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trending')
def trending():
     if 'user_id' in session:
            # Assuming you have stored the username in the session during login
        username = session['user_name']  # Retrieve the username from the session
        userid=session['user_id']
        return render_template('trending.html', username=username)
     else:
        return render_template('trending.html', username=None)  # Pass None if user is not logged in
    #return render_template('trending.html')

@app.route('/trending1')
def trending1():
    return render_template('trending1.html')
 
# Login route
@app.route('/login1', methods=['GET', 'POST'])
def login1():
     if request.method == 'POST':
            # Check which form was submitted based on the 'form_id' field
        if request.form.get('form_id') == 'form1':
            username = request.form['logemail']
            password = request.form['logpass']
            user = db.users.find_one({'username': username})
            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['user_name']=str(user['username'])
                flash('Login successful.', 'success')
                return redirect(url_for('trending'))
            else:
                flash('Login failed. Please check your username and password.', 'danger')
                return render_template('login1.html')
        elif request.form.get('form_id')=='form2':
             username = request.form['logemail1']
             password = request.form['logpass1']
             hashed_password = generate_password_hash(password)
        
        # Check if the username already exists
             if db.users.find_one({'username': username}):
              flash('Username already exists. Please choose a different one.', 'danger')
             else:
              db.users.insert_one({'username': username, 'password': hashed_password,'favourites':[]})
              flash('Registration successful. Please log in.', 'success')
     return render_template('login1.html')
# Dashboard route (requires login) 
"""@app.route('/dashboard1')
def dashboard1():
    if 'user_id' in session:
         movies = movie_data.to_dict(orient='records')
    else:
        return redirect(url_for('login1'))
    return render_template('dashboard1.html', movies=movies) """
# Logout route
@app.route('/userhome')
def userhome():
    return render_template('userhome.html')
@app.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login1'))

@app.route('/api/add-to-favorites', methods=['POST'])
def add_to_favorites():
    try:
        data = request.get_json()
        movie_id = data['movieId']
        #user_id = '123'
        user_id = session.get('user_name')  # Replace with the actual user ID (you may use a session or authentication system)
        action = data.get('action')  # Get the action ('add' or 'remove')
        # Check if the user document exists
        user_document = users_collection.find_one({'username': user_id})

        if not user_document:
            return jsonify({'error': 'User not found'}), 404

        favorite_movies = user_document.get('favourites', [])

        if action == 'add':
            if movie_id not in favorite_movies:
                # If the movie is not in favorites, add it to the array
                favorite_movies.append(movie_id)
                users_collection.update_one({'username': user_id}, {'$set': {'favourites': favorite_movies}})
                return jsonify({'message': 'Movie added to favorites'})
            else:
                return jsonify({'message': 'Movie is already in favorites'}), 400
        elif action == 'remove':
            if movie_id in favorite_movies:
                # If the movie is in favorites, remove it from the array
                favorite_movies.remove(movie_id)
                users_collection.update_one({'username': user_id}, {'$set': {'favourites': favorite_movies}})
                return jsonify({'message': 'Movie removed from favorites'})
            else:
                return jsonify({'message': 'Movie is not in favorites'}), 400
        else:
            return jsonify({'error': 'Invalid action'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/favourites')
def favourites():
    if 'user_id' in session:
        user_id = session['user_id']
        user_document = users_collection.find_one({'_id': ObjectId(user_id)})
       # user_id=session['username']
        #user_document=users_collection.find_one({'username':user_id})
        
        if user_document:
            favorite_movies = user_document.get('favourites', [])
            # You have the list of favorite movie IDs in the 'favorite_movies' variable
            return render_template('favourites.html', favorite_movies=favorite_movies)
        else:
            flash('User not found in database.', 'danger')
            return redirect(url_for('userhome'))
    else:
        return redirect(url_for('login1'))
    
@app.route('/api/get-favorites')
def get_favorites():
    if 'user_id' in session:
        user_id = session['user_id']
        user_document = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_document:
            favorite_movies = user_document.get('favourites', [])
            return jsonify({'favoriteMovies': favorite_movies})
    
    return jsonify({'favoriteMovies': []})  # Return an empty list if the user is not logged in or not found

# Your existing routes ...

@app.route('/recommendations')
def recommendations():
    if 'user_id' in session:
        user_id = session['user_id']
        user_favorites = users_collection.find_one({'_id': ObjectId(user_id)})['favourites']
        return render_template('recommendations.html', recommended_movies=user_favorites)
    else:
        return redirect(url_for('login1'))
    
@app.route('/recco1')
def recco1():
    if 'user_id' in session:
        user_id = session['user_id']
        user_favorites = users_collection.find_one({'_id': ObjectId(user_id)})['favourites']
        return render_template('recco1.html', recommended_movies=user_favorites)
    else:
        return redirect(url_for('login1'))
    
if __name__ == '__main__':
    app.run(debug=True)
