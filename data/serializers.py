from rest_framework import serializers

from data.models import Person


class DataPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "first_name",
            "middle_name",
            "last_name",
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["date_of_birth"] = (
            instance.date_ofBirth.strftime("%d-%m-%Y")
            if instance.date_of_birth
            else None
        )
        response["user_type"] = instance.user.user_type
        response["avatar"] = instance.avatar.pic
        response["contact_phone"] = instance.contact.phone
        # if a user didn't provide email use the one from credentials
        response["contact_email"] = (
            instance.contact.email if instance.contact.email else instance.user.email
        )
        response["contact_web"] = instance.contact.web
        response["location_street_address"] = instance.location.street_address
        response["location_post_code"] = instance.location.post_code
        response["location_city"] = instance.location.city
        response["location_country"] = instance.location.country

        return response
