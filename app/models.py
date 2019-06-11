from datetime import datetime

from flask import json
from sqlalchemy import Integer, VARCHAR, DateTime, ForeignKey, Float, Boolean, Text, Date, func
from sqlalchemy.orm import relationship

from app import db


class Groups(db.Model):
    __tablename__ = 'user_groups'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(VARCHAR(255), unique=True)
    desc = db.Column(VARCHAR(255), nullable=True)

    @staticmethod
    def insert_user_groups():
        user_groups = [
            {
                'name': 'superadmin',
                'desc': 'Super Admin'
            },
            {
                'name': 'admin',
                'desc': 'Admin'
            },
            {
                'name': 'user',
                'desc': 'User'
            }
        ]

        for user_group in user_groups:
            grp = Groups.query.filter_by(name=user_group.get('name')).first()

            if not grp:
                db.session.add(Groups(**user_group))

        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc
        }


class Users(db.Model):
    id = db.Column(Integer, primary_key=True)
    firstname = db.Column(VARCHAR(255), nullable=True, default='Anonymous')
    email = db.Column(VARCHAR(255), unique=True)
    created_at = db.Column(DateTime, default=datetime.utcnow())
    updated_at = db.Column(DateTime, nullable=True)
    password_digest = db.Column(VARCHAR(255), nullable=True)
    status = db.Column(Integer, ForeignKey('user_status.id'), nullable=True, default=2)
    user_status = relationship('UserStatus', backref='users')
    password_reset_token = db.Column(VARCHAR(255), nullable=True)
    password_reset_sent_at = db.Column(DateTime, nullable=True)
    lastname = db.Column(VARCHAR(255), nullable=True, default='User')
    organization = db.Column(VARCHAR(255), nullable=True)
    country = db.Column(VARCHAR(255), nullable=True)
    admin_id = db.Column(VARCHAR(255), nullable=True)
    city = db.Column(VARCHAR(255), nullable=True)
    state_province = db.Column(VARCHAR(255), nullable=True)
    street_address = db.Column(VARCHAR(255), nullable=True)
    postal_code = db.Column(VARCHAR(255), nullable=True)
    phone = db.Column(VARCHAR(255), nullable=True)
    mobile_phone = db.Column(VARCHAR(255), nullable=True)
    account_activation_token = db.Column(VARCHAR(255), nullable=True)
    fax = db.Column(VARCHAR(255), nullable=True)
    privileges = db.Column(Integer, ForeignKey('user_groups.id'), default=3)
    user_group = relationship('Groups', backref='users')
    shopperId = db.Column(VARCHAR(255), nullable=True)
    customerId = db.Column(VARCHAR(255), nullable=True)
    credit_balance = db.Column(Float, default=0)
    min_balance = db.Column(Float, nullable=True)
    ns1 = db.Column(VARCHAR(255), nullable=True)
    ns1_ip = db.Column(VARCHAR(255), nullable=True)
    ns2 = db.Column(VARCHAR(255), nullable=True)
    ns2_ip = db.Column(VARCHAR(255), nullable=True)
    ns3 = db.Column(VARCHAR(255), nullable=True)
    ns3_ip = db.Column(VARCHAR(255), nullable=True)
    ns4 = db.Column(VARCHAR(255), nullable=True)
    ns4_ip = db.Column(VARCHAR(255), nullable=True)
    last_login = db.Column(DateTime, nullable=True)
    deleted = db.Column(Boolean, default=False)
    deleted_at = db.Column(DateTime, nullable=True)

    def name(self):
        return f'{self.firstname} {self.lastname}'

    @staticmethod
    def insert_default_user():
        users = [{"id": 196, "firstname": "i3C", "email": "helpdesk@i3c.co.ug", "created_at": "2014-10-23 12:16:59",
                  "updated_at": "2018-08-02 11:17:38",
                  "password_digest": "$2a$10$\/iE8WJ08APP63LTomWFBK.jsTqcRErnv.EazeRQ1Am3LaUdbb0WE6",
                  "status": "1",
                  "password_reset_token": "P9CgrNHCNiyzQ1cxiuCszA",
                  "lastname": "LTD", "organization": "Infinity Computers and Communications Company LTD",
                  "country": "UG",
                  "city": "Kampala", "state_province": "", "street_address": "plot 6b windsor loop kololo",
                  "postal_code": "12510", "phone": "0312301800", "mobile_phone": "0312301800",
                  "fax": "vtinka@i3c.co.ug", "privileges": "2", "ns1": "ns1.cfi.co.ug", "ns1_ip": "50.22.208.130",
                  "ns2": "ns2.cfi.co.ug", "ns2_ip": "50.22.208.140", "ns3": "ns3.cfi.co.ug", "ns3_ip": "174.36.245.67",
                  "ns4": "ns4.cfi.co.ug", "ns4_ip": "212.88.97.131"},
                 {"id": "209", "firstname": "obella", "email": "wizlif.144@gmail.com",
                  "password_digest": "$2b$12$1uEtB55NOFgSWue.9YE6Cet1EXidnb1cVvrCDbdI.HArQFhmAYkm.", "status": "1",
                  "password_reset_token": "IndpemxpZi4xNDRAZ21haWwuY29tIg.Dm7cDg.FZOiaMrBrcLKpGwIRHMCn5MIjV0",
                  "password_reset_sent_at": "2018-09-03 17:51:59", "lastname": "isaac",
                  "organization": "infinity computers", "country": "UG", "admin_id": None, "city": "kampala",
                  "state_province": "central", "street_address": "plot 6b windsor loop", "postal_code": "6782",
                  "phone": "+256.778916353", "mobile_phone": "+256.778916353",
                  "account_activation_token": "IndpemxpZi4xNDRAZ21haWwuY29tIg.DnO3ZA.GhxPhATjWcnT6b0543NtHSwJb4I",
                  "fax": None, "privileges": "1", "shopperId": None, "customerId": None, "ns1": "ns1.cfi.co.ug",
                  "ns2": "ns2.cfi.co.ug", "ns3": "ns3.cfi.co.ug", "ns4": "ns4.cfi.co.ug",
                  "last_login": "2018-09-28 14:44:16", "ns1_ip": "50.22.208.130", "ns2_ip": "50.22.208.140",
                  "ns3_ip": "198.23.90.155", "ns4_ip": "192.168.100.249", "deleted": False, "deleted_at": None,
                  "credit_balance": "8874"}]

        for user in users:
            usr = Users.query.filter_by(email=user['email']).first()

            if not usr:
                db.session.add(Users(**user))
        db.session.commit()

    def admin(self):
        return 0 < self.privileges < 3

    def to_json(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'name': self.name(),
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.user_status.code if self.user_status else 'INACTIVE',
            'password_reset_sent_at': self.password_reset_sent_at,
            'lastname': self.lastname,
            'organization': self.organization,
            'country': self.country,
            'admin_id': self.admin_id,
            'city': self.city,
            'state_province': self.state_province,
            'street_address': self.street_address,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'mobile_phone': self.mobile_phone,
            'fax': self.fax,
            'privileges': self.user_group.desc,
            'ns1': self.ns1,
            'ns1_ip': self.ns1_ip,
            'ns2': self.ns2,
            'ns2_ip': self.ns2_ip,
            'ns3': self.ns3,
            'ns3_ip': self.ns3_ip,
            'ns4': self.ns4,
            'ns4_ip': self.ns4_ip,
            'last_login': self.last_login,
            'credit_balance': self.credit_balance,
            'min_balance': self.min_balance
        }

    @staticmethod
    def find_by_id(id):
        return Users.query.get(id)


class UserStatus(db.Model):
    __tablename__ = 'user_status'
    id = db.Column(Integer, primary_key=True)
    code = db.Column(VARCHAR(255), unique=True)
    desc = db.Column(VARCHAR(255), nullable=True)

    @staticmethod
    def insert_user_statuses():
        user_statuses = [
            {
                'code': 'ACTIVE',
                'desc': 'User is currently active'
            },
            {
                'code': 'INACTIVE',
                'desc': 'User is currently inactive'
            },
            {
                'code': 'LOCKED',
                'desc': 'User is currently locked'
            },
            {
                'code': 'SUSPENDED',
                'desc': 'User is currently suspended'
            }
        ]

        for user_status in user_statuses:
            status = UserStatus.query.filter_by(code=user_status.get('code')).first()

            if not status:
                db.session.add(UserStatus(**user_status))
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'code': self.code,
            'desc': self.desc
        }
