from rest_framework import serializers, status
from dj_rest_auth.registration.serializers import RegisterSerializer

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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class RegistrationSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate_email(self, email):
        email = super().validate_email(email)
        if email == '':
            raise serializers.ValidationError(detail="Email must not be empty.", code=status.HTTP_400_BAD_REQUEST)
        # TODO: Check if email exists (raise error if doesn't)
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
        user.location = self.get_cleaned_data().get('location', '')
        user.save()
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return super().create(validated_data)
