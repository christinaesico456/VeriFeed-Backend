from django.http import JsonResponse
import os
from django.conf import settings

def check_media_files(request):
    """Debug view to check if media files exist on the server"""
    media_root = settings.MEDIA_ROOT
    profile_pics_dir = os.path.join(media_root, 'profile_pics')
    default_jpg = os.path.join(profile_pics_dir, 'default.jpg')
    
    return JsonResponse({
        'media_root': str(media_root),
        'media_root_exists': os.path.exists(media_root),
        'profile_pics_dir': str(profile_pics_dir),
        'profile_pics_exists': os.path.exists(profile_pics_dir),
        'default_jpg_path': str(default_jpg),
        'default_jpg_exists': os.path.exists(default_jpg),
        'media_root_contents': os.listdir(media_root) if os.path.exists(media_root) else [],
        'profile_pics_contents': os.listdir(profile_pics_dir) if os.path.exists(profile_pics_dir) else [],
    })