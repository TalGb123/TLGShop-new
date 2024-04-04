import os


def image_exists(image_path):
    media_root = "path_to_your_media_folder"
    full_path = os.path.join(media_root, image_path)

    return os.path.exists(full_path)
