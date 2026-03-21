from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Participant, Church, Finance, Activity, VSGameResult, SurvivalGameResult, Demerit, Merit

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or Email'
        self.error_messages['invalid_login'] = 'Please enter a correct username and password. Note that both fields may be case-sensitive.'

class StaffCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        if commit:
            user.save()
        return user

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'age', 'type_of_ministry', 'status', 'category', 'church', 'registration_fee', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter participant name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age',
                'min': '1',
                'max': '120'
            }),
            'type_of_ministry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select or type ministry',
                'list': 'ministry-list'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select or type category',
                'list': 'category-list'
            }),
            'church': forms.Select(attrs={
                'class': 'form-control'
            }),
            'registration_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration fee',
                'step': '0.01',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter color (e.g., red, blue, #FF0000)',
                'title': 'Enter color name or hex code (e.g., red, blue, green, yellow, orange, purple, white, pink)',
                'list': 'color-list',
                'style': 'width: 200px;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Name'
        self.fields['age'].label = 'Age'
        self.fields['type_of_ministry'].label = 'Type of Ministry'
        self.fields['status'].label = 'Status'
        self.fields['category'].label = 'Category'
        self.fields['church'].label = 'Church'
        self.fields['registration_fee'].label = 'Registration Fee'
        self.fields['color'].label = 'Color'
        
        # Add color datalist to form
        self.color_choices = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'white', 'pink']
        
        # Populate church choices
        from .models import Church
        church_choices = [('', '-- Select Church --')]
        church_choices.extend([(church.id, church.name) for church in Church.objects.all()])
        self.fields['church'].choices = church_choices
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise ValidationError('Age must be between 1 and 120.')
        return age
    
    def clean_color(self):
        color = self.cleaned_data.get('color', '').strip().lower()
        
        # Define valid colors
        valid_colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'white', 'pink']
        
        # Check if it's a valid color name
        if color in valid_colors:
            return color
        
        # Check if it's a valid hex color
        if color.startswith('#') and len(color) in [4, 7]:  # #RGB or #RRGGBB
            return color.lower()
        
        # If not valid, raise validation error
        raise ValidationError(
            f'Invalid color. Please enter one of: {", ".join(valid_colors)} or a valid hex color code (e.g., #FF0000).'
        )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name.strip()
    
    def clean_registration_fee(self):
        registration_fee = self.cleaned_data.get('registration_fee')
        if registration_fee is None:
            raise ValidationError('Registration fee is required.')
        if registration_fee < 0:
            raise ValidationError('Registration fee cannot be negative.')
        if registration_fee > 999999.99:
            raise ValidationError('Registration fee is too high.')
        return registration_fee

class ChurchForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = ['name', 'host_pastor']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter church name'
            }),
            'host_pastor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter host pastor name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Name of Church'
        self.fields['host_pastor'].label = 'Host Pastor'
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise ValidationError('Church name must be at least 2 characters long.')
        return name.strip()
    
    def clean_host_pastor(self):
        host_pastor = self.cleaned_data.get('host_pastor')
        if host_pastor and len(host_pastor.strip()) < 2:
            raise ValidationError('Host pastor name must be at least 2 characters long.')
        return host_pastor.strip()

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['description', 'amount', 'expense_category']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter expense description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter expense amount',
                'step': '0.01',
                'min': '0.01'
            }),
            'expense_category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = 'Expense Description'
        self.fields['amount'].label = 'Amount'
        self.fields['expense_category'].label = 'Category'
        # Set transaction_type to expense by default
        self.initial['transaction_type'] = 'expense'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError('Amount is required.')
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0.')
        if amount > 999999.99:
            raise ValidationError('Amount is too high.')
        return amount
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 2:
            raise ValidationError('Description must be at least 2 characters long.')
        return description.strip()
    
    def save(self, commit=True):
        expense = super().save(commit=False)
        expense.transaction_type = 'expense'
        if commit:
            expense.save()
        return expense

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'activity_type', 'game_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter activity name'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'activity_type_select'
            }),
            'game_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select game type'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter activity description (optional)',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Activity Name'
        self.fields['activity_type'].label = 'Activity Type'
        self.fields['game_type'].label = 'Game Type'
        self.fields['description'].label = 'Description'

class VSGameResultForm(forms.ModelForm):
    class Meta:
        model = VSGameResult
        fields = ['activity', 'church_a', 'church_b', 'church_a_score', 'church_b_score', 'winner']
        widgets = {
            'activity': forms.Select(attrs={
                'class': 'form-control'
            }),
            'church_a': forms.Select(attrs={
                'class': 'form-control'
            }),
            'church_b': forms.Select(attrs={
                'class': 'form-control'
            }),
            'church_a_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Team A Score',
                'min': '0'
            }),
            'church_b_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Team B Score',
                'min': '0'
            }),
            'winner': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity'].label = 'Activity'
        self.fields['church_a'].label = 'Church A (Team A)'
        self.fields['church_b'].label = 'Church B (Team B)'
        self.fields['church_a_score'].label = 'Church A Score'
        self.fields['church_b_score'].label = 'Church B Score'
        self.fields['winner'].label = 'Winner'
        
        # Filter churches for dropdown
        self.fields['church_a'].queryset = Church.objects.all()
        self.fields['church_b'].queryset = Church.objects.all()
        
        # Filter activities for dropdown (only VS sports games)
        self.fields['activity'].queryset = Activity.objects.filter(activity_type='vs_sports')

