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


def translate(
    text: str, source_language_code: str, target_language_code: str, dry_run=False
) -> str | None:
    if dry_run:
        logger.debug(
            f'Dry run translation of "{text}" from "{source_language_code}" to "{target_language_code}"'
        )
        return text

    if not boto_client:
        logger.error("Machine translation service is not initialized.")
        return None

    if not bool(text):
        logger.error("Text for translation is empty.")
        return None

    try:
        result = boto_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language_code,
            TargetLanguageCode=target_language_code,
        )
        return result.get("TranslatedText")
    except Exception as e:
        logger.error(
            f'Error {e} occurred attempting to translate "{text}" to "{target_language_code}".'
        )

    return None
