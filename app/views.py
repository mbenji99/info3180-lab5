"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from flask import request
from .forms import MovieForm
from .models import db, Movie
from . import app
from . import form_errors
import os

###
# Routing for your application.
###

@app.route('/api/v1/movies', methods=['POST'])
def movies():
    form = MovieForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        poster = form.poster.data

        uploads_folder = 'uploads'
        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)

        # Save the movie to the database
        movie = Movie(title=title, description=description, poster=poster.filename)
        db.session.add(movie)
        db.session.commit()

        # Save the file to the uploads folder
        poster.save(os.path.join(uploads_folder, poster.filename))

        # Return success message and movie details
        response = {
            "message": "Movie Successfully added",
            "title": title,
            "poster": poster.filename,
            "description": description
        }
        return jsonify(response), 201
    else:
        # Return validation errors
        errors = form_errors(form)
        return jsonify({"errors": errors}), 400


@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")


###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404