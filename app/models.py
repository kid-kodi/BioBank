import base64
from datetime import datetime, timedelta
from hashlib import md5
import json
import os
from time import time
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import rq
from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(128))
    customers = db.relationship('Customer', backref='category', lazy='dynamic')


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    display_as = db.Column(db.String(120))
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    adresse = db.Column(db.String(255))
    telephone = db.Column(db.String(140), index=True, unique=True)
    email = db.Column(db.String(255), index=True, unique=True)
    projects = db.relationship('Project', backref='customer', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        data = {
            'id': self.id,
            'display_as': self.display_as,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'firstname': self.firstname,
            'lastname': self.lastname,
            'adresse': self.adresse,
            'telephone': self.telephone,
            'email': self.email,
        }
        return data

    def from_dict(self, data):
        for field in ['display_as', 'firstname', 'lastname']:
            if field in data:
                setattr(self, field, data[field])


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    study_id = db.Column(db.Integer, db.ForeignKey('study.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    orders = db.relationship('Order', backref='project', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def total_sample(self):
        number = 0
        orders = self.orders
        for o in orders:
            number = number + o.total_sample()
        return number

    def total_patient(self):
        number = 0
        orders = self.orders
        for o in orders:
            number = number + o.total_patient()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'customer_id': self.customer_id,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'study_id': self.study_id,
            'subject_id': self.subject_id,
            'program_id': self.program_id,
            'title': self.title,
            'description': self.description,
        }
        return json_post

    def from_json(self, data):
        for field in ['title', 'description', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    firstname = db.Column(db.String(255))
    serial = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    telephone = db.Column(db.String(255))
    order_date = db.Column(db.String(255))
    transport_date = db.Column(db.String(255))
    temperature = db.Column(db.String(255))
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patients = db.relationship('Patient', backref='order', lazy='dynamic')

    def total_sample(self):
        number = 0
        patients = self.patients
        for p in patients:
            number = number + p.total_sample()
        return number

    def total_patient(self):
        number = len(self.patients.all())
        return number


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    subjects = db.relationship('Subject', backref='study', lazy='dynamic')
    projects = db.relationship('Project', backref='study', lazy='dynamic')


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey('study.id'))
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    programs = db.relationship('Program', backref='subject', lazy='dynamic')
    projects = db.relationship('Project', backref='subject', lazy='dynamic')


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    projects = db.relationship('Project', backref='program', lazy='dynamic')


class SampleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='sample_type', lazy='dynamic')


class SampleNature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='sample_nature', lazy='dynamic')


class Origin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(5))
    description = db.Column(db.String(128))
    patients = db.relationship('Patient', backref='origin', lazy='dynamic')


class TubeType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='tube_type', lazy='dynamic')


class Mesure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='mesure', lazy='dynamic')


