import json
import sys


class Languages:
    ARABIC = "ar", "Arabic"
    ENGLISH = "en", "English"
    GERMAN = "de", "German"
    FARSI = "fa", "Farsi"
    TURKISH = "tr", "Turkish"
    RUSSIAN = "ru", "Russian"
    UKRAINIAN = "uk", "Ukrainian"
    KURDISH = "ku", "Kurdish"

    ARMENIAN = "hy", "Armenian"
    BELARUSIAN = "be", "Belarusian"
    CHECHEN = "ce", "Chechen"
    CHINESE = "zh", "Chinese"
    CZECH = "cs", "Czech"
    DARI = "prs", "Dari"
    DUTCH = "nl", "Dutch"
    FRENCH = "fr", "French"
    GEORGIAN = "ka", "Georgian"
    GREEK = "el", "Greek"
    HEBREW = "he", "Hebrew"
    HINDI = "hi", "Hindi"
    ITALIAN = "it", "Italian"
    PASHTO = "ps", "Pashto"
    POLISH = "pl", "Polish"
    PUNJABI = "pa", "Punjabi"
    ROMANY = "rom", "Romany"
    SERBIAN = "sr", "Serbian"
    SOMALI = "so", "Somali"
    SPANISH = "es", "Spanish"
    SWEDISH = "sv", "Swedish"
    URDU = "ur", "Urdu"
    VIETNAMESE = "vi", "Vietnamese"

    OTHER = "ot", "Other"


def getLanguagesFromClass():
    return [
        {
            "model": "data.Language",
            "fields": {
                "iso_code": getattr(Languages, attr)[0],
                "title": getattr(Languages, attr)[1],
            },
        }
        for attr in dir(Languages)
        if attr.isupper()
    ]


def getLanguagesFromFile():
    languages = []
    pk = 0
    with open("languages.txt", "r") as f:
        # Id	Part2b	Part2t	Part1	Scope	Language_Type	Ref_Name	Comment
        for line in f:
            parts = line.split("\t")

            pk += 1
            languages.append(
                {
                    "pk": pk,
                    "model": "data.Language",
                    "fields": {
                        "title": parts[6],
                        "iso_code": parts[3] if parts[3] else parts[0],
                    },
                }
            )

    return languages


if __name__ == "__main__":
    # languages = getLanguagesFromClass()
    languages = getLanguagesFromFile()

    json.dump(languages, sys.stdout, indent=4)
