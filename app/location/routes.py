from flask import render_template, request, redirect, url_for
from app import db
from app.models import Room, Box, Rack, Equipment, Hole, Basket, Sample
from app.location import bp
from flask_login import current_user, login_required


@bp.route('/location')
def index():
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    return render_template('location/index.html', rooms=rooms, basket=basket)


@bp.route('/location/room/<int:id>')
def room(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    room = Room.query.get_or_404(id)
    return render_template('location/index.html', rooms=rooms, basket=basket, room=room)


@bp.route('/location/equipment/<int:id>')
def equipment(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    equipment = Equipment.query.get_or_404(id)
    return render_template('location/index.html', rooms=rooms, equipment=equipment, basket=basket)


@bp.route('/location/rack/<int:id>')
def rack(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    rack = Rack.query.get_or_404(id)
    return render_template('location/index.html', rooms=rooms, rack=rack, basket=basket)


@bp.route('/location/box/<int:id>')
def box(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    box = Box.query.get_or_404(id)
    return render_template('location/index.html', rooms=rooms, basket=basket, box=box)


@bp.route('/location/hole/<int:id>')
def hole(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    rooms = Room.query.all()
    hole = Hole.query.get_or_404(id)
    box = Box.query.get_or_404(hole.box_id)
    return render_template('location/index.html', rooms=rooms, basket=basket, box=box, hole=hole)


@bp.route('/location/store/<int:id>', methods=['GET', 'POST'])
def store(id):
    if request.method == 'POST':
        box = Box.query.get_or_404(id)
        sampleIds = request.form.getlist('samples_id')
        basket = Basket.query.filter_by(created_by=current_user.id).first()
        for sid in sampleIds:
            sample = Sample.query.get_or_404(sid)
            if sample.status == 0:
                hole = box.holes.filter_by(status=0).first()
                hole.status = 1
                sample.status = 1
                basket.samples.remove(sample)
                sample.holes.append(hole)
                db.session.add(sample)
                db.session.commit()
        return redirect(url_for('location.index'))
