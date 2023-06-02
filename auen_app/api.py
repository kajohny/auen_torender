from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, json, Response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, and_, or_, desc
from .models import User, Music, Albums, Favourites, Playlists, PlaylistMusic, Followers, WaitingAudios, WaitingReleases, Collaborations,\
    musics_schema, user_schema, playlist_schema, albums_schema, followers_schema, artists_schema, audio_schema, collaboration_schema
from . import db
import os
import re

api = Blueprint('api', __name__)

@api.route('/login/api', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify(["error"])
        return jsonify(["success"])

    return jsonify(['hello'])

@api.route('/registration/api', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        isartist = request.form['isartist']
        image = "/images/pfp/pfp_standard.jpg"

        if isartist == "artist":
            isartist = True
        else:
            isartist = False

        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify(['Email already exists'])
        else:
            if password != password_confirm:
                return jsonify(['Passwords do not match'])
            else:
                reg_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), image=image, isartist=isartist)
                db.session.add(reg_user)
                db.session.commit()
                return jsonify(['success'])
    return jsonify(['registration'])

@api.route('/profile/api/<email>', methods=["GET"])
def profile(email):
    user = User.query.filter_by(email = email).first()
    return user_schema.jsonify(user)

@api.route('/music_available/api/', methods=["GET"])
def music_available():
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img)\
        .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id).all()

    return musics_schema.jsonify(musics)

@api.route('/favourites/api/<id>', methods=["GET"])
def favourites(id):
    musics = db.session.query\
        (Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img)\
        .join(Albums, Albums.id == Music.album_id).join(User, Music.author_id == User.id)\
        .join(Favourites, and_(Favourites.music_id == Music.id, Favourites.user_id == id)).all()

    return musics_schema.jsonify(musics)

@api.route('/favouritesAdd/api/<id>', methods=["POST"])
def add_favourites(id):
    if request.method == "POST":
        music_id = request.form['music_id']

        favourite = Favourites(user_id=id, music_id=music_id)

        db.session.add(favourite)
        db.session.commit()

        return jsonify(['success'])
    
    return jsonify(['add to fav'])

@api.route('/favouritesRemove/api/<id>', methods=["POST"])
def remove_favourites(id):
    if request.method == "POST":
        music_id = request.form['music_id']

        favourite = Favourites.query.filter_by(user_id=id, music_id=music_id).first()   

        db.session.delete(favourite)
        db.session.commit()

        return jsonify(['success'])
    
    return jsonify(['remove fav'])

@api.route('/playlist_user/api/<id>', methods=["GET"])
def playlist_user(id):
    playlists = Playlists.query.filter_by(user_id = id).all()
    
    return playlist_schema.jsonify(playlists)

@api.route('/playlist_songs/api/<playlist_id>', methods=["GET"])
def playlist_songs(playlist_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img)\
        .join(User, Music.author_id == User.id)\
        .join(Albums, Albums.id == Music.album_id).join(PlaylistMusic, PlaylistMusic.music_id == Music.id)\
        .filter(PlaylistMusic.playlist_id == playlist_id)
    
    return musics_schema.jsonify(musics)

@api.route('/create_playlist/api/<id>', methods=["POST"])
def create_playlist(id):
    if request.method == "POST":
        playlist_name = request.form['playlist_name']

        new_playlist = Playlists(user_id=id, playlist_name=playlist_name)

        db.session.add(new_playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['create playlist'])

@api.route('/playlist_add/api/', methods=["POST"])
def playlist_add():
    if request.method == "POST":
        music_id = request.form['music_id']
        playlist_id = request.form['playlist_id']

        playlist = PlaylistMusic(playlist_id=playlist_id, music_id=music_id)
        
        db.session.add(playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['add to playlist'])

@api.route('/playlist_remove/api/', methods=["POST"])
def playlist_remove():
    if request.method == "POST":
        music_id = request.form['music_id']
        playlist_id = request.form['playlist_id']

        playlist = PlaylistMusic.query.filter_by(music_id=music_id, playlist_id=playlist_id).first()
        
        db.session.delete(playlist)
        db.session.commit()

        return jsonify(['success'])
    return jsonify(['remove from playlist'])

