from sqlalchemy.sql import func
from flask_login import UserMixin
from . import db
from . import ma

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))    
    image = db.Column(db.String(100))
    isartist = db.Column(db.Boolean, default=False)

class Albums(db.Model):
    __tablename__ = 'albums'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)    
    album_title = db.Column(db.String(255))
    album_img = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))    
    isalbum = db.Column(db.Boolean, default=True)

class Music(db.Model):
    __tablename__ = 'music'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    music_title = db.Column(db.String(255))
    music_source = db.Column(db.String(255))
    streams = db.Column(db.Integer, default=0)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
    featured_artist = db.Column(db.String(100), db.ForeignKey('users.name'))
    time_added = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Favourites(db.Model):
    __tablename__ = 'favourites'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))

class Genres(db.Model):
    __tablename__ = 'genres'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(255))
    genre_img = db.Column(db.String(255))

class Playlists(db.Model):
    __tablename__ = 'playlists'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class PlaylistMusic(db.Model):
    __tablename__ = 'playlist_music'
    __table_args__ = {'extend_existing':True}
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id')) 

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'image', 'isartist')   

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class ArtistsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'image')

artist_schema = ArtistsSchema()
artists_schema = ArtistsSchema(many=True)

class MusicSchema(ma.Schema):
    class Meta:
        fields = ('id', 'music_title', 'music_source', 'author_name', 'album_title', 'album_img', 'streams', 'featured_artist')

class AudioSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'source', 'name', 'album_img', 'album_title', 'time_added', 'streams', 'featured_artist')

audio_schema = AudioSchema(many=True)

music_schema = MusicSchema()
musics_schema = MusicSchema(many=True)

class PlaylistSchema(ma.Schema):
    class Meta:
        fields = ('id', 'playlist_name')

playlist_schema = PlaylistSchema(many=True)

class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'album_title', 'album_img', 'author_name')

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)

class Followers(db.Model):
    __tablename__ = 'followers'
    id = db.Column(db.Integer, primary_key=True)    
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))    
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))    
    time_followed = db.Column(db.DateTime(timezone=True), server_default=func.now())

class FollowerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

followers_schema = FollowerSchema(many=True)

class WaitingReleases(db.Model):
    __tablename__ = 'waitingList'
    id = db.Column(db.Integer, primary_key=True)    
    album_title = db.Column(db.String(255))
    album_img = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))    
    isalbum = db.Column(db.Boolean, default=True)


class WaitingAudios(db.Model):
    __tablename__ = 'waitingAudios'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    source = db.Column(db.String(255))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('waitingList.id'))
    featured_artist = db.Column(db.String, db.ForeignKey('users.name'))

class ListeningHistory(db.Model):
    __tablename__ = 'listeningHistory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))
    time_added = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Subscriptions(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time_added = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Collaborations(db.Model):
    __tablename__ = 'collaborations'
    id = db.Column(db.Integer, primary_key=True)
    first_artist = db.Column(db.Integer, db.ForeignKey('users.id'))
    second_artist = db.Column(db.Integer, db.ForeignKey('users.id'))
    isapproved = db.Column(db.Boolean, default=False)

class CollaborationSchema(ma.Schema):
    class Meta:
        fields = ('first_artist', 'name', 'image')

collaboration_schema = CollaborationSchema(many=True)