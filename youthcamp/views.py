from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from .forms import CustomLoginForm, StaffCreationForm, ParticipantForm, ChurchForm, ExpenseForm, IncomeForm, ActivityForm, VSGameResultForm, SurvivalGameResultForm, DemeritForm, MeritForm
from .models import Participant, Finance, Church, Activity, VSGameResult, SurvivalGameResult, Demerit, Merit

def login_view(request):
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def dashboard_view(request):
    # Get real statistics from database
    total_participants = Participant.objects.count()
    total_youth = Participant.objects.filter(category__iexact='youth').count()
    total_pastors = Participant.objects.filter(category__iexact='pastor').count()
    
    # Get churches from database
    churches = Church.objects.all().order_by('-created_at')
    total_churches = churches.count()
    
    # Get leading church (most recent or first)
    leading_church = churches.first().name if churches.exists() else "No churches registered"
    
    # Calculate finances
    total_income = Finance.objects.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Finance.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    remaining_balance = total_income - total_expenses
    
    context = {
        'total_participants': total_participants,
        'total_youth': total_youth,
        'total_pastors': total_pastors,
        'total_churches': total_churches,
        'churches': churches,
        'leading_church': leading_church,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)

@login_required
def participants_view(request):
    color_filter = request.GET.get('color', '')
    
    if color_filter:
        participants = Participant.objects.filter(color__iexact=color_filter).order_by('-created_at')
    else:
        participants = Participant.objects.all().order_by('-created_at')
    
    # Get all unique colors for filter buttons
    available_colors = Participant.objects.values_list('color', flat=True).distinct().exclude(color='').exclude(color__isnull=True).order_by('color')
    
    # Get all participants for statistics calculation
    all_participants = Participant.objects.all()
    
    return render(request, 'participants.html', {
        'participants': participants, 
        'user': request.user,
        'current_color_filter': color_filter,
        'available_colors': available_colors,
        'all_participants': all_participants
    })

