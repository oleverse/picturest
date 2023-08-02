import cloudinary
import cloudinary.uploader
import base64
import io
import qrcode
import qrcode.image.base
import qrcode.image.svg

from api.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def upload(file, public_id: str):
        try:
            r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        except cloudinary.exceptions.Error as cl_error:
            raise ValueError(str(cl_error))
        return r

    @staticmethod
    def destroy(public_id):
        cloudinary.uploader.destroy(public_id=public_id)

    @staticmethod
    def get_url_for_picture(public_id, r):
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url

    @staticmethod
    def get_transformed_url(image_url: str, transform_list: list[dict]):
        picture_url = cloudinary.CloudinaryImage(image_url.split("/")[-1]).build_url(transformation=transform_list)
        return picture_url

    @staticmethod
    def get_qrcode(pict_url: str):
        """
        The get_qrcode function takes a pict_url as an argument and returns the QR code for that URL.
        The function uses the qrcode library to create a QR code object from the photo_url, then saves it to a buffer.
        The buffer is encoded in base64 and returned as a string.

        :param pict_url: str: indicates type of data to expect
        :return: A base64 encoded string of a qr code image
        """
        qr = qrcode.make(pict_url)
        buf = io.BytesIO()
        qr.save(buf)
        qr_code = base64.b64encode(buf.getvalue()).decode('ascii')
        return qr_code

