from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import AssociationRule
from .services import run_and_persist, get_top_rules


@login_required
def mining_run(request):
    """
    Run the Apriori mining algorithm with specified parameters
    """
    # Check if user has permission to run mining
    if request.user.role not in ['analyst', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        min_support = float(request.POST.get('min_support', 0.05))
        min_confidence = float(request.POST.get('min_confidence', 0.6))
        limit = int(request.POST.get('limit', 200))
        
        # Validate parameters
        if min_support <= 0 or min_support >= 1:
            messages.error(request, 'Minimum support harus antara 0 dan 1')
            return render(request, 'mining/run.html')
        if min_confidence <= 0 or min_confidence >= 1:
            messages.error(request, 'Minimum confidence harus antara 0 dan 1')
            return render(request, 'mining/run.html')
        
        try:
            count = run_and_persist(
                min_support=min_support,
                min_conf=min_confidence,
                limit=limit
            )
            messages.success(request, f'Algoritma Apriori berhasil dijalankan. Ditemukan {count} aturan asosiasi.')
            return render(request, 'mining/run.html')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat menjalankan algoritma: {str(e)}')
            return render(request, 'mining/run.html')
    else:
        # Show the form
        return render(request, 'mining/run.html')


@login_required
def association_rules_list(request):
    """
    List all association rules
    """
    # Check if user has permission to access association rules
    if request.user.role not in ['analyst', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sort_by = request.GET.get('sort_by', 'lift')  # Default sort by lift
    limit = int(request.GET.get('limit', 20))  # Default to 20 rules
    
    if sort_by not in ['lift', 'confidence', 'support']:
        sort_by = 'lift'
    
    rules = get_top_rules(limit=limit, sort_by=sort_by)
    
    context = {
        'rules': rules,
        'sort_by': sort_by,
        'limit': limit,
    }
    return render(request, 'mining/rules_list.html', context)


@login_required
def association_rules_api(request):
    """
    API endpoint for association rules, used by dashboard charts
    """
    sort_by = request.GET.get('sort_by', 'lift')
    limit = int(request.GET.get('limit', 10))
    
    if sort_by not in ['lift', 'confidence', 'support']:
        sort_by = 'lift'
    
    rules = get_top_rules(limit=limit, sort_by=sort_by)
    
    data = []
    for rule in rules:
        data.append({
            'antecedent': rule.get_antecedent_list(),
            'consequent': rule.get_consequent_list(),
            'support': float(rule.support),
            'confidence': float(rule.confidence),
            'lift': float(rule.lift),
            'rule_text': f"{', '.join(rule.get_antecedent_list())} → {', '.join(rule.get_consequent_list())}"
        })
    
    return JsonResponse({'rules': data})


@login_required
def mining_dashboard(request):
    """
    Mining dashboard showing the rules and their metrics
    """
    # Check if user has permission to access mining dashboard
    if request.user.role not in ['analyst', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    # Get top 10 rules by lift
    top_rules = get_top_rules(limit=10, sort_by='lift')
    
    context = {
        'top_rules': top_rules,
    }
    return render(request, 'mining/dashboard.html', context)