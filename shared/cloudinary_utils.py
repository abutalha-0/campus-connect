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


def delete_image(public_id):
    cloudinary.uploader.destroy(public_id)