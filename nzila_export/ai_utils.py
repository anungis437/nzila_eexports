"""
AI-Powered Lead Scoring and Recommendations
Phase 2: Smart Automation Features
"""
from django.db.models import Count, Avg, Q
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone


class LeadScoringEngine:
    """
    AI-powered lead scoring to prioritize high-value opportunities
    Based on historical data and behavioral patterns
    """
    
    @staticmethod
    def calculate_lead_score(lead):
        """
        Calculate a score (0-100) for a lead based on multiple factors
        Higher score = higher conversion probability
        """
        score = 50  # Base score
        
        # Factor 1: Buyer engagement (30 points)
        if lead.last_contacted:
            days_since_contact = (timezone.now() - lead.last_contacted).days
            if days_since_contact == 0:
                score += 30
            elif days_since_contact <= 2:
                score += 20
            elif days_since_contact <= 7:
                score += 10
        
        # Factor 2: Vehicle price range (20 points)
        vehicle_price = lead.vehicle.price_cad
        if vehicle_price < 20000:
            score += 20  # Lower price = easier to close
        elif vehicle_price < 35000:
            score += 15
        else:
            score += 10
        
        # Factor 3: Source quality (15 points)
        source_scores = {
            'referral': 15,
            'broker': 12,
            'direct': 10,
            'website': 8
        }
        score += source_scores.get(lead.source, 5)
        
        # Factor 4: Buyer history (15 points)
        from deals.models import Deal
        previous_deals = Deal.objects.filter(
            buyer=lead.buyer,
            status='completed'
        ).count()
        
        if previous_deals > 0:
            score += min(15, previous_deals * 5)
        
        # Factor 5: Lead age (10 points)
        lead_age = (timezone.now() - lead.created_at).days
        if lead_age <= 1:
            score += 10
        elif lead_age <= 3:
            score += 7
        elif lead_age <= 7:
            score += 5
        
        # Factor 6: Broker involvement (10 points)
        if lead.broker:
            score += 10
        
        return min(100, max(0, score))
    
    @staticmethod
    def get_conversion_probability(lead):
        """
        Estimate conversion probability based on historical data
        """
        from deals.models import Lead, Deal
        
        # Get similar leads that converted
        similar_leads = Lead.objects.filter(
            status='converted',
            source=lead.source,
            vehicle__price_cad__range=(
                lead.vehicle.price_cad * Decimal('0.8'),
                lead.vehicle.price_cad * Decimal('1.2')
            )
        ).count()
        
        total_similar = Lead.objects.filter(
            source=lead.source,
            vehicle__price_cad__range=(
                lead.vehicle.price_cad * Decimal('0.8'),
                lead.vehicle.price_cad * Decimal('1.2')
            )
        ).count()
        
        if total_similar > 0:
            probability = (similar_leads / total_similar) * 100
        else:
            probability = 50  # Default probability
        
        return round(probability, 2)
    
    @staticmethod
    def recommend_next_action(lead):
        """
        AI-powered recommendation for next best action
        """
        score = LeadScoringEngine.calculate_lead_score(lead)
        lead_age = (timezone.now() - lead.created_at).days
        
        if score >= 70:
            priority = 'high'
            if not lead.last_contacted:
                action = 'Contact immediately - High value lead!'
            elif (timezone.now() - lead.last_contacted).days >= 2:
                action = 'Follow up within 24 hours'
            else:
                action = 'Continue engagement, send vehicle details'
        
        elif score >= 40:
            priority = 'medium'
            if lead_age > 7:
                action = 'Re-engage with special offer'
            else:
                action = 'Schedule a call within 3 days'
        
        else:
            priority = 'low'
            action = 'Add to nurture campaign, check back in 7 days'
        
        return {
            'score': score,
            'priority': priority,
            'recommended_action': action,
            'conversion_probability': LeadScoringEngine.get_conversion_probability(lead)
        }


