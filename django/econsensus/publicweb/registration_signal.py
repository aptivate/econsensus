from custom_organizations.forms import CustomUserSignupRegistrationForm
from registration.signals import user_registered

# we catch the user created signal and add the first_name and last_name
def user_created(sender, user, request, **kwargs):
	form = CustomUserSignupRegistrationForm(request.POST)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
	user.save()

user_registered.connect(user_created)