class JoncType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='jonc_type', lazy='dynamic')


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'))
    code = db.Column(db.String(120))
    bio_code = db.Column(db.String(120))
    birthday = db.Column(db.String(128))
    age = db.Column(db.Integer)
    sexe = db.Column(db.Integer)
    city = db.Column(db.String(128))
    job = db.Column(db.String(128))
    clinical_data = db.Column(db.String(255))
    observation_file = db.Column(db.Integer)
    observation_file_url = db.Column(db.String(255))
    sample_file = db.Column(db.Integer)
    sample_file_url = db.Column(db.String(255))
    consent_file = db.Column(db.Integer)
    consent_file_url = db.Column(db.String(255))
    samples = db.relationship('Sample', backref='patient', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def total_sample(self):
        number = len(self.samples.all())
        return number


sample_hole_history = db.Table(
    'sample_hole_history',
    db.Column('sample_id', db.Integer, db.ForeignKey('sample.id')),
    db.Column('hole_id', db.Integer, db.ForeignKey('hole.id'))
)


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    sample_nature_id = db.Column(db.Integer, db.ForeignKey('sample_nature.id'))
    sample_type_id = db.Column(db.Integer, db.ForeignKey('sample_type.id'))
    tube_type_id = db.Column(db.Integer, db.ForeignKey('tube_type.id'))
    jonc_type_id = db.Column(db.Integer, db.ForeignKey('jonc_type.id'))
    mesure_id = db.Column(db.Integer, db.ForeignKey('mesure.id'))
    technique = db.Column(db.String(255))
    serial = db.Column(db.String(255))
    code = db.Column(db.String(255))
    date = db.Column(db.String(255))
    site = db.Column(db.String(255))
    volume = db.Column(db.Integer)
    status = db.Column(db.Integer)
    in_basket = db.Column(db.Integer)
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'))
    aliquots = db.relationship('Aliquot', backref='sample', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('sample.id'))
    children = db.relationship("Sample", backref=db.backref('parent', remote_side=[id]))
    holes = db.relationship(
        "Hole",
        secondary=sample_hole_history,
        back_populates="samples")


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    samples = db.relationship('Sample', backref='basket', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Temperature {}>'.format(self.name)


# 1 - pushing(aliquot), 2 pulling
class Technique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    category = db.Column(db.Integer, default=1)
    out_number = db.Column(db.Integer, default=0)
    in_number = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255))
    processes = db.relationship('Process', backref='technique', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Technique {}>'.format(self.name)


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    technique_id = db.Column(db.Integer, db.ForeignKey('technique.id'))
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Process {}>'.format(self.name)


class Aliquot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'))
    volume = db.Column(db.Integer)
    number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Process {}>'.format(self.name)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    equipments = db.relationship('Equipment', backref='room', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Room {}>'.format(self.name)

    def available(self):
        number = 0
        equipments = self.equipments
        for equipment in equipments:
            number = number + equipment.available()
        return number

    def occupied(self):
        number = 0
        equipments = self.equipments
        for equipment in equipments:
            number = number + equipment.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at
        }
        return json_post


class EquipmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    equipments = db.relationship('Equipment', backref='equipment_type', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<EquipmentType {}>'.format(self.name)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    equipment_type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'))
    name = db.Column(db.String(255))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    racks = db.relationship('Rack', backref='equipment', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Equipment {}>'.format(self.name)

    def available(self):
        number = 0
        racks = self.racks
        for rack in racks:
            number = number + rack.available()
        return number

    def occupied(self):
        number = 0
        racks = self.racks
        for rack in racks:
            number = number + rack.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'room_id': self.room_id,
            'equipment_type_id': self.equipment_type_id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class Rack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    name = db.Column(db.String(255))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    boxes = db.relationship('Box', backref='rack', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Rack {}>'.format(self.name)

    def available(self):
        number = 0
        boxes = self.boxes
        for boxe in boxes:
            number = number + boxe.available()
        return number

    def occupied(self):
        number = 0
        boxes = self.boxes
        for boxe in boxes:
            number = number + boxe.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class BoxType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    max_number = db.Column(db.Integer)
    description = db.Column(db.String(255))
    boxes = db.relationship('Box', backref='box_type', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<BoxType {}>'.format(self.name)


class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('rack.id'))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    box_type_id = db.Column(db.Integer, db.ForeignKey('box_type.id'))
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)
    holes = db.relationship('Hole', backref='box', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<box {}>'.format(self.name)

    def available(self):
        number = 0
        holes = self.holes
        for hole in holes:
            if hole.status == 0:
                number = number + 1
        return number

    def occupied(self):
        number = 0
        holes = self.holes
        for hole in holes:
            if hole.status == 1:
                number = number + 1
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'rack_id': self.rack_id,
            'box_type_id': self.box_type_id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by,
            'holes_count': self.holes.count(),
            'free_holes': self.holes.filter_by(status=0).count(),
            'used_holes': self.holes.filter_by(status=1).count()
        }
        return json_post


class Hole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'))
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'))
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    samples = db.relationship(
        "Sample",
        secondary=sample_hole_history,
        back_populates="holes")

    def __repr__(self):
        return '<Hole {}>'.format(self.name)

    def is_available(self):
        return self.status == 0

    def to_json(self):
        json_post = {
            'id': self.id,
            'box_id': self.box_id,
            'sample_id': self.sample_id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class LocationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_type = db.Column(db.String(255))
    old_location = db.Column(db.String(255))
    new_location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<LocationHistory {}>'.format(self.name)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class Init():
    def start(self):
        category = Category(name='Unité', description='')
        db.session.add(category)
        category = Category(name='Chercheur', description='')
        db.session.add(category)
        category = Category(name='Industriel', description='')
        db.session.add(category)
        category = Category(name='Clinicien', description='')
        db.session.add(category)
        category = Category(name='Sample', description='')
        db.session.add(category)

        customer = Customer(display_as='customer 1', email='customer@gmail.com')
        db.session.add(customer)

        origin = Origin(name='Humain', sign='HU', description='')
        db.session.add(origin)
        origin = Origin(name='Animal', sign='AN', description='')
        db.session.add(origin)
        origin = Origin(name='Environementale', sign='EN', description='')
        db.session.add(origin)

        sample_type = SampleType(siggle='-fn-', name='-fn-', description='')
        db.session.add(sample_type)

        sample_type = SampleType(siggle='-in-', name='-in-', description='')
        db.session.add(sample_type)

        sample_nature = SampleNature(name='Sang', siggle="Sg", description='')
        db.session.add(sample_nature)

        sample_nature = SampleNature(name='Urine', siggle="Ur", description='')
        db.session.add(sample_nature)

        sample_nature = SampleNature(name='LCR', siggle="Lcr", description='')
        db.session.add(sample_nature)

        tube_type = TubeType(name='EDTA', siggle='', description='')
        db.session.add(tube_type)

        tube_type = TubeType(name='Tube sec', description='')
        db.session.add(tube_type)

        jonc_type = JoncType(name='Rouge', siggle='Rouge', description='')
        db.session.add(jonc_type)

        jonc_type = JoncType(name='Bleu', siggle='Rouge', description='')
        db.session.add(jonc_type)

        jonc_type = JoncType(name='Vert', siggle='Rouge', description='')
        db.session.add(jonc_type)

        jonc_type = JoncType(name='Jaune', siggle='Rouge', description='')
        db.session.add(jonc_type)

        mesure = Mesure(name='microlitre', siggle='ul', description='')
        db.session.add(mesure)

        mesure = Mesure(name='microgramme', siggle='mg', description='')
        db.session.add(mesure)

        study = Study(name='Etude1', description='')
        db.session.add(study)

        subject = Subject(name='Subject1', description='')
        db.session.add(subject)

        program = Program(name='Program1', description='')
        db.session.add(program)

        user = User(username='@kodi', email='konedangui@pasteur.ci')
        user.set_password('12345')
        db.session.add(user)

        basket = Basket(name='basket1', description="")
        db.session.add(basket)

        temperature = Temperature(name='+18°C')
        db.session.add(temperature)

        temperature = Temperature(name='+4°C')
        db.session.add(temperature)

        temperature = Temperature(name='-20°C')
        db.session.add(temperature)

        temperature = Temperature(name='-80°C')
        db.session.add(temperature)

        # Location management
        room = Room(name='Mireille dosso', max_number=0, status=0)
        db.session.add(room)

        e = Equipment(room_id=room.id, name='Cocody', max_number=200, status=0)
        db.session.add(e)

        rack = Rack(equipment_id=e.id, name='Rack1', max_number=10, status=0)
        db.session.add(rack)

        box_type = BoxType(name='Cryo Boite 100', description='', max_number=100)
        db.session.add(box_type)

        box_type = BoxType(name='Cryo Boite 81', description='', max_number=81)
        db.session.add(box_type)

        equipment_type = EquipmentType(name='Congélateur -20°C', description='')
        db.session.add(equipment_type)

        equipment_type = EquipmentType(name='Congélateur -80°C', description='')
        db.session.add(equipment_type)

        equipment_type = EquipmentType(name='Cryoconservateur', description='')
        db.session.add(equipment_type)

        db.session.commit()
