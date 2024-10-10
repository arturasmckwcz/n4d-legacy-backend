class ValidVolunteerFormData:
    john_doe = {
        "schedule": [[1, "morning"], [1, "evening"], [3, "afternoon"]],
        "preferred_berlin_locations": ["Friedrichshain", "Tempelhof"],
        "native_languages": ["English", "German"],
        "activities": ["Playing sports with children"],
        "full_name": "John Doe",
        "phone": "+491234567890",
        "email": "john.doe@example.com",
        "postal_code": 10115,
        "if_good_conduct_certificate": True,
        "if_measles_vaccination": True,
        "lead_from": "Website",
        "comments": "Found through Google search",
        "fluent_languages": ["ru", "tr"],
        "skills": ["Coaching", "First Aid"],
    }


class InvalidVolunteerFormData:
    robin_hood = {
        "schedule": [[1, "morning"], [1, "evening"], [3, "afternoon"]],
        "preferred_berlin_locations": ["Friedrichshain", "Tempelhof"],
        "native_languages": ["English", "German"],
        "activities": ["Playing sports with children"],
        "full_name": "Robin Hood",
        "postal_code": 10115,
        "if_good_conduct_certificate": True,
        "if_measles_vaccination": True,
        "lead_from": "Website",
        "comments": "Found through Google search",
        "fluent_languages": ["ru", "tr"],
        "skills": ["Coaching", "First Aid"],
    }
