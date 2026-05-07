from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

from .forms import UserRegisterForm, ExpenseForm, BudgetCycleForm, ProfileForm, UserUpdateForm
from .models import Expense, BudgetCycle, Profile


class BudgetContext:
    def __init__(self, user, session):
        today = timezone.localdate() + timezone.timedelta(days = 0)  # ✅ ensure local date is used consistently
        expenses = Expense.objects.filter(user=user)
        budget = BudgetCycle.objects.filter(user=user).first()
        total_expenses = sum((e.amount for e in expenses), Decimal('0'))

        self.today = today
        self.expenses = expenses
        self.budget = budget
        self.total_expenses = total_expenses
        self.exp = total_expenses > 0
        self.has_budget = budget is not None

        if budget:
            remaining_days = (budget.end_date - today).days + 1
            remaining_days = max(remaining_days, 1)

            total_days = (budget.end_date - budget.start_date).days + 1
            remaining_balance = budget.total_amount - total_expenses
            
            
            spent_percentage = (total_expenses / budget.total_amount) * 100
            self.spent_percentage = round(spent_percentage, 1)
            self.exceeeded_80 = spent_percentage >= 80

            # --- Day changed check ---
            last_visited = session.get('last_visited_date')
            if last_visited:
                last_visited_date = timezone.datetime.strptime(last_visited, '%Y-%m-%d').date()
                day_changed = last_visited_date < today
            else:
                day_changed = False

            # --- Update session date FIRST ---
            session['last_visited_date'] = today.strftime('%Y-%m-%d')

            # --- Calculate safe_daily_limit once per day ---
            if day_changed or 'safe_daily_limit' not in session:
                safe_daily_limit = round(remaining_balance / remaining_days, 2)
                session['safe_daily_limit'] = float(safe_daily_limit)
                print(f"Recalculated safe_daily_limit: {safe_daily_limit}")
            else:
                safe_daily_limit = Decimal(str(session['safe_daily_limit']))
                print(f"Using cached safe_daily_limit: {safe_daily_limit}")

            # --- Today's expenses using expense_date field ---
            today_expenses_qs = Expense.objects.filter(
                user=user,
                expense_date=today  # ✅ matches local date saved at creation
            )
            today_total = sum((e.amount for e in today_expenses_qs), Decimal('0'))

            print(f"Today: {today}, Today expenses: {list(today_expenses_qs.values('category', 'amount', 'expense_date'))}")

            remaining_daily_limit = safe_daily_limit - today_total
            if remaining_daily_limit < 0:
                remaining_daily_limit = Decimal('0')

            self.day_changed = day_changed
            self.remaining_days = remaining_days
            self.total_days = total_days
            self.remaining_balance = remaining_balance
            self.safe_daily_limit = safe_daily_limit
            self.today_total = today_total
            self.current_balance = remaining_balance
            self.is_over_today_limit = today_total > safe_daily_limit
            self.remaining_daily_limit = round(remaining_daily_limit, 2)

        else:
            self.day_changed = False
            self.remaining_days = 0
            self.total_days = 0
            self.remaining_balance = Decimal('0')
            self.safe_daily_limit = Decimal('0')
            self.today_total = Decimal('0')
            self.current_balance = Decimal('0')
            self.is_over_today_limit = False
            self.remaining_daily_limit = Decimal('0')
            self.spent_percentage = 0
            self.exceeeded_80 = False
    
            

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items()}




def delete_expense(request, pk):
    expense = get_object_or_404(Expense, id=pk, user=request.user)

    expense.delete()

    return redirect('expenses')


@login_required
def home(request):
    ctx = BudgetContext(request.user, request.session)

    # Day changed logic
    last_visited = request.session.get('last_visited_date')
    if last_visited:
        last_visited_date = timezone.datetime.strptime(last_visited, '%Y-%m-%d').date()
        ctx.day_changed = last_visited_date < ctx.today
    else:
        ctx.day_changed = False

    request.session['last_visited_date'] = ctx.today.strftime('%Y-%m-%d')

    # 80% threshold notification
    # Only show once — track if already notified at this threshold
    already_notified = request.session.get('threshold_80_notified', False)
    if ctx.exceeeded_80 and not already_notified:
        request.session['threshold_80_notified'] = True
        ctx.show_threshold_warning = True
    elif not ctx.exceeeded_80:
        # Reset notification if they go back below 80% (e.g. new cycle)
        request.session['threshold_80_notified'] = False
        ctx.show_threshold_warning = False
    else:
        ctx.show_threshold_warning = False

    # Category data for pie chart
    category_totals = {}
    for e in ctx.expenses:
        category = e.get_category_display()
        if category in category_totals:
            category_totals[category] += float(e.amount)
        else:
            category_totals[category] = float(e.amount)

    result = ctx.as_dict()
    result['category_labels'] = list(category_totals.keys())
    result['category_data'] = list(category_totals.values())

    return render(request, 'users/home.html', result)

