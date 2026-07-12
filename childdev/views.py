from django.shortcuts import render


def frontend_home(request):
    return render(request, 'frontend.html')


def child_dashboard_home(request):
    return render(request, 'child_dashboard.html')


def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


def milestones_page(request):
    return render(request, 'milestones_page.html')


def assessments_page(request):
    return render(request, 'assessments_page.html')


def care_page(request):
    return render(request, 'care_page.html')


def referrals_page(request):
    return render(request, 'referrals_page.html')


def child_detail_page(request, child_id):
    return render(request, 'child_detail_page.html', {'child_id': child_id})
