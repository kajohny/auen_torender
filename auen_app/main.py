from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_, desc, cast
from .models import User, Music, Favourites, Albums, Genres, Playlists, PlaylistMusic, Followers, WaitingAudios,\
                    WaitingReleases, ListeningHistory, Subscriptions, Collaborations
from . import db
import os
import re
from datetime import datetime, timezone, date
from PIL import Image

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
        db.session.query(Favourites.id)\
            .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
        .order_by(desc(Music.streams)).limit(15).all()  

    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Music.streams, User.id.label('artist_id'))\
            .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).limit(15).all()
        
    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id')).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum==True).all()

    genres = Genres.query.all()
    
    artists = User.query.filter_by(isartist=True).all()

    new_musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'))\
                    .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
                    .order_by(desc(Music.time_added)).limit(30).all()
    
    return render_template('index.html', musics=musics, new_musics=new_musics, albums=albums, genres=genres, artists=artists)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        title = request.form.get('search')
        search = "%{}%".format(title)

        if current_user.is_authenticated:
            playlists = Playlists.query.filter_by(user_id=current_user.id).all()
            audios = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img,
                                Music.streams, db.session.query(Favourites.id)\
                .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
                .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
                .filter(Music.music_title.ilike(search)).limit(5).all()  

        else:
            audios = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img,
                                Music.streams)\
                .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
                .filter(Music.music_title.ilike(search)).limit(5).all()  
            
        authors = db.session.query(User.id, User.name, User.image).filter(User.isartist,User.name.ilike(search)).all()

        albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id'))\
                                    .join(User, Albums.author_id == User.id)\
                                    .filter(Albums.album_title.ilike(search)).all()
        
        print(len(albums))

        return render_template("search.html", audios=audios, authors=authors, albums=albums, playlists=playlists)


@main.route('/album.html')
def album():
    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum == True).all()
    
    return render_template('album.html', albums=albums)

@main.route('/artist')
def artist():
    authors = User.query.filter_by(isartist=True).all()
    
    return render_template('artist.html', authors=authors)

@main.route('/genre')
def genre():
    genres = Genres.query.all()
    
    return render_template('genres.html', genres=genres)

@main.route('/top_track')
def top_track():
    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
        db.session.query(Favourites.id)\
            .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
        .order_by(func.random()).limit(15).all()

    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).limit(15).all()
    
    return render_template('top_track.html', musics=musics)

@main.route('/artist/<artist_id>', methods=["GET"])
def artist_single(artist_id):
    author_single = User.query.filter_by(id=artist_id).first()

    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
        db.session.query(Favourites.id)\
        .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
        .filter(User.id == artist_id).order_by(func.random()).all()
    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'))\
            .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
            .filter(User.id == artist_id).all()

    authors_similar = User.query.filter_by(genre_id=author_single.genre_id).filter(User.id != artist_id).all()
    albums = Albums.query.filter_by(author_id = artist_id, isalbum=True).all()

    return render_template('artist_single.html', author_single=author_single, musics=musics, authors_similar=authors_similar, albums=albums)

@main.route('/album/album_single/<album_id>', methods=["GET"])
def album_single(album_id):
    album_single = Albums.query.filter_by(id=album_id).first()
    artist_single = db.session.query(User.name).join(Albums, Albums.author_id == User.id).filter(Albums.id == album_id).first()

    if current_user.is_authenticated:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
        db.session.query(Favourites.id)\
        .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
        .filter(and_(Music.id != None, Albums.id == album_id)).order_by(func.random()).all()
    else:
        musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img)\
            .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Albums.id == album_id).all()

    counter = 0

    for music in musics:
        counter += 1

    return render_template('album_single.html', album_single=album_single, artist_single=artist_single, musics=musics, counter=counter)

@main.route('/genres/genres_single/<genre_id>')
def genres_single(genre_id):
    genre = Genres.query.filter_by(id=genre_id).first()

    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'))\
        .join(User, User.id == Music.author_id)\
        .join(Albums, Albums.id == Music.album_id)\
        .join(Genres, Genres.id == Music.genre_id).filter(Genres.id == genre_id).order_by(func.random()).all()
    
    return render_template('genres_single.html', genre=genre, musics=musics)

