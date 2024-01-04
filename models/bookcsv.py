from db import db
from datetime import datetime

class BookCSV(db.Model):
    __tablename__ = 'book_csv'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(), nullable=False)
    s3_url = db.Column(db.String(), nullable=True)  # URL to the file in S3
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
