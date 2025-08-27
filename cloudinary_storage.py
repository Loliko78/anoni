import cloudinary
import cloudinary.uploader
import os
from werkzeug.utils import secure_filename

# Конфигурация Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

def upload_file_to_cloudinary(file, user_id):
    """Загружает файл в Cloudinary"""
    try:
        # Генерируем уникальное имя файла
        filename = secure_filename(f"{user_id}_{file.filename}")
        
        # Загружаем файл
        result = cloudinary.uploader.upload(
            file,
            public_id=filename,
            folder="harvest_messenger",
            resource_type="auto"  # Автоопределение типа файла
        )
        
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_file_from_cloudinary(public_id):
    """Удаляет файл из Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result['result'] == 'ok'
    except:
        return False