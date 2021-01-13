from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.db.models import Sum, Count
from .models import MealVoucherInput, MealVoucherWarehouse, MonthOfIssue, EmployeeInput, Distribution
from .forms import MealVoucherAddForm, MonthOfIssueInputForm, EmployeeAddForm


import psycopg2
import environ

# Django Environ initialization (to keep passwords to the database secret)
env = environ.Env()
environ.Env.read_env()


def delete_employee(request, pk):
    """
    View that enables to delete an employee
    """
    EmployeeInput.objects.filter(id=pk).delete()
    return redirect('/add_employees/')


def restore_warehouse(request):
    """
    View that enables to restore warehouse as it was before distribution
    """
    conn = psycopg2.connect(dbname=env("DATABASE_NAME"), user=env("DATABASE_USER"),
                            password=env("DATABASE_PASSWORD"))
    cur = conn.cursor()
    cur.execute("CALL backup_restore();")
    conn.commit()
    return redirect('/add_mealvouchers/')


def distribute_mealvouchers(request):
    """
    Enables to set claims for meal vouchers to particular employees
    """
    # Nastavení formuláře, aby přepisoval jednu stávající hodnotu z dabáze
    # https://stackoverflow.com/questions/2890038/django-forms-overwrite-data-when-saved
    month_to_update = MonthOfIssue.objects.get(pk=1)
    month = {'mesic_vydani': month_to_update.mesic_vydani}

    # VOUCHER ADD FORM
    if request.method == 'POST':
        input_month_code_form = MonthOfIssueInputForm(request.POST, instance=month_to_update)
        if input_month_code_form.is_valid():
            month_code_input = input_month_code_form.save(commit=False)
            month_code_input.save()
            # Spuštění procedury po kliknutí na tlačítko submit ve formuláři
            conn = psycopg2.connect(dbname=env("DATABASE_NAME"), user=env("DATABASE_USER"),
                                    password=env("DATABASE_PASSWORD"))
            cur = conn.cursor()
            cur.execute("CALL distribute_mealvouchers21();")
            conn.commit()
            # Make the input field blank after submitting the form
            return redirect('/distribute_mealvouchers/')
    else:
        input_month_code_form = MonthOfIssueInputForm()

    employee_claims_overview = EmployeeInput.objects.all().order_by('prijmeni')
    # Vypsání agregovaných sum u jednotlivých zaměstnanců
    # 'https://simpleisbetterthancomplex.com/tutorial/2016/12/06/how-to-create-group-by-queries.html'

    claims_fullfilments = Distribution.objects.values('prijmeni', 'jmeno','narok_v_mesici', 'chyba_distribuce').annotate(
        sum_hodnota=Sum('suma')).order_by('prijmeni').filter(**month).filter(chyba_distribuce='N').filter(narok_v_mesici__gt=0)

    claims_fullfilments_errors = Distribution.objects.values('prijmeni', 'narok_v_mesici').annotate(
        sum_hodnota=Sum('suma')).order_by('prijmeni').filter(**month).distinct().filter(chyba_distribuce='A')


    distribution = Distribution.objects.values('prijmeni', 'jmeno', 'hodnota').annotate(
        sum_kvantita=Sum('kvantita')).order_by('prijmeni', 'hodnota').filter(**month).filter(chyba_distribuce='N').filter(narok_v_mesici__gt=0)

    distribution_sum = Distribution.objects.all().filter(**month).aggregate(total_sum=Sum('suma'))
    meal_vouchers_counts = Distribution.objects.values('hodnota').filter(**month).annotate(
        sum_kvantita=Sum('kvantita'), sum_suma=Sum('suma'))

    total_employees = EmployeeInput.objects.all().aggregate(prijmeni__count=Count('prijmeni'))
    employees_without_claim = EmployeeInput.objects.all().filter(narok='0').count()
    employees_with_claim = int(int(total_employees['prijmeni__count']) - int(employees_without_claim))
    employees_claims_sum = EmployeeInput.objects.all().aggregate(claims_total=Sum('narok'))
    employees_distributed_count = Distribution.objects.values('prijmeni', 'narok_v_mesici', 'chyba_distribuce').distinct().filter(
        **month).filter(chyba_distribuce='N').filter(narok_v_mesici__gt=0)
    # .distinct() umožní počítat pouze unikántí záznamy
    # funguje pouze ve spojení s objects.values() nikoliv s objects.all()

    context = {
        'input_month_code_form': input_month_code_form,
        'employee_claims_overview': employee_claims_overview,
        'claims_fullfilments': claims_fullfilments,
        'distribution': distribution,
        'month_to_update': month_to_update,
        'distribution_sum': distribution_sum,
        'meal_vouchers_counts': meal_vouchers_counts,
        'total_employees': total_employees,
        'employees_without_claim': employees_without_claim,
        'employees_with_claim': employees_with_claim,
        'employees_claims_sum': employees_claims_sum,
        'employees_distributed_count': employees_distributed_count,
        'claims_fullfilments_errors': claims_fullfilments_errors,
    }
    return render(request, 'distribute_mealvouchers/distribute_mealvouchers.html', context)