@main.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(id = current_user.id).first()
    is_subscribed = Subscriptions.query.filter_by(user_id = current_user.id).first()

    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id')).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum == True, Albums.author_id == current_user.id).all()    
    singles = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id')).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum == False, Albums.author_id == current_user.id).all() 
      
    playlists = Playlists.query.filter_by(user_id = current_user.id).all()

    audios = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Music.streams, User.id.label('artist_id'),
                                db.session.query(Favourites.id)\
                .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
                .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).filter(User.id == current_user.id).all()  
    
    return render_template('profile.html', user=user, is_subscribed=is_subscribed, albums=albums, singles=singles, audios=audios, playlists=playlists)

@main.route('/profile/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        user = User.query.filter_by(email = current_user.email).first()

        if password == password_confirm:
            if check_password_hash(user.password, password):
                user.email = email
                user.name = name
                db.session.commit()

                return redirect(url_for('main.profile'))
            else:
                flash('Your password is incorrect')
        else:
            flash('Passwords do not match')
    
    return render_template('profile_edit.html', name=current_user.name, email=current_user.email)

@main.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == "POST":
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')

        user = User.query.filter_by(email=current_user.email).first()

        if check_password_hash(user.password, password):
            if new_password == new_password2:
                user.password = generate_password_hash(new_password, method='sha256')
                
                db.session.commit()

                return redirect(url_for('main.profile'))

            else:
                flash('Passwords do not match')
        else:
            flash('Your current pwd is incorrect')
    return render_template('profile_pwd_change.html')

@main.route("/profile/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    playlists = Playlists.query.filter_by(user_id=current_user.id).all()

    audios = db.session.query\
        (Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Albums.album_title, Music.streams)\
        .join(User, Music.author_id == User.id)\
        .join(Albums, Albums.id == Music.album_id)\
        .join(Favourites, Favourites.music_id == Music.id).filter(Favourites.user_id == current_user.id).all()
    
    if request.method == "POST":
        music_id = request.form.get('music_id')
        favourite = Favourites.query.filter_by(music_id=music_id, user_id=current_user.id).first()

        db.session.delete(favourite)
        db.session.commit()

        return redirect(url_for('main.favourites'))
    return render_template('favourite.html', audios=audios, playlists=playlists)

@main.route("/favourites/add", methods=["POST"])
@login_required
def add_favourites():
    music_id = request.form.get('music_id')

    favourite = Favourites(user_id=current_user.id, music_id=music_id)
        
    db.session.add(favourite)
    db.session.commit()

    return "added"

@main.route("/favourites/remove", methods=["POST"])
@login_required
def remove_favourites():
    music_id = request.form.get('music_id')
    favourite = Favourites.query.filter_by(music_id=music_id, user_id=current_user.id).first()

    db.session.delete(favourite)
    db.session.commit()

    return "removed"

@main.route('/profile/playlist_user')
@login_required
def playlist_user():
    favourites = Favourites.query.filter_by(user_id=current_user.id).all()

    playlists = db.session.query(Playlists.playlist_name, Playlists.id, PlaylistMusic.playlist_id, func.count(PlaylistMusic.playlist_id).label('counter'))\
        .join(PlaylistMusic, PlaylistMusic.playlist_id == Playlists.id, full=True)\
        .filter(Playlists.user_id == current_user.id).group_by(Playlists.id, PlaylistMusic.playlist_id, Playlists.playlist_name)
    counter_f = 0

    for favourite in favourites:
        counter_f += 1
    
    return render_template('add_playlist.html', playlists=playlists, counter_f=counter_f)

@main.route('/profile/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == "POST":
        playlist_name = request.form.get('playlist_name')

        new_playlist = Playlists(user_id=current_user.id, playlist_name=playlist_name)

        db.session.add(new_playlist)
        db.session.commit()

        return redirect(url_for('main.playlist_user'))
    return render_template('create_playlist.html')

@main.route('/profile/playlist_user/<playlist_id>', methods=["GET", "POST"])
@login_required
def playlist_music(playlist_id):
    playlist_single = Playlists.query.filter_by(id = playlist_id).first()

    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, 
                              User.id.label('artist_id'), db.session.query(Favourites.id)\
                    .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(User, User.id == Music.author_id)\
        .join(Albums, Albums.id == Music.album_id).join(PlaylistMusic, PlaylistMusic.music_id == Music.id)\
        .filter(PlaylistMusic.playlist_id == playlist_id).all()

    musics_playlist = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
        db.session.query(PlaylistMusic.id)\
            .filter(and_(Music.id == PlaylistMusic.music_id, PlaylistMusic.playlist_id == playlist_id)).limit(1).label('is_playlist'))\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
        .limit(15).all()
    
    return render_template('playlist_music.html', playlist_single=playlist_single, musics=musics, musics_playlist=musics_playlist)

@main.route("/playlist/add", methods=["POST"])
@login_required
def add_playlist():
    music_id = request.form.get('music_id')
    playlist_id = request.form.get('playlist_id')

    print(music_id, playlist_id)

    playlist = PlaylistMusic(playlist_id=playlist_id, music_id=music_id)
        
    db.session.add(playlist)
    db.session.commit()

    return "added"

@main.route("/playlist/remove", methods=["POST"])
@login_required
def remove_playlist():
    music_id = request.form.get('music_id')
    playlist_id = request.form.get('playlist_id')
    playlist = PlaylistMusic.query.filter_by(music_id=music_id, playlist_id=playlist_id).first()

    db.session.delete(playlist)
    db.session.commit()

    return "removed"

AUDIO_EXTENSIONS = {'mp3', 'wav'}
def audio_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in AUDIO_EXTENSIONS

@main.route('/profile/upload', methods=["GET", "POST"])
@login_required
def upload():
    is_subscribed = Subscriptions.query.filter_by(user_id = current_user.id).first()

    if is_subscribed is None:
        music = db.session.query(Music.music_title, func.to_char(Music.time_added, 'DD-MM-YYYY').label('time_added'))\
            .filter(Music.author_id == current_user.id).order_by(desc('time_added')).limit(5).all()
    
        counter = 0
    
        for mus in music:
            if date.today() == (datetime.strptime(mus.time_added, '%d-%m-%Y')).date():
                counter += 1
        if counter == 5:
            flash("You have reached your upload limit today. Buy a subscription for AUEN+ to remove the limit.")
        if request.method == "POST":
            file = request.files['file']
            title = request.form.get('title')
            artist_name = request.form.get('artist_name')
            img_file = request.files['img-file']

            if img_file.filename:
                img_file.save(os.path.join("auen_app/static/images/albums", img_file.filename))
                waiting_release = WaitingReleases(album_title = title, album_img = 'images/albums/' + img_file.filename, author_id=current_user.id, isalbum=False)
            else:
                waiting_release = WaitingReleases(album_title = title, album_img = 'images/albums/images.jfif', author_id=current_user.id, isalbum=False)
            db.session.add(waiting_release)
            db.session.commit()

            waiting_release = WaitingReleases.query.filter_by(album_title=title).first()

            fixedFilename = re.sub('[^A-Za-z0-9.]+', '', file.filename)
            file.save(os.path.join("auen_app/static/music", fixedFilename))
            if artist_name == "":
                add_audio = WaitingAudios(title = title, source="/static/music/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id)
            else:
                add_audio = WaitingAudios(title = title, source="/static/music/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id, featured_artist = artist_name)
            db.session.add(add_audio)
            db.session.commit()
            return redirect(url_for('main.waiting_list'))
        return render_template('upload.html', counter=counter)
    else:
        if request.method == "POST":
            files = request.files.getlist('file')
            titles = request.form.getlist('title')
            artist_name = request.form.getlist('artist_name')
            isalbum = False
        
            if(len(files) > 1):
                album_title = request.form.get('album_title')
                isalbum = True
            else:
                album_title = request.form.get('title')

            img_file = request.files['img-file']

            if img_file.filename:
                img_file.save(os.path.join("auen_app/static/images/albums", img_file.filename))
                waiting_release = WaitingReleases(album_title = album_title, album_img = 'images/albums/' + img_file.filename, author_id=current_user.id, isalbum=isalbum)
            else:
                waiting_release = WaitingReleases(album_title = album_title, album_img = 'images/albums/images.jfif', author_id=current_user.id, isalbum=isalbum)
            db.session.add(waiting_release)
            db.session.commit()

            waiting_release = WaitingReleases.query.filter_by(album_title=album_title).first()

            for i in range(len(files)):
                fixedFilename = re.sub('[^A-Za-z0-9.]+', '', files[i].filename)
                files[i].save(os.path.join("auen_app/static/music", fixedFilename))
                if artist_name[i] == "":
                    add_audio = WaitingAudios(title = titles[i], source="/static/music/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id)
                else:
                    add_audio = WaitingAudios(title = titles[i], source="/static/music/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id, featured_artist = artist_name[i])
                db.session.add(add_audio)
                db.session.commit()

            return redirect(url_for('main.waiting_list'))
        return render_template('upload_multiple.html')


@main.route('/approval_list', methods=['GET', 'POST'])
@login_required
def waiting_list():
    musics = db.session.query(WaitingAudios.id, WaitingAudios.title, WaitingAudios.source, User.name, 
                              WaitingReleases.album_img, WaitingReleases.album_title, WaitingAudios.featured_artist)\
                        .join(User, WaitingAudios.artist_id == User.id)\
                        .join(WaitingReleases, and_(WaitingReleases.id == WaitingAudios.album_id, WaitingReleases.author_id == User.id))\
                        .filter(WaitingAudios.artist_id == current_user.id)\
                        .group_by(WaitingAudios.id, User.name, WaitingAudios.title, WaitingAudios.source, WaitingReleases.album_title, 
                      WaitingReleases.album_img).all()

    return render_template("waiting_list.html", musics=musics)

@main.route('/upload_audio', methods=["POST"])
@login_required
def upload_audio():
    musics = db.session.query(WaitingAudios.id, WaitingAudios.title, WaitingAudios.source, User.name, 
                              WaitingReleases.album_img, WaitingReleases.album_title, WaitingReleases.isalbum, WaitingAudios.featured_artist)\
                        .join(User, WaitingAudios.artist_id == User.id)\
                        .join(WaitingReleases, and_(WaitingReleases.id == WaitingAudios.album_id, WaitingReleases.author_id == User.id))\
                        .filter(WaitingAudios.artist_id == current_user.id)\
                        .group_by(WaitingAudios.id, User.name, WaitingAudios.title, WaitingAudios.source, WaitingReleases.album_title, 
                      WaitingReleases.album_img, WaitingReleases.isalbum).all()
    
    waiting_releases = db.session.query(WaitingReleases.id, WaitingReleases.album_title, WaitingReleases.album_img, WaitingReleases.author_id, WaitingReleases.isalbum).\
                        filter(WaitingReleases.author_id == current_user.id).first()
    
    add_release = Albums(id=waiting_releases.id + 5, album_title=waiting_releases.album_title, album_img=waiting_releases.album_img, author_id=current_user.id, isalbum=waiting_releases.isalbum)
    db.session.add(add_release)
    db.session.commit()

    release = Albums.query.filter_by(album_title=waiting_releases.album_title).first()

    for music in musics:
        add_audio = Music(id = music.id + 15, music_title=music.title, music_source=music.source, author_id=current_user.id, album_id=release.id, 
                           featured_artist=music.featured_artist)
        db.session.add(add_audio)
        db.session.commit()

    to_delete_audios = WaitingAudios.query.filter_by(artist_id=current_user.id).all()
    to_delete_releases = WaitingReleases.query.filter_by(author_id=current_user.id).all()

    for i in range(len(to_delete_audios)):
        to_delete_audio = WaitingAudios.query.filter_by(artist_id=current_user.id).first()
        db.session.delete(to_delete_audio)
        db.session.commit()
    for i in range(len(to_delete_releases)):
        to_delete_release = WaitingReleases.query.filter_by(author_id=current_user.id).first()
        db.session.delete(to_delete_release)
        db.session.commit()

    return redirect(url_for('main.your_tracks'))

@main.route('/artists/<artist_id>', methods=["GET"])
def single_artist(artist_id):
    author_single = User.query.filter_by(id=artist_id).first()

    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id')).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum == True, Albums.author_id == artist_id).all()  
      
    singles = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name, User.id.label('artist_id')).join(User, Albums.author_id == User.id)\
                        .filter(Albums.isalbum == False, Albums.author_id == artist_id).all()    
    
    follower_all = Followers.query.filter_by(followed_id=artist_id).all()

    counter_followers = 0

    for i in follower_all:
        counter_followers += 1

    if current_user.is_authenticated:
        playlists = Playlists.query.filter_by(user_id=current_user.id).all()

        audios = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, User.id.label('artist_id'),
                                Music.streams, db.session.query(Favourites.id)\
                .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
                .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).filter(User.id == artist_id).all()   
        
        is_followed = Followers.query.filter_by(follower_id=current_user.id, followed_id=artist_id).first()
        is_collaborated = Collaborations.query.filter_by(first_artist=current_user.id, second_artist=artist_id).first()
        
        if is_collaborated is None:
            is_collaborated = Collaborations.query.filter_by(first_artist=artist_id, second_artist=current_user.id).first()

        return render_template('artist_page.html', author_single=author_single, audios=audios, 
                           counter_followers=counter_followers, is_followed=is_followed, albums=albums, singles=singles, 
                           is_collaborated=is_collaborated, playlists=playlists)
    else:
        audios = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Music.streams,
                                  User.id.label('artist_id'))\
                            .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).filter(User.id == artist_id).all()
        
        return render_template('artist_page.html', author_single=author_single, audios=audios, 
                            counter_followers=counter_followers, albums=albums, singles=singles)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/edit_pfp', methods=["GET", "POST"])
@login_required
def edit_pfp():
    if request.method == "POST":
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            file.save(os.path.join("auen_app/static/images/pfp", file.filename))
            image = Image.open('auen_app/static/images/pfp/' + file.filename)
            new_image = image.resize((360, 360))
            new_image.save(os.path.join("auen_app/static/images/pfp", file.filename))
            user = User.query.filter_by(id = current_user.id).first()
            user.image = "/images/pfp/" + file.filename
            db.session.commit()
            return render_template("profile.html", user=user)
        else:
            return redirect(url_for('main.profile'))
        
@main.route('/your_tracks', methods=["GET"])
@login_required
def your_tracks():
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, 
                              Albums.album_img, Albums.album_title, Music.featured_artist)\
                        .join(User, Music.author_id == User.id)\
                        .join(Albums, and_(Albums.id == Music.album_id, Albums.author_id == User.id))\
                        .filter(or_(Music.author_id == current_user.id, Music.featured_artist == current_user.name))\
                        .group_by(Music.id, User.name, Music.music_title, Music.music_source, Albums.album_title, 
                      Albums.album_img).order_by(User.name).all()
    
    return render_template('your_tracks.html', musics=musics)
        
@main.route('/following/follow', methods=["POST"])
@login_required
def follow():
    followed_id = request.form.get('followed_id')

    follower = Followers(follower_id=current_user.id, followed_id=followed_id)
    db.session.add(follower)
    db.session.commit()

    return "followed"


@main.route('/following/unfollow', methods=["POST"])
@login_required
def unfollow():
    followed_id = request.form.get('followed_id')

    follower = Followers.query.filter_by(follower_id=current_user.id, followed_id=followed_id).first()
    db.session.delete(follower)
    db.session.commit()

    return "unfollowed"

@main.route('/feed', methods=["GET"])
@login_required
def feed():
    collaborations = db.session.query(Collaborations.first_artist, User.id, User.name).join(User, User.id == Collaborations.first_artist)\
                    .filter(Collaborations.second_artist == current_user.id, Collaborations.isapproved == False).all()
    
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Albums.album_title, User.id.label('artist_id'),
                              func.to_char(Music.time_added, 'DD-MM-YYYY HH24:MI:SS').label('time_added'))\
            .join(User, Music.author_id == User.id).join(Albums, and_(Albums.id == Music.album_id, Albums.author_id == User.id))\
            .join(Followers, Followers.followed_id == User.id).filter(Followers.follower_id == current_user.id)\
            .group_by(Music.id, User.name, Music.music_title, Music.music_source, Music.time_added, Albums.album_title, 
                      Albums.album_img, User.id).order_by(desc('time_added')).all()

    return render_template("feed.html", musics=musics, collaborations=collaborations)

