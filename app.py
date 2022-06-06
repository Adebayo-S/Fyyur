from config import *
from models import *

# ---------------------------------------------------------------------------#
# Filters.
# ---------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'mediu-m':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# --------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    cities = db.session.query(Venue.city, Venue.state).distinct()

    for city in cities:
        venues = db.session.query(Venue).filter_by(
            city=city.city, state=city.state).all()

        for venue in venues:
            data.append({
                "city": city.city,
                "state": city.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": db.session.query(Show).filter_by(
                        venue_id=venue.id).count()
                }]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venue_found = db.session.query(Venue).filter(
        Venue.name.ilike('%' + request.form.get('search_term') + '%')).all()

    response = {
        "count": len(venue_found),
        "data": venue_found
    }

    return render_template(
        'pages/search_venues.html', results=response, search_term=request.form.get(
            'search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    data = venue.__dict__

    shows = db.session.query(Show).join(
        Artist, Venue).filter_by(id = venue_id)
    # print(shows)
    # for show in shows:
    #     print(show.start_time)
    #     print(show.venue_id)
    past_shows = shows.filter(Show.start_time < datetime.now()).all()
    upcoming_shows = shows.filter(Show.start_time >= datetime.now()).all()
    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    for show in upcoming_shows:
        show.start_time = show.start_time.strftime('%d-%m-%Y %H:%M')

    for show in past_shows:
        print(show.artist)
        print(show.venue)
        show.start_time = show.start_time.strftime('%d-%m-%Y %H:%M')

    data["past_shows"] = past_shows
    data["past_shows_count"] = past_shows_count
    data["upcoming_shows"] = upcoming_shows
    data["upcoming_shows_count"] = upcoming_shows_count

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    venue = Venue.query.get(venue_id)

    if venue is None:
        return abort(400)

    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted successfully!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('Error occurred: Venue could not be deleted.')
    finally:
        db.session.close()

    if (error):
        abort(500)
    else:
        return jsonify({
            'message': 'Delete Successful'
        })

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    artist_found = db.session.query(Artist).filter(
        Artist.name.ilike('%' + request.form.get('search_term') + '%')).all()

    response = {
        "count": len(artist_found),
        "data": artist_found
    }

    return render_template(
        'pages/search_artists.html', results=response, search_term=request.form.get(
            'search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    data = artist.__dict__

    shows = db.session.query(Show).join(
        Venue, Artist).filter_by(id = artist_id)
    past_shows = shows.filter(Show.start_time < datetime.now()).all()
    upcoming_shows = shows.filter(Show.start_time >= datetime.now()).all()
    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    for show in upcoming_shows:
        show.start_time = show.start_time.strftime('%d-%m-%Y %H:%M')

    for show in past_shows:
        show.start_time = show.start_time.strftime('%d-%m-%Y %H:%M')

    data["past_shows"] = past_shows
    data["past_shows_count"] = past_shows_count
    data["upcoming_shows"] = upcoming_shows
    data["upcoming_shows_count"] = upcoming_shows_count

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = db.session.query(Artist).filter_by(id=artist_id).first()
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = db.session.query(Artist).filter_by(id=artist_id).first()

    try:
        form.populate_obj(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.query(Venue).filter_by(id=venue_id).first()
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = db.session.query(Venue).filter_by(id=venue_id).first()

    try:
        form.populate_obj(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm(request.form)
        artists = Artist()
        form.populate_obj(artists)
        db.session.add(artists)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('Failed to create artist ' + request.form['name'])
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = db.session.query(Show).join(Artist).join(Venue).all()

    for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = ShowForm(request.form)
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('Failed to create show')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
