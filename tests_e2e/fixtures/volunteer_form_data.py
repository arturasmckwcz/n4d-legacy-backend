class ValidVolunteerFormData:
    john_doe = {
        "schedule": [[1, "morning"], [1, "evening"], [3, "afternoon"]],
        "preffered_berlin_locations": ["Friedrichshain", "Tempelhof"],
        "languages": ["en", "de"],
        "activities": ["Playing sports with children"],
        "full_name": "John Doe",
        "phone": "+491234567890",
        "email": "john.doe@example.com",
        "schedule_comments": "Available most weekdays",
        "postal_code": 10115,
        "languages_comments": "Fluent in English, intermediate German",
        "if_good_conduct_certificate": True,
        "if_measles_vaccination": True,
        "activities_comments": "Experienced in coaching youth sports",
        "lead_from": "Website",
        "lead_from_comments": "Found through Google search",
        "translate_languages": ["ru", "tr"],
        "skills": ["Coaching", "First Aid"],
    }


class InvalidVolunteerFormData:
    robin_hood = {
        "schedule": [[1, "morning"], [1, "evening"], [3, "afternoon"]],
        "preffered_berlin_locations": ["Friedrichshain", "Tempelhof"],
        "languages": ["en", "de"],
        "activities": ["Playing sports with children"],
        "full_name": "Robin Hood",
        "schedule_comments": "Available most weekdays",
        "postal_code": 10115,
        "languages_comments": "Fluent in English, intermediate German",
        "if_good_conduct_certificate": True,
        "if_measles_vaccination": True,
        "activities_comments": "Experienced in coaching youth sports",
        "lead_from": "Website",
        "lead_from_comments": "Found through Google search",
        "translate_languages": ["ru", "tr"],
        "skills": ["Coaching", "First Aid"],
    }