class DocumentQualityChecker:
    """
    AI-powered document quality assessment
    Phase 2: Automated document verification
    """
    
    @staticmethod
    def check_document_quality(document):
        """
        Assess document quality (placeholder for AI integration)
        Returns quality score and issues
        """
        issues = []
        score = 100
        
        # Check 1: File size (basic validation)
        if hasattr(document.file, 'size'):
            if document.file.size < 50000:  # Less than 50KB
                issues.append('File size too small - may be low quality')
                score -= 20
            elif document.file.size > 10485760:  # More than 10MB
                issues.append('File size very large - may be unnecessary')
                score -= 10
        
        # Check 2: File type validation
        allowed_types = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = document.file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_types:
            issues.append('Invalid file type - use PDF or image files')
            score -= 30
        
        # Future AI enhancements:
        # - OCR to extract and validate text
        # - Image quality assessment (blur, brightness, contrast)
        # - Document authenticity verification
        # - Auto-classification of document type
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendation': 'Approve' if score >= 70 else 'Review Required'
        }


class PricePredictionEngine:
    """
    AI-powered vehicle price prediction
    Helps dealers price vehicles competitively
    """
    
    @staticmethod
    def suggest_price(vehicle):
        """
        Suggest optimal price based on market data
        """
        from vehicles.models import Vehicle
        from deals.models import Deal
        
        # Get similar vehicles
        similar_vehicles = Vehicle.objects.filter(
            make=vehicle.make,
            year__range=(vehicle.year - 2, vehicle.year + 2),
            status='sold'
        )
        
        if similar_vehicles.exists():
            avg_price = similar_vehicles.aggregate(Avg('price_cad'))['price_cad__avg']
            
            # Adjust based on condition
            condition_multipliers = {
                'new': 1.15,
                'used_excellent': 1.05,
                'used_good': 1.0,
                'used_fair': 0.90
            }
            
            suggested_price = avg_price * Decimal(str(condition_multipliers.get(vehicle.condition, 1.0)))
            
            # Get price range
            price_range = {
                'min': suggested_price * Decimal('0.9'),
                'suggested': suggested_price,
                'max': suggested_price * Decimal('1.1')
            }
            
            # Calculate market demand
            sold_count = Deal.objects.filter(
                vehicle__make=vehicle.make,
                vehicle__year=vehicle.year,
                status='completed',
                created_at__gte=timezone.now() - timedelta(days=90)
            ).count()
            
            demand = 'high' if sold_count > 10 else 'medium' if sold_count > 5 else 'low'
            
            return {
                'price_range': price_range,
                'market_demand': demand,
                'similar_vehicles_count': similar_vehicles.count(),
                'avg_days_to_sell': 30,  # Placeholder for actual calculation
                'confidence': 85 if similar_vehicles.count() > 5 else 60
            }
        
        return {
            'price_range': {
                'min': vehicle.price_cad * Decimal('0.9'),
                'suggested': vehicle.price_cad,
                'max': vehicle.price_cad * Decimal('1.1')
            },
            'market_demand': 'unknown',
            'similar_vehicles_count': 0,
            'confidence': 30,
            'note': 'Insufficient market data for accurate prediction'
        }


class FraudDetectionEngine:
    """
    AI-powered fraud detection for deals and users
    """
    
    @staticmethod
    def assess_deal_risk(deal):
        """
        Assess fraud risk for a deal
        Returns risk score and red flags
        """
        risk_score = 0
        red_flags = []
        
        # Check 1: Buyer account age
        buyer_age = (timezone.now() - deal.buyer.date_joined).days
        if buyer_age < 7:
            risk_score += 20
            red_flags.append('New buyer account (less than 7 days)')
        
        # Check 2: Price anomaly
        if deal.agreed_price_cad < deal.vehicle.price_cad * Decimal('0.7'):
            risk_score += 30
            red_flags.append('Deal price significantly below vehicle price')
        
        # Check 3: Rapid progression
        if hasattr(deal, 'lead') and deal.lead:
            lead_to_deal_time = (deal.created_at - deal.lead.created_at).days
            if lead_to_deal_time < 1:
                risk_score += 15
                red_flags.append('Very rapid lead-to-deal conversion')
        
        # Check 4: Buyer location vs destination
        if deal.buyer.country and hasattr(deal, 'shipment'):
            # Check if countries match (placeholder logic)
            pass
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'red_flags': red_flags,
            'recommendation': 'Additional verification required' if risk_level in ['high', 'medium'] else 'Proceed normally'
        }