@login_required
def expenses(request):
    
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date', '-date')
    ctx = BudgetContext(request.user, request.session)
    category_totals = {}
    for e in expenses:
        category = e.get_category_display()
        if category in category_totals:
            category_totals[category] += float(e.amount)
        else:
            category_totals[category] = float(e.amount)

    return render(request, 'users/expenses.html', {
        'expenses': expenses,
        'has_budget': ctx.has_budget,
        'total_expenses': ctx.total_expenses,
        'category_labels': list(category_totals.keys()),
        'category_data': list(category_totals.values()),
    })





@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        confirmed = request.POST.get('confirmed') == 'true'

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.expense_date = timezone.localdate() + timezone.timedelta(days = 0)  # ✅ ensure local date is used consistently

            ctx = BudgetContext(request.user, request.session)

            if ctx.budget and not confirmed:
                if expense.amount <= 0:
                    form.add_error('amount', 'Expense must be greater than 0')
                    return render(request, 'users/add_expense.html', {'form': form})

                print(f"Adding: {expense.amount}, Remaining Today: {ctx.remaining_daily_limit}")

                if expense.amount > ctx.remaining_daily_limit:
                    return render(request, 'users/add_expense.html', {
                        'form': form,
                        'show_confirm': True,
                        'remaining_today': ctx.remaining_daily_limit,
                        'exceeded_by': round(expense.amount - ctx.remaining_daily_limit, 2),
                    })

            expense.save()
            return redirect('home')

    else:
        form = ExpenseForm()

    return render(request, 'users/add_expense.html', {'form': form})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi {username}, your account was created successfully')
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def setup_budget(request):
    if BudgetCycle.objects.filter(user=request.user).exists():
        return redirect('home')

    if request.method == "POST":
        form = BudgetCycleForm(request.POST)

        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            today = timezone.localdate()

            if budget.total_amount <= 0:
                form.add_error('total_amount', 'Income must be greater than 0')

            if budget.start_date < today:
                form.add_error('start_date', 'Start date cannot be in the past')

            if budget.end_date < today:
                form.add_error('end_date', 'End date cannot be in the past')

            if budget.end_date <= budget.start_date:
                form.add_error('end_date', 'End date must be after start date')

            if form.errors:
                return render(request, 'users/setup_budget.html', {'form': form})

            days = (budget.end_date - budget.start_date).days + 1
            budget.daily_limit = round(budget.total_amount / days, 2)
            print(f"Setting up budget: Total {budget.total_amount}, Days {days}, Daily Limit {budget.daily_limit}")

            request.session.pop('safe_daily_limit', None)
            request.session.pop('last_visited_date', None)

            budget.save()
            return redirect('home')

    else:
        form = BudgetCycleForm()

    return render(request, 'users/setup_budget.html', {'form': form})


# @login_required
# def expenses(request):
#     expenses = Expense.objects.filter(user=request.user)
#     return render(request, 'users/expenses.html', {'expenses': expenses})


@login_required
def delete_budget(request):
    if request.method == "POST":
        BudgetCycle.objects.filter(user=request.user).delete()
        Expense.objects.filter(user=request.user).delete()
        request.session.pop('safe_daily_limit', None)
        request.session.pop('last_visited_date', None)
        messages.success(request, 'Budget cycle deleted successfully')
        return redirect('setup_budget')
    return redirect('home')


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        print("POST HIT")
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        print("USER FORM VALID:", u_form.is_valid())
        print("PROFILE FORM VALID:", p_form.is_valid())

        print("USER ERRORS:", u_form.errors)
        print("PROFILE ERRORS:", p_form.errors)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })