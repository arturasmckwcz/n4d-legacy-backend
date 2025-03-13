import boto3
import structlog

from alfred.settings import AWS_ACCESS_KEY_ID, AWS_DEFAULT_REGION, AWS_SECRET_ACCESS_KEY

logger = structlog.get_logger(__name__)

try:
    boto_client = boto3.client(
        service_name="translate",
        use_ssl=True,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )
except Exception as e:
    boto_client = None
    logger.error(f"Error {e} occurred instantiating boto3 client.")


def translate(text: str, source_language_code: str, target_language_code: str):
    result = (
        boto_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language_code,
            TargetLanguageCode=target_language_code,
        )
        if boto_client
        else {"TranslatedText": text}
    )

    logger.debug(f"{result=}")

    return result.get("TranslatedText")
