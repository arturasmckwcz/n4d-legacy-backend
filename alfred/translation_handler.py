import boto3

from alfred.settings import AWS_ACCESS_KEY_ID, AWS_DEFAULT_REGION, AWS_SECRET_ACCESS_KEY

boto_client = boto3.client(
    service_name="translate",
    use_ssl=True,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)


def translate(text: str, source_language_code: str, target_language_code: str):
    result = boto_client.translate_text(
        Text=text,
        SourceLanguageCode=source_language_code,
        TargetLanguageCode=target_language_code,
    )

    return result.get("TranslatedText")