@api.route('/albums/api', methods=["GET"])
def albums():
    albums = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name).join(User, Albums.author_id == User.id).all()

    return albums_schema.jsonify(albums)

@api.route('/album_songs/api/<album_id>', methods=["GET"])
def album_songs(album_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img)\
            .join(User, Music.author_id == User.id).join(Albums, Albums.id == Music.album_id)\
            .filter(Albums.id == album_id).all()

    return musics_schema.jsonify(musics)

# @api.route('/upload/api/<artist_id>', methods=["POST"])
# def upload(artist_id):
#     if request.method == "POST":
#         files = request.files.getlist('file')
#         titles = request.form.getlist('title')
        
#         if(len(files) > 1):
#             album_title = request.form.get('album_title')
#         else:
#             album_title = request.form.get('title')

#         img_file = request.files['img-file']

#         if img_file.filename:
#             img_file.save(os.path.join("auen_app/static/images/album", img_file.filename))
#             release = Releases(album_title = album_title, album_img = 'images/album/' + img_file.filename, author_id=artist_id)
#         else:
#             release = Releases(album_title = album_title, album_img = 'images/album/images.jfif', author_id=artist_id)
#         db.session.add(release)
#         db.session.commit()

#         release = Releases.query.filter_by(album_title=album_title).first()
        
#         for i in range(len(files)):
#             fixedFilename = re.sub('[^A-Za-z0-9.]+', '', files[i].filename)
#             files[i].save(os.path.join("auen_app/static/audio", fixedFilename))
#             add_audio = Audios(title = titles[i], source="/static/audio/" + fixedFilename, album_id = release.id, artist_id = artist_id)
#             db.session.add(add_audio)
#             db.session.commit()

#         return jsonify(['success'])
#     return jsonify(['upload'])