@main.route('/stream', methods=["POST"])
def stream():
    music_title = request.form.get("music_title")
    db.session.query(Music).filter(Music.music_title == music_title).update({'streams': Music.streams + 1})
    db.session.commit()

    return '+1 stream'

@main.route('/add_history', methods=["POST"])
def add_history():
    music_id = request.form.get('music_id') 
    is_exists = db.session.query(ListeningHistory).filter_by(user_id=current_user.id, music_id=music_id).first()
    print(is_exists)
    if is_exists:
        db.session.delete(is_exists)
        db.session.commit()

    music = ListeningHistory(user_id=current_user.id, music_id=music_id)
        
    db.session.add(music)
    db.session.commit()

    return "added"

@main.route('/listening_history', methods=["GET"])
@login_required
def listening_history():
    musics = db.session.query\
        (Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img,  
         Albums.album_title, User.id.label('artist_id'),
             func.to_char(ListeningHistory.time_added, 'DD-MM-YYYY HH24:MI:SS').label('time_added'), db.session.query(Favourites.id)\
                    .filter(and_(Music.id == Favourites.music_id, Favourites.user_id == current_user.id)).limit(1).label('is_favourite'))\
        .join(Albums, Albums.id == Music.album_id)\
        .join(ListeningHistory, and_(ListeningHistory.music_id == Music.id, ListeningHistory.user_id == current_user.id))\
        .join(User, User.id == Music.author_id)\
        .group_by(Music.id, Music.music_title, Albums.album_title, Music.music_source, ListeningHistory.time_added, Albums.album_img,
                  User.name, User.id)\
        .order_by(desc('time_added')).all()
    return render_template('listening_history.html', musics=musics)