def add_employees(request):
    """
    Voucher-add-function using Django Forms
    """
    if request.method == 'POST':
        add_employee_form = EmployeeAddForm(request.POST)
        if add_employee_form.is_valid():
            employee_add = add_employee_form.save(commit=False)
            employee_add.save()
            # Make the input field blank after submitting the form
            return redirect('/add_employees/')
    else:
        add_employee_form = EmployeeAddForm()

    EmployeeFormSet = modelformset_factory(
        EmployeeInput,
        extra=0,
        fields=('jmeno', 'prijmeni', 'zavod', 'narok'))
    if request.method == 'POST':
        formset = EmployeeFormSet(request.POST)
        if formset.is_valid():
            # employee_claim_add = formset.save(commit=False)
            # employee_claim_add.save()
            formset.save()
        vouchers = formset.save()
        # Make the input field blank after submitting the form
        return redirect('/add_employees/')
    else:
        formset = EmployeeFormSet()

    employees = EmployeeInput.objects.all().order_by('prijmeni')

    context = {
        'employees': employees,
        'form_add_employee': add_employee_form,
        'formset': formset
    }

    return render(request, 'add_employees/add_employees.html', context)


def remove_mealvouchers(request):
    """
    Enables a removal of particular meal vouchers from the warehouse system
    """
    # Variable that enables the form to update record instead of adding new one
    mealvoucher_to_update = MealVoucherInput.objects.get(pk=1)

    # Voucher Remove Form
    if request.method == 'POST':
        remove_mealvoucher_form = MealVoucherAddForm(request.POST, instance=mealvoucher_to_update)
        if remove_mealvoucher_form.is_valid():
            vouchers_to_remove = remove_mealvoucher_form.save(commit=False)
            vouchers_to_remove.save()
            # Procedure to call related to the form submit button
            # The procedure will make quantitative changes in mealvouchers warehouse
            conn = psycopg2.connect(dbname=env("DATABASE_NAME"), user=env("DATABASE_USER"),
                                    password=env("DATABASE_PASSWORD"))
            cur = conn.cursor()
            cur.execute("CALL remove_mealvoucher();")
            conn.commit()
            # Make the input field blank after submitting the form
            return redirect('/remove_mealvouchers/')
    else:
        remove_mealvoucher_form = MealVoucherAddForm()

    # variable different from the variable connected to the form
    mealvouchers_warehouse = MealVoucherWarehouse.objects.all().order_by('hodnota')
    context = {
        'remove_mealvoucher_form': remove_mealvoucher_form,
        'mealvouchers_warehouse': mealvouchers_warehouse,
    }
    return render(request, 'remove_mealvouchers/remove_mealvouchers.html', context)


def add_mealvouchers(request):
    """
    Enables to add meal vouchers to the warehouse system
    """
    # Variable that enables the form to update record of a meal voucher
    # ...of a particular value that is already in the meal voucher warehouse
    mealvoucher_to_update = MealVoucherInput.objects.get(pk=1)

    # Mealvoucher Add Form
    if request.method == 'POST':
        add_mealvoucher_form = MealVoucherAddForm(request.POST, instance=mealvoucher_to_update)
        # add_mealvoucher_form = MealVoucherAddForm(request.POST)
        if add_mealvoucher_form.is_valid():
            vouchers_to_add = add_mealvoucher_form.save(commit=False)
            vouchers_to_add.save()
            # Procedure to call related to the form submit button
            # The procedure will make quantitative changes in mealvouchers warehouse
            conn = psycopg2.connect(dbname=env("DATABASE_NAME"), user=env("DATABASE_USER"),
                                    password=env("DATABASE_PASSWORD"))
            cur = conn.cursor()
            cur.execute("CALL add_mealvoucher();")
            conn.commit()
            # Make the input field blank after submitting the form
            return redirect('/add_mealvouchers/')
    else:
        add_mealvoucher_form = MealVoucherAddForm()

    # variable different from the variable connected to the form
    mealvouchers_warehouse = MealVoucherWarehouse.objects.all().order_by('hodnota')

    mv_sum = MealVoucherWarehouse.objects.all().aggregate(total_sum=Sum('suma'))

    context = {
        'add_mealvoucher_form': add_mealvoucher_form,
        'mealvouchers_warehouse': mealvouchers_warehouse,
        'distribution_sum': mv_sum,
    }
    return render(request, 'add_mealvouchers/add_mealvouchers.html', context)


def homepage(request):
    context = {}

    return render(request, '_homepage/homepage.html', context)