@api.route('/upload/api/<artist_id>', methods=["POST"])
def upload(artist_id):
    files = request.files.getlist('file')
    titles = request.form.getlist('title')
    artist_name = request.form.getlist('artist_name')
        
    if(len(files) > 1):
        album_title = request.form.get('album_title')
    else:
        album_title = request.form.get('title')

        img_file = request.files['img-file']

    if img_file.filename:
        img_file.save(os.path.join("auen_app/static/images/albums", img_file.filename))
        waiting_release = WaitingReleases(album_title = album_title, album_img = 'images/albums/' + img_file.filename, author_id=artist_id)
    else:
        waiting_release = WaitingReleases(album_title = album_title, album_img = 'images/albums/images.jfif', author_id=artist_id)
    db.session.add(waiting_release)
    db.session.commit()

    waiting_release = WaitingReleases.query.filter_by(album_title=album_title).first()

    for i in range(len(files)):
        fixedFilename = re.sub('[^A-Za-z0-9.]+', '', files[i].filename)
        files[i].save(os.path.join("auen_app/static/audio", fixedFilename))
        if artist_name[i] == "":
            add_audio = WaitingAudios(title = titles[i], source="/static/audio/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id)
        else:
            add_audio = WaitingAudios(title = titles[i], source="/static/audio/" + fixedFilename, album_id = waiting_release.id, 
                                      artist_id = current_user.id, featured_artist = artist_name[i])
        db.session.add(add_audio)
        db.session.commit()

    return jsonify(['success'])
@api.route('/approval_list/<artist_id>', methods=["GET"])
def approval_list(artist_id):
    musics = db.session.query(WaitingAudios.id, WaitingAudios.title.label('music_title'), WaitingAudios.source.label('music_source'), 
                              User.name.label('author_name'), WaitingReleases.album_img, WaitingReleases.album_title, WaitingAudios.featured_artist)\
                        .join(User, WaitingAudios.artist_id == User.id)\
                        .join(WaitingReleases, and_(WaitingReleases.id == WaitingAudios.album_id, WaitingReleases.author_id == User.id))\
                        .filter(WaitingAudios.artist_id == artist_id)\
                        .group_by(WaitingAudios.id, User.name, WaitingAudios.title, WaitingAudios.source, WaitingReleases.album_title, 
                      WaitingReleases.album_img).all()
    
    return musics_schema.jsonify(musics)

@api.route('/upload_audio/<artist_id>', methods=["POST"])
@login_required
def upload_audio(artist_id):
    musics = db.session.query(WaitingAudios.id, WaitingAudios.title, WaitingAudios.source, User.name, 
                              WaitingReleases.album_img, WaitingReleases.album_title, WaitingAudios.featured_artist)\
                        .join(User, WaitingAudios.artist_id == User.id)\
                        .join(WaitingReleases, and_(WaitingReleases.id == WaitingAudios.album_id, WaitingReleases.author_id == User.id))\
                        .filter(WaitingAudios.artist_id == artist_id)\
                        .group_by(WaitingAudios.id, User.name, WaitingAudios.title, WaitingAudios.source, WaitingReleases.album_title, 
                      WaitingReleases.album_img).all()
    
    waiting_releases = db.session.query(WaitingReleases.album_title, WaitingReleases.album_img, WaitingReleases.author_id).\
                        filter(WaitingReleases.author_id == artist_id).first()
    
    add_release = Albums(album_title=waiting_releases.album_title, album_img=waiting_releases.album_img, author_id=artist_id)
    db.session.add(add_release)
    db.session.commit()

    release = Albums.query.filter_by(album_title=waiting_releases.album_title).first()

    for music in musics:
        add_audio = Music(music_title=music.title, music_source=music.source, artist_id=artist_id, album_id=release.id, 
                           featured_artist=music.featured_artist)
        db.session.add(add_audio)
        db.session.commit()

    to_delete_audios = WaitingAudios.query.filter_by(artist_id=artist_id).all()
    to_delete_releases = WaitingReleases.query.filter_by(author_id=artist_id).all()

    for i in range(len(to_delete_audios)):
        to_delete_audio = WaitingAudios.query.filter_by(artist_id=artist_id).first()
        db.session.delete(to_delete_audio)
        db.session.commit()
    for i in range(len(to_delete_releases)):
        to_delete_release = WaitingReleases.query.filter_by(author_id=artist_id).first()
        db.session.delete(to_delete_release)
        db.session.commit()

    return "uploaded to auen"

@api.route('/following/follow/api/<user_id>', methods=["POST"])
def follow(user_id):
    if request.method == "POST":
        followed_id = request.form.get('followed_id')

        follower = Followers(follower_id=user_id, followed_id=followed_id)
        db.session.add(follower)
        db.session.commit()

        return jsonify(['followed'])
    return jsonify(['follow'])

@api.route('/following/unfollow/api/<user_id>', methods=["POST"])
def unfollow(user_id):
    if request.method == "POST":
        followed_id = request.form.get('followed_id')

        follower = Followers.query.filter_by(follower_id=user_id, followed_id=followed_id).first()
        db.session.delete(follower)
        db.session.commit()

        return jsonify(['unfollowed'])
    return jsonify(['unfollow'])

@api.route('/followers/api/<artist_id>', methods=["GET"])
def followers(artist_id):
    followers = db.session.query(User.id, User.name).join(Followers, Followers.follower_id == User.id).filter(Followers.followed_id == artist_id).all()

    return followers_schema.jsonify(followers)

@api.route('/followed/api/<user_id>', methods=["GET"])
def followed(user_id):
    followed = db.session.query(User.id, User.name).join(Followers, Followers.followed_id == User.id).filter(Followers.follower_id == user_id).all()

    return followers_schema.jsonify(followed)

@api.route('/show_albums/api/<artist_id>', methods=["GET"])
def show_albums(artist_id):
    releases = db.session.query(Albums.id, Albums.album_title, Albums.album_img, User.name.label('author_name'))\
        .join(User, User.id == Albums.author_id).filter(Albums.author_id == artist_id).all()

    return albums_schema.jsonify(releases)

@api.route('/show_songs/api/<album_id>', methods=["GET"])
def show_songs(album_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name.label('author_name'), 
                              Albums.album_img)\
        .join(User, Music.author_id == User.id)\
        .join(Albums, Albums.id == Music.album_id)\
        .filter(Albums.id == album_id)
    
    return musics_schema.jsonify(musics)

@api.route('/show_artists/api/', methods=["GET"])
def show_artists():
    artists = db.session.query(User.id, User.name, User.image).filter(User.isartist == True)
    
    return artists_schema.jsonify(artists)

@api.route('/search/api/', methods=["GET"])
def search():
    title = request.form.get('search')
    search = "%{}%".format(title)
    
    authors = db.session.query(User.id, User.name, User.email, User.image).\
                filter(User.name.ilike(search), User.isartist == True).all()

    return artists_schema.jsonify(authors)

@api.route('/feed/api/<user_id>', methods=["GET"])
def feed(user_id):
    musics = db.session.query(Music.id, Music.music_title, Music.music_source, User.name, Albums.album_img, Albums.album_title, 
                              Music.time_added.label('time_added'))\
            .join(User, Music.artist_id == User.id).join(Music, and_(Music.id == Music.album_id, Music.author_id == User.id))\
            .join(Followers, Followers.followed_id == User.id).filter(Followers.follower_id == user_id)\
            .join(Albums, Albums.id == Music.album_id)\
            .group_by(Music.id, User.name, Music.music_title, Music.music_source, Music.time_added, Albums.album_title, 
                      Albums.album_img).order_by(desc('time_added')).all()
    
    return audio_schema.jsonify(musics)

@api.route('/stream/api/', methods=["POST"])
def stream():
    music_title = request.form.get("music_title")

    db.session.query(Music).filter(Music.music_title == music_title).update({'streams': Music.streams + 1})
    db.session.commit()

    return jsonify(['+1 stream'])

@api.route('/uploaded_songs/api/', methods=["GET"])
def show_uploaded_songs():
    audios = db.session.query(Music.id, Music.music_title, Music.music_source,
                               User.name.label("author_name"), Albums.album_img, Music.streams)\
                        .join(User, User.id==Music.author_id).join(Albums, Albums.id==Music.album_id).all()
    
    return musics_schema.jsonify(audios)

@api.route('/uploaded_songs/api/<artist_id>', methods=["GET"])
def show_uploaded_songs_single(artist_id):
    audios = db.session.query(Music.id, Music.music_title, Music.music_source,
                               User.name.label("author_name"), Albums.album_img, Music.streams)\
                        .join(User, User.id == Music.author_id).join(Albums, Albums.id == Music.album_id).filter(User.id == artist_id)
    
    return musics_schema.jsonify(audios)

@api.route('/collaborations/api/<second_artist>', methods=["GET"])
def collaborations(second_artist):
    collaborations = db.session.query(Collaborations.first_artist, User.name, User.image)\
                    .join(User, User.id == Collaborations.first_artist)\
                    .filter(Collaborations.second_artist == second_artist, Collaborations.isapproved == False).all()
    
    return collaboration_schema.jsonify(collaborations)

@api.route('/collaboration/collaborate/api/<first_artist>', methods=["POST"])
def collaborate(first_artist):
    second_artist = request.form.get('second_artist')

    collaboration = Collaborations(first_artist=first_artist, second_artist=second_artist)

    db.session.add(collaboration)
    db.session.commit()

    return jsonify(['send collab'])

@api.route('/collaboration/accept/api/<second_artist>', methods=["POST"])
def collaboration_accept(second_artist):
    first_artist = request.form.get('first_artist')

    collaboration = Collaborations.query.filter_by(first_artist=first_artist, second_artist=second_artist).first()
    collaboration.isapproved = True
    db.session.commit()

    return jsonify(['accepted'])

@api.route('/collaboration/deny/api/<second_artist>', methods=["POST"])
def collaboration_deny(second_artist):
    first_artist = request.form.get('first_artist')

    collaboration = Collaborations.query.filter_by(first_artist=first_artist, second_artist=second_artist).first()
    db.session.delete(collaboration)
    db.session.commit()

    return jsonify(['denied'])