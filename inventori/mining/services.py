from collections import defaultdict
from django.db import transaction
from django.db.models import Count
from sales.models import SaleItem
from .models import AssociationRule


def build_baskets():
    """
    Build transaction baskets from SaleItem data
    Returns a list of sets, where each set represents items in a single transaction
    """
    baskets = defaultdict(set)
    
    # Group SaleItem by sale_id to form transaction baskets
    sale_items = SaleItem.objects.select_related("sale", "product").values(
        "sale_id", "product__sku"
    ).order_by("sale_id", "product__sku")
    
    for si in sale_items:
        baskets[si["sale_id"]].add(si["product__sku"])
    
    return list(baskets.values())


def apriori(baskets, min_support=0.05, min_conf=0.6):
    """
    Apriori algorithm implementation
    """
    N = len(baskets)
    
    def support(itemset):
        """Calculate support for an itemset"""
        count = sum(1 for b in baskets if itemset.issubset(b))
        return count / N
    
    # Generate frequent 1-itemsets
    all_items = set()
    for basket in baskets:
        all_items.update(basket)
    
    items = sorted(all_items)
    L1 = {frozenset([item]) for item in items if support(frozenset([item])) >= min_support}
    
    L = [L1]  # List of frequent itemsets for each size
    k = 2
    
    # Generate frequent k-itemsets for k > 1
    while L[-1]:
        Ck = set()
        prev = list(L[-1])
        
        # Generate candidate k-itemsets from (k-1)-itemsets
        for a in range(len(prev)):
            for b in range(a + 1, len(prev)):
                union = prev[a] | prev[b]
                if len(union) == k:
                    Ck.add(union)
        
        # Filter candidates that meet minimum support
        Lk = {c for c in Ck if support(c) >= min_support}
        
        if not Lk:
            break
            
        L.append(Lk)
        k += 1
    
    # Generate association rules from frequent itemsets
    rules = []
    for Lk in L[1:]:  # Skip 1-itemsets
        for F in Lk:  # For each frequent itemset F
            for r in range(1, len(F)):  # For each possible rule size
                from itertools import combinations
                for A in combinations(F, r):
                    A = set(A)
                    B = F - A  # consequent = itemset - antecedent
                    
                    supF = support(F)
                    supA = support(A)
                    supB = support(B)
                    
                    if supA == 0:
                        continue
                        
                    conf = supF / supA
                    lift = conf / supB if supB > 0 else 0
                    
                    # Only include rules that meet minimum confidence and have lift > 1
                    if conf >= min_conf and lift >= 1:
                        rules.append({
                            'antecedent': sorted(list(A)),
                            'consequent': sorted(list(B)),
                            'support': supF,
                            'confidence': conf,
                            'lift': lift
                        })
    
    return rules


def run_and_persist(min_support=0.05, min_conf=0.6, limit=200):
    """
    Run the mining algorithm and persist the rules to the database
    """
    baskets = build_baskets()
    rules = apriori(baskets, min_support, min_conf)
    
    # Sort rules: by lift (descending), then confidence (descending), then support (descending)
    rules.sort(key=lambda x: (-x['lift'], -x['confidence'], -x['support']))
    
    # Keep only the specified number of rules
    rules = rules[:limit]
    
    # Delete existing rules and create new ones
    with transaction.atomic():
        AssociationRule.objects.all().delete()
        for rule in rules:
            AssociationRule.objects.create(
                antecedent=rule['antecedent'],
                consequent=rule['consequent'],
                support=rule['support'],
                confidence=rule['confidence'],
                lift=rule['lift']
            )
    
    return len(rules)


def get_top_rules(limit=10, sort_by='lift'):
    """
    Get top association rules based on specified criteria
    """
    if sort_by == 'lift':
        rules = AssociationRule.objects.order_by('-lift', '-confidence', '-support')[:limit]
    elif sort_by == 'confidence':
        rules = AssociationRule.objects.order_by('-confidence', '-lift', '-support')[:limit]
    elif sort_by == 'support':
        rules = AssociationRule.objects.order_by('-support', '-lift', '-confidence')[:limit]
    else:
        rules = AssociationRule.objects.all()[:limit]
    
    return rules