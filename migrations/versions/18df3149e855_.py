"""empty message

Revision ID: 18df3149e855
Revises: 
Create Date: 2019-02-02 09:36:00.439642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18df3149e855'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('jonc_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mesure',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('origin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=5), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_origin_created_at'), 'origin', ['created_at'], unique=False)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_role_default'), 'role', ['default'], unique=False)
    op.create_table('sample_nature',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_nature_created_at'), 'sample_nature', ['created_at'], unique=False)
    op.create_table('sample_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_type_created_at'), 'sample_type', ['created_at'], unique=False)
    op.create_table('study',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_created_at'), 'study', ['created_at'], unique=False)
    op.create_table('support',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('siggle', sa.String(length=120), nullable=True),
    sa.Column('volume', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_created_at'), 'support', ['created_at'], unique=False)
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('display_as', sa.String(length=120), nullable=True),
    sa.Column('firstname', sa.String(length=128), nullable=True),
    sa.Column('lastname', sa.String(length=128), nullable=True),
    sa.Column('adresse', sa.String(length=255), nullable=True),
    sa.Column('telephone', sa.String(length=140), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'], unique=True)
    op.create_index(op.f('ix_customer_telephone'), 'customer', ['telephone'], unique=True)
    op.create_index(op.f('ix_customer_timestamp'), 'customer', ['timestamp'], unique=False)
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('study_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['study_id'], ['study.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subject_created_at'), 'subject', ['created_at'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('last_message_read_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('basket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_basket_created_at'), 'basket', ['created_at'], unique=False)
    op.create_table('box_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('max_number', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_box_type_created_at'), 'box_type', ['created_at'], unique=False)
    op.create_table('disease',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['disease.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disease_created_at'), 'disease', ['created_at'], unique=False)
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_type_created_at'), 'equipment_type', ['created_at'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('label',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_label_created_at'), 'label', ['created_at'], unique=False)
    op.create_table('location_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_type', sa.String(length=255), nullable=True),
    sa.Column('old_location', sa.String(length=255), nullable=True),
    sa.Column('new_location', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_location_history_created_at'), 'location_history', ['created_at'], unique=False)
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_timestamp'), 'message', ['timestamp'], unique=False)
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('payload_json', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_name'), 'notification', ['name'], unique=False)
    op.create_index(op.f('ix_notification_timestamp'), 'notification', ['timestamp'], unique=False)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(length=5), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('program',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_created_at'), 'program', ['created_at'], unique=False)
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('max_number', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_created_at'), 'room', ['created_at'], unique=False)
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    op.create_table('technique',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('category', sa.Integer(), nullable=True),
    sa.Column('out_number', sa.Integer(), nullable=True),
    sa.Column('in_number', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_technique_created_at'), 'technique', ['created_at'], unique=False)
    op.create_table('temperature',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_temperature_created_at'), 'temperature', ['created_at'], unique=False)
    op.create_table('equipment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('equipment_type_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('horizontal', sa.Integer(), nullable=True),
    sa.Column('vertical', sa.Integer(), nullable=True),
    sa.Column('max_number', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['equipment_type_id'], ['equipment_type.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_created_at'), 'equipment', ['created_at'], unique=False)
    op.create_table('print',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('label_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['label_id'], ['label.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_print_serial'), 'print', ['serial'], unique=False)
    op.create_index(op.f('ix_print_timestamp'), 'print', ['timestamp'], unique=False)
    op.create_table('process',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('technique_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['technique_id'], ['technique.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_created_at'), 'process', ['created_at'], unique=False)
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('study_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('program_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['program.id'], ),
    sa.ForeignKeyConstraint(['study_id'], ['study.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_timestamp'), 'project', ['timestamp'], unique=False)
    op.create_table('expedition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('telephone', sa.String(length=255), nullable=True),
    sa.Column('temperature_id', sa.Integer(), nullable=True),
    sa.Column('expedition_date', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['temperature_id'], ['temperature.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expedition_timestamp'), 'expedition', ['timestamp'], unique=False)
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('telephone', sa.String(length=255), nullable=True),
    sa.Column('send_date', sa.String(length=255), nullable=True),
    sa.Column('temperature_id', sa.Integer(), nullable=True),
    sa.Column('receive_date', sa.String(length=255), nullable=True),
    sa.Column('nbr_pack', sa.String(length=255), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_url', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['temperature_id'], ['temperature.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_timestamp'), 'order', ['timestamp'], unique=False)
    op.create_table('rack',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('equipment_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('horizontal', sa.Integer(), nullable=True),
    sa.Column('vertical', sa.Integer(), nullable=True),
    sa.Column('max_number', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rack_created_at'), 'rack', ['created_at'], unique=False)
    op.create_table('box',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rack_id', sa.Integer(), nullable=True),
    sa.Column('horizontal', sa.Integer(), nullable=True),
    sa.Column('vertical', sa.Integer(), nullable=True),
    sa.Column('box_type_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['box_type_id'], ['box_type.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['rack_id'], ['rack.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_box_created_at'), 'box', ['created_at'], unique=False)
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('origin_id', sa.Integer(), nullable=True),
    sa.Column('code', sa.String(length=120), nullable=True),
    sa.Column('bio_code', sa.String(length=120), nullable=True),
    sa.Column('birthday', sa.String(length=128), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('sexe', sa.Integer(), nullable=True),
    sa.Column('city', sa.String(length=128), nullable=True),
    sa.Column('job', sa.String(length=128), nullable=True),
    sa.Column('clinical_data', sa.String(length=255), nullable=True),
    sa.Column('observation_file', sa.Integer(), nullable=True),
    sa.Column('observation_file_url', sa.String(length=255), nullable=True),
    sa.Column('sample_file', sa.Integer(), nullable=True),
    sa.Column('sample_file_url', sa.String(length=255), nullable=True),
    sa.Column('consent_file', sa.Integer(), nullable=True),
    sa.Column('consent_file_url', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['origin_id'], ['origin.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_created_at'), 'patient', ['created_at'], unique=False)
    op.create_table('sample',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('expedition_id', sa.Integer(), nullable=True),
    sa.Column('origin_id', sa.Integer(), nullable=True),
    sa.Column('sample_nature_id', sa.Integer(), nullable=True),
    sa.Column('sample_type_id', sa.Integer(), nullable=True),
    sa.Column('support_id', sa.Integer(), nullable=True),
    sa.Column('jonc_type_id', sa.Integer(), nullable=True),
    sa.Column('mesure_id', sa.Integer(), nullable=True),
    sa.Column('technique', sa.String(length=255), nullable=True),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('code', sa.String(length=255), nullable=True),
    sa.Column('date', sa.String(length=255), nullable=True),
    sa.Column('site', sa.String(length=255), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('in_basket', sa.Integer(), nullable=True),
    sa.Column('basket_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['basket_id'], ['basket.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['expedition_id'], ['expedition.id'], ),
    sa.ForeignKeyConstraint(['jonc_type_id'], ['jonc_type.id'], ),
    sa.ForeignKeyConstraint(['mesure_id'], ['mesure.id'], ),
    sa.ForeignKeyConstraint(['origin_id'], ['origin.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['sample.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['sample_nature_id'], ['sample_nature.id'], ),
    sa.ForeignKeyConstraint(['sample_type_id'], ['sample_type.id'], ),
    sa.ForeignKeyConstraint(['support_id'], ['support.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_created_at'), 'sample', ['created_at'], unique=False)
    op.create_table('store',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('box_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['box_id'], ['box.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_store_serial'), 'store', ['serial'], unique=False)
    op.create_index(op.f('ix_store_timestamp'), 'store', ['timestamp'], unique=False)
    op.create_table('aliquot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('sample_id', sa.Integer(), nullable=True),
    sa.Column('support_id', sa.Integer(), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('mesure_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['mesure_id'], ['mesure.id'], ),
    sa.ForeignKeyConstraint(['sample_id'], ['sample.id'], ),
    sa.ForeignKeyConstraint(['support_id'], ['support.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aliquot_created_at'), 'aliquot', ['created_at'], unique=False)
    op.create_index(op.f('ix_aliquot_serial'), 'aliquot', ['serial'], unique=False)
    op.create_table('hole',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('box_id', sa.Integer(), nullable=True),
    sa.Column('sample_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['box_id'], ['box.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sample_id'], ['sample.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hole_created_at'), 'hole', ['created_at'], unique=False)
    op.create_table('print_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('print_id', sa.Integer(), nullable=True),
    sa.Column('sample_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['print_id'], ['print.id'], ),
    sa.ForeignKeyConstraint(['sample_id'], ['sample.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_print_item_timestamp'), 'print_item', ['timestamp'], unique=False)
    op.create_table('aliquot_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('aliquot_id', sa.Integer(), nullable=True),
    sa.Column('serial', sa.String(length=255), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['aliquot_id'], ['aliquot.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aliquot_item_serial'), 'aliquot_item', ['serial'], unique=False)
    op.create_index(op.f('ix_aliquot_item_timestamp'), 'aliquot_item', ['timestamp'], unique=False)
    op.create_table('sample_hole_history',
    sa.Column('sample_id', sa.Integer(), nullable=True),
    sa.Column('hole_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['hole_id'], ['hole.id'], ),
    sa.ForeignKeyConstraint(['sample_id'], ['sample.id'], )
    )
    op.create_table('store_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('sample_id', sa.Integer(), nullable=True),
    sa.Column('hole_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['hole_id'], ['hole.id'], ),
    sa.ForeignKeyConstraint(['sample_id'], ['sample.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_store_item_timestamp'), 'store_item', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_store_item_timestamp'), table_name='store_item')
    op.drop_table('store_item')
    op.drop_table('sample_hole_history')
    op.drop_index(op.f('ix_aliquot_item_timestamp'), table_name='aliquot_item')
    op.drop_index(op.f('ix_aliquot_item_serial'), table_name='aliquot_item')
    op.drop_table('aliquot_item')
    op.drop_index(op.f('ix_print_item_timestamp'), table_name='print_item')
    op.drop_table('print_item')
    op.drop_index(op.f('ix_hole_created_at'), table_name='hole')
    op.drop_table('hole')
    op.drop_index(op.f('ix_aliquot_serial'), table_name='aliquot')
    op.drop_index(op.f('ix_aliquot_created_at'), table_name='aliquot')
    op.drop_table('aliquot')
    op.drop_index(op.f('ix_store_timestamp'), table_name='store')
    op.drop_index(op.f('ix_store_serial'), table_name='store')
    op.drop_table('store')
    op.drop_index(op.f('ix_sample_created_at'), table_name='sample')
    op.drop_table('sample')
    op.drop_index(op.f('ix_patient_created_at'), table_name='patient')
    op.drop_table('patient')
    op.drop_index(op.f('ix_box_created_at'), table_name='box')
    op.drop_table('box')
    op.drop_index(op.f('ix_rack_created_at'), table_name='rack')
    op.drop_table('rack')
    op.drop_index(op.f('ix_order_timestamp'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_expedition_timestamp'), table_name='expedition')
    op.drop_table('expedition')
    op.drop_index(op.f('ix_project_timestamp'), table_name='project')
    op.drop_table('project')
    op.drop_index(op.f('ix_process_created_at'), table_name='process')
    op.drop_table('process')
    op.drop_index(op.f('ix_print_timestamp'), table_name='print')
    op.drop_index(op.f('ix_print_serial'), table_name='print')
    op.drop_table('print')
    op.drop_index(op.f('ix_equipment_created_at'), table_name='equipment')
    op.drop_table('equipment')
    op.drop_index(op.f('ix_temperature_created_at'), table_name='temperature')
    op.drop_table('temperature')
    op.drop_index(op.f('ix_technique_created_at'), table_name='technique')
    op.drop_table('technique')
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_room_created_at'), table_name='room')
    op.drop_table('room')
    op.drop_index(op.f('ix_program_created_at'), table_name='program')
    op.drop_table('program')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_notification_timestamp'), table_name='notification')
    op.drop_index(op.f('ix_notification_name'), table_name='notification')
    op.drop_table('notification')
    op.drop_index(op.f('ix_message_timestamp'), table_name='message')
    op.drop_table('message')
    op.drop_index(op.f('ix_location_history_created_at'), table_name='location_history')
    op.drop_table('location_history')
    op.drop_index(op.f('ix_label_created_at'), table_name='label')
    op.drop_table('label')
    op.drop_table('followers')
    op.drop_index(op.f('ix_equipment_type_created_at'), table_name='equipment_type')
    op.drop_table('equipment_type')
    op.drop_table('document')
    op.drop_index(op.f('ix_disease_created_at'), table_name='disease')
    op.drop_table('disease')
    op.drop_index(op.f('ix_box_type_created_at'), table_name='box_type')
    op.drop_table('box_type')
    op.drop_index(op.f('ix_basket_created_at'), table_name='basket')
    op.drop_table('basket')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_subject_created_at'), table_name='subject')
    op.drop_table('subject')
    op.drop_index(op.f('ix_customer_timestamp'), table_name='customer')
    op.drop_index(op.f('ix_customer_telephone'), table_name='customer')
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
    op.drop_table('customer')
    op.drop_index(op.f('ix_support_created_at'), table_name='support')
    op.drop_table('support')
    op.drop_index(op.f('ix_study_created_at'), table_name='study')
    op.drop_table('study')
    op.drop_index(op.f('ix_sample_type_created_at'), table_name='sample_type')
    op.drop_table('sample_type')
    op.drop_index(op.f('ix_sample_nature_created_at'), table_name='sample_nature')
    op.drop_table('sample_nature')
    op.drop_index(op.f('ix_role_default'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_origin_created_at'), table_name='origin')
    op.drop_table('origin')
    op.drop_table('mesure')
    op.drop_table('jonc_type')
    op.drop_table('category')
    # ### end Alembic commands ###
