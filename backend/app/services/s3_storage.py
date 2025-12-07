import boto3
import base64
import logging
from io import BytesIO
from app.config import settings

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

async def upload_image_to_s3(base64_image: str, session_id: str) -> str:
    """Upload base64 image to S3"""
    try:
        # Decode base64
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        image_data = base64.b64decode(base64_image)
        
        # Upload to S3
        key = f"sessions/{session_id}/captured.jpg"
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=image_data,
            ContentType='image/jpeg',
        )
        
        logger.info(f"Image uploaded to S3: {key}")
        return f"s3://{settings.AWS_S3_BUCKET}/{key}"
    except Exception as e:
        logger.error(f"S3 upload error: {e}")
        raise
