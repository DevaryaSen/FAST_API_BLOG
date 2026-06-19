import io
import uuid

import boto3
from PIL import Image
from botocore.exceptions import ClientError

from config import settings

MAX_IMAGE_SIZE = (256, 256)


def _get_s3_client():
    kwargs = {
        "region_name": settings.s3_region,
    }
    if settings.s3_access_key_id:
        kwargs["aws_access_key_id"] = settings.s3_access_key_id.get_secret_value()
    if settings.s3_secret_access_key:
        kwargs["aws_secret_access_key"] = settings.s3_secret_access_key.get_secret_value()
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    """Resize and convert image to JPEG. Returns (bytes, filename)."""
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGB")
    img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85)
    output.seek(0)

    filename = f"{uuid.uuid4().hex}.jpg"
    return output.read(), filename


async def upload_profile_image(data: bytes, filename: str) -> None:
    """Upload image bytes to S3."""
    s3 = _get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=f"profile_pics/{filename}",
        Body=data,
        ContentType="image/jpeg",
    )


async def delete_profile_image(filename: str) -> None:
    """Delete image from S3, ignoring errors."""
    try:
        s3 = _get_s3_client()
        s3.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=f"profile_pics/{filename}",
        )
    except ClientError:
        pass
