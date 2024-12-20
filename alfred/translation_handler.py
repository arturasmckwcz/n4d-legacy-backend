import boto3

boto_client = boto3.client(
    service_name="translate", region_name="eu-central-1", use_ssl=True
)


def translate(text: str, source_language_code: str, target_language_code: str):
    result = boto_client.translate_text(
        Text="Hello, World", SourceLanguageCode="en", TargetLanguageCode="de"
    )
    print("TranslatedText: " + result.get("TranslatedText"))
    print("SourceLanguageCode: " + result.get("SourceLanguageCode"))
    print("TargetLanguageCode: " + result.get("TargetLanguageCode"))


translate(text="test", source_language_code="a", target_language_code="b")
