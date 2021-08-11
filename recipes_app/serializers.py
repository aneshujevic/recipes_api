import json

import requests
from rest_framework import serializers, status
from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
import clearbit

import recipes_api.settings
from recipes_app.models import Recipe, Ingredient, UserProfile


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
        fields = '__all__'
        read_only_fields = ['rating', 'number_of_ratings', 'owner']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserProfileSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        model = UserProfile
        fields = (*UserDetailsSerializer.Meta.fields, 'location', 'time_zone', 'city', 'employment')
        extra_kwargs = {'password': {'write_only': True}, 'location': {'write_only': True}}


class RegistrationSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate_email(self, email):
        email = super().validate_email(email)
        if email == '':
            raise serializers.ValidationError(detail="Email must not be empty.", code=status.HTTP_400_BAD_REQUEST)
        if not email_is_trustworthy(email):
            raise serializers.ValidationError(detail="Email must not be empty.", code=status.HTTP_400_BAD_REQUEST)
        return email

    def get_cleaned_data(self):
        cleaned_data = super().get_cleaned_data()
        return {
            **cleaned_data,
            'location': self.validated_data.get('location', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', '')
        }

    def save(self, request):
        user = super().save(request)
        additional_user_info = {}
        additional_user_info = get_user_data_clearbit(user.email)
        user.location = additional_user_info.get('location', None)
        user.time_zone = additional_user_info.get('time_zone', None)
        user.city = additional_user_info.get('city', None)
        user.employment = additional_user_info.get('employment', None)
        user.save()
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return super().create(validated_data)


def email_is_trustworthy(email):
    try:
        hunter_check_url = recipes_api.settings.HUNTER_URL.format(email, recipes_api.settings.HUNTER_API_KEY)
        response = requests.get(hunter_check_url)
        json_data = json.loads(response.text)['data']
        score = int(json_data['score'])

        # For the simplicity sake and limits by hunter.io only parameter considered is the score
        if score >= 50:
            return True
        return False
    except json.decoder.JSONDecodeError:
        print("Potroseno 25 zahteva :(")
        return True


def get_user_data_clearbit(email):
    clearbit.key = recipes_api.settings.CLEARBIT_API_KEY
    data = {}
    try:
        response = clearbit.Enrichment.find(email=email, stream=True).get['person']
        data['location'] = response['location']
        data['time_zone'] = response['timeZone']
        data['city'] = response['geo']['city']
        data['employment'] = response['employment']['title']
    except TypeError:
        print("No info on clearbit.")
    except requests.exceptions.HTTPError:
        print("Invalid email.")
    except AttributeError:
        print("Couldn't create a object of type clearbit.")
    return data

