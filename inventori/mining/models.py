from django.db import models
import json


class AssociationRule(models.Model):
    """
    Association Rule model for Apriori algorithm
    """
    antecedent = models.JSONField()  # e.g., ["Stopkontak","Saklar"]
    consequent = models.JSONField()  # e.g., ["Dudukan Lampu"]
    support = models.DecimalField(max_digits=6, decimal_places=4)
    confidence = models.DecimalField(max_digits=6, decimal_places=4)
    lift = models.DecimalField(max_digits=8, decimal_places=4)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'association_rule'
        indexes = [
            models.Index(fields=['lift', 'confidence', 'support'], name='idx_rule_metrics'),
        ]
    
    def __str__(self):
        ant = ', '.join(json.loads(self.antecedent)) if isinstance(self.antecedent, str) else ', '.join(self.antecedent)
        cons = ', '.join(json.loads(self.consequent)) if isinstance(self.consequent, str) else ', '.join(self.consequent)
        return f"{ant} -> {cons} (lift: {self.lift})"
    
    def get_antecedent_list(self):
        """Return antecedent as a list of strings"""
        if isinstance(self.antecedent, str):
            return json.loads(self.antecedent)
        return self.antecedent
    
    def get_consequent_list(self):
        """Return consequent as a list of strings"""
        if isinstance(self.consequent, str):
            return json.loads(self.consequent)
        return self.consequent