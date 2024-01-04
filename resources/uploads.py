from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename
from flask import request
from models import BookCSV, User
from db import db
from schemas import FileUploadResponseSchema
from dotenv import load_dotenv

import logging
import boto3

load_dotenv()
s3_client = boto3.client('s3')

blp = Blueprint('uploads', __name__, description='File Upload Operations')

ALLOWED_EXTENSIONS = {'csv'}


logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logfile_csv_book_upload.log')
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@blp.route('/books/<int:user_id>')
class CSVUploadView(MethodView):

    @blp.response(200, FileUploadResponseSchema)
    def post(self, user_id):
        file = request.files.get('file')
        filename = secure_filename(file.filename)

        if not file or not allowed_file(file.filename):
            abort(400, message='Invalid file type')

        user = User.query.get(user_id)
        if not user:
            abort(404, message='User not found')

        upload_success =  upload_file_to_s3(file, 'wrec-upload-book-csv', f'user-csv/{user_id}/{filename}')
        if upload_success:
            book_csv = BookCSV(filename=filename, user_id=user_id, s3_url=f's3://your-s3-bucket-name/user-csv/{user_id}/{filename}')
            db.session.add(book_csv)
            db.session.commit()
            response_data = {'message': f'File uploaded successfully for user {user_id}.',
                            'filename': filename,
                            's3_url': f's3://your-s3-bucket-name/user-csv/{user_id}/{filename}'}
            return response_data
        else:
            abort(500, message='Failed to upload file')


def upload_file_to_s3(file, bucket_name, object_name):
    """Upload a file to an S3 bucket

    :param file: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        logger.info(f'File {object_name} uploaded to {bucket_name}')
        return True
    except Exception as e:
        logger.error(f'Error uploading file to S3: {e}')
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