@main.route('/collaboration/collaborate', methods=["POST"])
@login_required
def collaborate():
    second_artist = request.form.get('second_artist')

    collaboration = Collaborations(first_artist=current_user.id, second_artist=second_artist)
    db.session.add(collaboration)
    db.session.commit()

    return "collabed"

@main.route('/collaboration/cancel', methods=["POST"])
@login_required
def uncollaborate():
    second_artist = request.form.get('second_artist')

    collaboration = Collaborations.query.filter_by(first_artist=current_user.id, second_artist=second_artist).first()
    if collaboration is None:
        collaboration = Collaborations.query.filter_by(first_artist=second_artist, second_artist=current_user.id).first()
    db.session.delete(collaboration)
    db.session.commit()

    return "canceled collab"

@main.route('/collaboration/accept', methods=["POST"])
@login_required
def collaboration_accept():
    first_artist = request.form.get('first_artist')

    collaboration = Collaborations.query.filter_by(first_artist=first_artist, second_artist=current_user.id).first()
    collaboration.isapproved = True
    db.session.commit()

    return redirect(url_for('main.feed'))

@main.route('/collaboration/deny', methods=["POST"])
@login_required
def collaboration_deny():
    first_artist = request.form.get('first_artist')

    collaboration = Collaborations.query.filter_by(first_artist=first_artist, second_artist=current_user.id).first()
    db.session.delete(collaboration)
    db.session.commit()

    return redirect(url_for('main.feed'))