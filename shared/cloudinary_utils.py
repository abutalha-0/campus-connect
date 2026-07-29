import cloudinary.uploader


def upload_image(file, folder="campus_connect"):
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        allowed_formats=["jpg", "jpeg", "png", "webp"],
        transformation=[
            {"quality": "auto"},
            {"fetch_format": "auto"}
        ]
    )
    return result.get("secure_url")


def upload_file(file, folder="campus_connect"):
    """
    Upload any file type (PDF, PPT, DOC, etc.) to Cloudinary. Uses
    resource_type="auto" so non-image documents are accepted, unlike
    upload_image() which is restricted to image formats.
    """
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="auto"
    )
    return result.get("secure_url")


def delete_image(public_id):
    cloudinary.uploader.destroy(public_id)

def extract_public_id(cloudinary_url):
    try:
        # URL format:
        # https://res.cloudinary.com/cloud/image/upload/v123/folder/filename.jpg
        # public_id is everything after /upload/vXXX/ without the extension
        parts = cloudinary_url.split("/upload/")
        if len(parts) < 2:
            return None
        after_upload = parts[1]
        # remove version number (v123/) if present
        if after_upload.startswith("v") and "/" in after_upload:
            after_upload = after_upload.split("/", 1)[1]
        # remove file extension
        public_id = after_upload.rsplit(".", 1)[0]
        return public_id
    except Exception:
        return None