class SurvivalGameResultForm(forms.ModelForm):
    class Meta:
        model = SurvivalGameResult
        fields = ['activity', 'church', 'points_earned', 'rank']
        widgets = {
            'activity': forms.Select(attrs={
                'class': 'form-control'
            }),
            'church': forms.Select(attrs={
                'class': 'form-control'
            }),
            'points_earned': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Points Earned',
                'min': '0'
            }),
            'rank': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rank (optional)',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity'].label = 'Activity'
        self.fields['church'].label = 'Church'
        self.fields['points_earned'].label = 'Points Earned'
        self.fields['rank'].label = 'Rank'
        
        # Filter churches for dropdown
        self.fields['church'].queryset = Church.objects.all()
        
        # Filter activities for dropdown (only survival games)
        self.fields['activity'].queryset = Activity.objects.filter(activity_type='survival')

class DemeritForm(forms.ModelForm):
    class Meta:
        model = Demerit
        fields = ['points', 'violation_type', 'reason']
        widgets = {
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Demerit Points',
                'min': '0'
            }),
            'violation_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional reason for violation (optional)',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['points'].label = 'Demerit Points'
        self.fields['violation_type'].label = 'Violation Type'
        self.fields['reason'].label = 'Reason (Optional)'
    
    def clean_points(self):
        points = self.cleaned_data.get('points')
        if points and points < 0:
            raise ValidationError('Demerit points cannot be negative.')
        return points
    
    def save(self, commit=True, survival_result=None, recorded_by=None):
        demerit = super().save(commit=False)
        if survival_result:
            demerit.survival_result = survival_result
        if recorded_by:
            demerit.recorded_by = recorded_by
        if commit:
            demerit.save()
        return demerit

class MeritForm(forms.ModelForm):
    class Meta:
        model = Merit
        fields = ['points', 'merit_type', 'reason']
        widgets = {
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Merit Points',
                'min': '0'
            }),
            'merit_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional reason for merit (optional)',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['points'].label = 'Merit Points'
        self.fields['merit_type'].label = 'Merit Type'
        self.fields['reason'].label = 'Reason (Optional)'
    
    def clean_points(self):
        points = self.cleaned_data.get('points')
        if points and points < 0:
            raise ValidationError('Merit points cannot be negative.')
        return points
    
    def save(self, commit=True, survival_result=None, recorded_by=None):
        merit = super().save(commit=False)
        if survival_result:
            merit.survival_result = survival_result
        if recorded_by:
            merit.recorded_by = recorded_by
        if commit:
            merit.save()
        return merit

class IncomeForm(forms.ModelForm):
    # Override participant field to use CharField instead of ForeignKey
    participant_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter participant name'
        })
    )
    
    recorded_by_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter recorded by name'
        })
    )
    
    class Meta:
        model = Finance
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter income description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter income amount',
                'step': '0.01',
                'min': '0.01'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = 'Income Description'
        self.fields['amount'].label = 'Amount'
        self.fields['participant_name'].label = 'Participant'
        self.fields['recorded_by_name'].label = 'Recorded By'
        
        # Pre-populate fields with existing data if editing
        if self.instance and self.instance.pk:
            if self.instance.participant:
                self.initial['participant_name'] = self.instance.participant.name
            if self.instance.recorded_by:
                self.initial['recorded_by_name'] = self.instance.recorded_by.get_full_name() or self.instance.recorded_by.username
            else:
                self.initial['recorded_by_name'] = 'System'
        
        # Set transaction_type to income by default
        self.initial['transaction_type'] = 'income'
    
    def save(self, commit=True):
        income = super().save(commit=False)
        income.transaction_type = 'income'
        
        # Handle participant_name field
        participant_name = self.cleaned_data.get('participant_name', '').strip()
        if participant_name:
            # Try to find existing participant by name
            participant = Participant.objects.filter(name__iexact=participant_name).first()
            if not participant:
                # Create new participant if not found with required defaults
                participant = Participant.objects.create(
                    name=participant_name,
                    age=18,  # Default value
                    type_of_ministry='',  # Default empty
                    status='single',  # Default value
                    category='youth',  # Default value
                    registration_fee=100.00,  # Default value
                )
            income.participant = participant
        else:
            income.participant = None
        
        # Handle recorded_by_name field
        recorded_by_name = self.cleaned_data.get('recorded_by_name', '').strip()
        if recorded_by_name and recorded_by_name.lower() != 'system':
            # Try to find existing user by name or username
            from django.contrib.auth.models import User
            from django.db import models
            user = User.objects.filter(
                models.Q(username__iexact=recorded_by_name) |
                models.Q(first_name__iexact=recorded_by_name.split()[0] if ' ' in recorded_by_name else recorded_by_name) &
                models.Q(last_name__iexact=' '.join(recorded_by_name.split()[1:]) if ' ' in recorded_by_name else models.Q(last_name=''))
            ).first()
            if user:
                income.recorded_by = user
            else:
                income.recorded_by = None
        else:
            income.recorded_by = None
        
        if commit:
            income.save()
        return income
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0.')
        return amount
    
    def clean_participant_name(self):
        participant_name = self.cleaned_data.get('participant_name', '').strip()
        return participant_name
    
    def clean_recorded_by_name(self):
        recorded_by_name = self.cleaned_data.get('recorded_by_name', '').strip()
        return recorded_by_name