@login_required
def add_participant_view(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()
            
            # Create finance record for registration fee
            Finance.objects.create(
                participant=participant,
                description=f"Registration fee - {participant.name} ({participant.category or 'Custom'})",
                amount=participant.registration_fee,
                transaction_type='income'
            )
            
            messages.success(request, f'Participant "{participant.name}" has been added successfully! Registration fee of ₱{participant.registration_fee} has been recorded.')
            return redirect('finances')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParticipantForm()
    
    return render(request, 'add_participant.html', {'form': form, 'user': request.user})

@login_required
def edit_participant_view(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            updated_participant = form.save()
            
            # Update finance record if registration fee changed
            if participant.registration_fee != updated_participant.registration_fee:
                finance_record = Finance.objects.filter(participant=participant, transaction_type='income').first()
                if finance_record:
                    finance_record.amount = updated_participant.registration_fee
                    finance_record.description = f"Registration fee - {updated_participant.name} ({updated_participant.category or 'Custom'})"
                    finance_record.save()
            
            messages.success(request, f'Participant "{updated_participant.name}" has been updated successfully!')
            return redirect('participants')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParticipantForm(instance=participant)
    
    return render(request, 'edit_participant.html', {'form': form, 'participant': participant, 'user': request.user})

@login_required
def churches_view(request):
    churches = Church.objects.all().order_by('-created_at')
    return render(request, 'churches.html', {'churches': churches, 'user': request.user})

@login_required
def add_church_view(request):
    if request.method == 'POST':
        form = ChurchForm(request.POST)
        if form.is_valid():
            church = form.save()
            messages.success(request, f'Church "{church.name}" has been added successfully!')
            return redirect('churches')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChurchForm()
    
    return render(request, 'add_church.html', {'form': form, 'user': request.user})

@login_required
def delete_participant_view(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    if request.method == 'POST':
        try:
            participant_name = participant.name
            participant.delete()
            messages.success(request, f'Participant "{participant_name}" has been deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting participant: {str(e)}')
        
        return redirect('participants')
    
    return render(request, 'delete_participant.html', {'participant': participant, 'user': request.user})

@login_required
def church_members_view(request, church_id):
    church = get_object_or_404(Church, id=church_id)
    members = Participant.objects.filter(church=church).order_by('name')
    
    # Calculate statistics
    youth_count = members.filter(category__iexact='youth').count()
    pastor_count = members.filter(category__iexact='pastor').count()
    total_fees = sum(member.registration_fee for member in members if member.registration_fee)
    
    context = {
        'church': church,
        'members': members,
        'youth_count': youth_count,
        'pastor_count': pastor_count,
        'total_fees': total_fees,
        'user': request.user,
    }
    return render(request, 'church_members.html', context)

@login_required
def delete_finance_view(request, finance_id):
    finance = get_object_or_404(Finance, id=finance_id)
    
    if request.method == 'POST':
        try:
            finance_type = finance.transaction_type
            finance_description = finance.description
            finance_amount = finance.amount
            finance.delete()
            messages.success(request, f'{finance_type.title()} record "{finance_description}" of ₱{finance_amount} has been deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting record: {str(e)}')
        
        return redirect('finances')
    
    return render(request, 'delete_finance.html', {'finance': finance, 'user': request.user})

@login_required
def edit_finance_view(request, finance_id):
    finance = get_object_or_404(Finance, id=finance_id)
    
    if request.method == 'POST':
        if finance.transaction_type == 'expense':
            form = ExpenseForm(request.POST, instance=finance)
        else:
            form = IncomeForm(request.POST, instance=finance)
        
        if form.is_valid():
            try:
                # For IncomeForm, the save method handles all the logic
                form.save()
                messages.success(request, f'{finance.transaction_type.title()} record has been updated successfully.')
                return redirect('finances')
            except Exception as e:
                messages.error(request, f'Error updating record: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        if finance.transaction_type == 'expense':
            form = ExpenseForm(instance=finance)
        else:
            form = IncomeForm(instance=finance)
            # Pre-populate recorded_by if not set
            if not finance.recorded_by:
                form.initial['recorded_by'] = request.user.get_full_name() or request.user.username
    
    context = {
        'form': form,
        'finance': finance,
        'user': request.user,
    }
    return render(request, 'edit_finance.html', context)

@login_required
def activities_view(request):
    # Get all activities
    activities = Activity.objects.all().order_by('-created_at')
    
    # Get VS game results
    vs_games = VSGameResult.objects.all().order_by('-created_at')
    
    # Get survival game results
    survival_results = SurvivalGameResult.objects.all()
    
    # Calculate automatic rankings based on final score
    survival_results_with_rank = []
    all_survival_results = list(survival_results)
    
    # Sort by final score (descending) for ranking
    sorted_by_final_score = sorted(all_survival_results, key=lambda x: x.final_score, reverse=True)
    
    # Assign ranks
    rank_dict = {}
    current_rank = 1
    for i, result in enumerate(sorted_by_final_score):
        if i > 0 and result.final_score < sorted_by_final_score[i-1].final_score:
            current_rank = i + 1
        rank_dict[result.id] = current_rank
    
    # Update rank for each result and sort by rank for display
    for result in all_survival_results:
        result.calculated_rank = rank_dict[result.id]
        survival_results_with_rank.append(result)
    
    # Sort by rank for display
    survival_results_with_rank.sort(key=lambda x: x.calculated_rank)
    
    # Handle display toggle for VS games
    if request.method == 'POST' and 'toggle_vs_display' in request.POST:
        game_id = request.POST.get('game_id')
        if game_id:
            game = VSGameResult.objects.get(id=game_id)
            game.display_in_scoring = not game.display_in_scoring
            game.save()
            status = "displayed" if game.display_in_scoring else "hidden"
            messages.success(request, f'VS Game result {status} in Admin Scoring System.')
            return redirect('activities')
    
    # Handle display toggle for survival games
    if request.method == 'POST' and 'toggle_survival_display' in request.POST:
        result_id = request.POST.get('result_id')
        if result_id:
            result = SurvivalGameResult.objects.get(id=result_id)
            result.display_in_scoring = not result.display_in_scoring
            result.save()
            status = "displayed" if result.display_in_scoring else "hidden"
            messages.success(request, f'Survival Game result {status} in Admin Scoring System.')
            return redirect('activities')
    
    # Handle activity creation
    if request.method == 'POST':
        if 'create_activity' in request.POST:
            activity_form = ActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.created_by = request.user
                activity.save()
                messages.success(request, f'Activity "{activity.name}" created successfully!')
                return redirect('activities')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            activity_form = ActivityForm()
    else:
        activity_form = ActivityForm()
    
    # Handle VS game result creation
    if request.method == 'POST' and 'create_vs_result' in request.POST:
        vs_form = VSGameResultForm(request.POST)
        if vs_form.is_valid():
            vs_result = vs_form.save()
            messages.success(request, 'VS Game result saved successfully!')
            return redirect('activities')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        vs_form = VSGameResultForm()
    
    # Handle survival game result creation
    if request.method == 'POST' and 'create_survival_result' in request.POST:
        survival_form = SurvivalGameResultForm(request.POST)
        if survival_form.is_valid():
            survival_result = survival_form.save()
            messages.success(request, 'Survival game result saved successfully!')
            return redirect('activities')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        survival_form = SurvivalGameResultForm()
    
    # Handle demerit creation
    if request.method == 'POST' and 'add_demerit' in request.POST:
        result_id = request.POST.get('survival_result_id')
        if result_id:
            survival_result = get_object_or_404(SurvivalGameResult, id=result_id)
            demerit_form = DemeritForm(request.POST)
            if demerit_form.is_valid():
                demerit = demerit_form.save(
                    survival_result=survival_result,
                    recorded_by=request.user
                )
                messages.success(request, f'Demerit of {demerit.points} points added successfully!')
                return redirect('activities')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            demerit_form = DemeritForm()
    else:
        demerit_form = DemeritForm()
    
    # Handle merit creation
    if request.method == 'POST' and 'add_merit' in request.POST:
        result_id = request.POST.get('survival_result_id')
        if result_id:
            survival_result = get_object_or_404(SurvivalGameResult, id=result_id)
            merit_form = MeritForm(request.POST)
            if merit_form.is_valid():
                merit = merit_form.save(
                    survival_result=survival_result,
                    recorded_by=request.user
                )
                messages.success(request, f'Merit of {merit.points} points added successfully!')
                return redirect('activities')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            merit_form = MeritForm()
    else:
        merit_form = MeritForm()
    
    context = {
        'activities': activities,
        'vs_games': vs_games,
        'survival_results': survival_results_with_rank,
        'activity_form': activity_form,
        'vs_form': vs_form,
        'survival_form': survival_form,
        'demerit_form': demerit_form,
        'merit_form': merit_form,
        'user': request.user,
    }
    return render(request, 'activities.html', context)


# VS Game Edit and Delete Views
@login_required
def edit_vs_game_view(request, game_id):
    # Only staff or admin can edit
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit game results.')
        return redirect('activities')
    
    game = get_object_or_404(VSGameResult, id=game_id)
    
    if request.method == 'POST':
        form = VSGameResultForm(request.POST, instance=game)
        if form.is_valid():
            updated_game = form.save()
            messages.success(request, f'VS Game result for "{updated_game.activity.game_type.title}" has been updated successfully!')
            return redirect('activities')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VSGameResultForm(instance=game)
    
    return render(request, 'edit_vs_game.html', {'form': form, 'game': game, 'user': request.user})


@login_required
def delete_vs_game_view(request, game_id):
    # Only staff or admin can delete
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete game results.')
        return redirect('activities')
    
    game = get_object_or_404(VSGameResult, id=game_id)
    
    if request.method == 'POST':
        activity_name = game.activity.game_type.title
        match_name = f"{game.church_a.name} VS {game.church_b.name}"
        game.delete()
        messages.success(request, f'VS Game result "{match_name}" for "{activity_name}" has been deleted successfully!')
        return redirect('activities')
    
    return render(request, 'delete_vs_game.html', {'game': game, 'user': request.user})


# Survival Game Edit and Delete Views
@login_required
def edit_survival_game_view(request, result_id):
    # Only staff or admin can edit
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit game results.')
        return redirect('activities')
    
    result = get_object_or_404(SurvivalGameResult, id=result_id)
    
    if request.method == 'POST':
        form = SurvivalGameResultForm(request.POST, instance=result)
        if form.is_valid():
            updated_result = form.save()
            messages.success(request, f'Survival Game result for "{updated_result.activity.game_type.title}" has been updated successfully!')
            return redirect('activities')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SurvivalGameResultForm(instance=result)
    
    return render(request, 'edit_survival_game.html', {'form': form, 'result': result, 'user': request.user})


@login_required
def delete_survival_game_view(request, result_id):
    # Only staff or admin can delete
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete game results.')
        return redirect('activities')
    
    result = get_object_or_404(SurvivalGameResult, id=result_id)
    
    if request.method == 'POST':
        activity_name = result.activity.game_type.title
        church_name = result.church.name
        result.delete()
        messages.success(request, f'Survival Game result for "{church_name}" in "{activity_name}" has been deleted successfully!')
        return redirect('activities')
    
    return render(request, 'delete_survival_game.html', {'result': result, 'user': request.user})

@login_required
def participants_api_view(request):
    """API endpoint for participant autocomplete"""
    query = request.GET.get('q', '').strip()
    participants = []
    
    if query and len(query) >= 2:
        # Search participants by name (case-insensitive)
        participant_list = Participant.objects.filter(
            name__icontains=query
        ).order_by('name')[:10]  # Limit to 10 results
        
        participants = [
            {
                'id': p.id,
                'name': p.name,
                'age': p.age,
                'category': p.category or 'Custom'
            }
            for p in participant_list
        ]
    
    return JsonResponse({'participants': participants})

@login_required
def finances_view(request):
    finance_records = Finance.objects.all().order_by('-created_at')
    total_income = Finance.objects.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Finance.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    remaining_balance = total_income - total_expenses
    
    # Handle expense form submission
    expense_form = ExpenseForm()
    income_form = IncomeForm()
    
    if request.method == 'POST':
        if 'add_expense' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense = expense_form.save(commit=False)
                expense.recorded_by = request.user
                expense.save()
                messages.success(request, f'Expense "{expense.description}" of ₱{expense.amount} has been recorded.')
                return redirect('finances')
        elif 'add_income' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income = income_form.save(commit=False)
                income.recorded_by = request.user
                income.save()
                messages.success(request, f'Income "{income.description}" of ₱{income.amount} has been recorded.')
                return redirect('finances')
    
    context = {
        'finance_records': finance_records,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'expense_form': expense_form,
        'income_form': income_form,
        'user': request.user,
    }
    return render(request, 'finances.html', context)

@login_required
def demerit_details_view(request, survival_result_id):
    """View detailed demerit history for a specific survival result"""
    survival_result = get_object_or_404(SurvivalGameResult, id=survival_result_id)
    demerits = Demerit.objects.filter(survival_result=survival_result).order_by('-created_at')
    
    context = {
        'survival_result': survival_result,
        'demerits': demerits,
        'user': request.user,
    }
    return render(request, 'demerit_details.html', context)

@login_required
def merit_details_view(request, survival_result_id):
    """View detailed merit history for a specific survival result"""
    survival_result = get_object_or_404(SurvivalGameResult, id=survival_result_id)
    merits = Merit.objects.filter(survival_result=survival_result).order_by('-created_at')
    
    context = {
        'survival_result': survival_result,
        'merits': merits,
        'user': request.user,
    }
    return render(request, 'merit_details.html', context)

@login_required
def admin_scoring_view(request):
    # Get only results marked for display in Admin Scoring System
    vs_games = VSGameResult.objects.filter(display_in_scoring=True).order_by('-created_at')
    survival_results = SurvivalGameResult.objects.filter(display_in_scoring=True)
    
    # Calculate automatic rankings based on final score for admin scoring
    survival_results_with_rank = []
    all_survival_results = list(survival_results)
    
    # Sort by final score (descending) for ranking
    sorted_by_final_score = sorted(all_survival_results, key=lambda x: x.final_score, reverse=True)
    
    # Assign ranks
    rank_dict = {}
    current_rank = 1
    for i, result in enumerate(sorted_by_final_score):
        if i > 0 and result.final_score < sorted_by_final_score[i-1].final_score:
            current_rank = i + 1
        rank_dict[result.id] = current_rank
    
    # Update rank for each result and sort by rank for display
    for result in all_survival_results:
        result.calculated_rank = rank_dict[result.id]
        survival_results_with_rank.append(result)
    
    # Sort by rank for display
    survival_results_with_rank.sort(key=lambda x: x.calculated_rank)
    
    context = {
        'vs_games': vs_games,
        'survival_results': survival_results_with_rank,
        'user': request.user,
    }
    return render(request, 'admin_scoring.html', context)

# Staff Management Views
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin)
def staff_management_view(request):
    staff_users = User.objects.filter(is_staff=True).order_by('username')
    context = {
        'staff_users': staff_users,
        'user': request.user,
    }
    return render(request, 'staff_management.html', context)

@login_required
@user_passes_test(is_admin)
def add_staff_view(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Staff user "{user.username}" has been created successfully!')
            return redirect('staff_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffCreationForm()
    
    return render(request, 'add_staff.html', {'form': form, 'user': request.user})

@login_required
@user_passes_test(is_admin)
def delete_staff_view(request, staff_id):
    staff_user = get_object_or_404(User, id=staff_id, is_staff=True)
    
    # Prevent deletion of superusers
    if staff_user.is_superuser:
        messages.error(request, 'Cannot delete superuser accounts.')
        return redirect('staff_management')
    
    # Prevent self-deletion
    if staff_user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('staff_management')
    
    if request.method == 'POST':
        username = staff_user.username
        staff_user.delete()
        messages.success(request, f'Staff user "{username}" has been deleted successfully!')
        return redirect('staff_management')
    
    return render(request, 'delete_staff.html', {'staff_user': staff_user, 'user': request.user})
