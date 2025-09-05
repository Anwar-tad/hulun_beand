from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

class PremiumAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for static files and certain paths
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # List of URL names to exempt (without reversing)
        exempt_url_names = [
            'premium_upgrade',
            'business_verification',
            'premium_success',
            'verification_success',
            'login',
            'logout',
            'register',
            'switch_to_standard',
            'switch_to_wholesale',  # Add this even if it might not exist
            'api_premium_status',
        ]
        
        # Check if current path matches any exempt URL
        for url_name in exempt_url_names:
            try:
                exempt_url = reverse(url_name)
                if request.path == exempt_url:
                    return None
            except NoReverseMatch:
                # Skip URLs that don't exist
                continue
        
        # Check if user is trying to access premium features
        if (request.path.startswith('/premium/') or 
            request.path.startswith('/wholesale/')) and request.user.is_authenticated:
            
            # Get or create user tier
            from .models import UserTier, Profile
            user_tier, created = UserTier.objects.get_or_create(user=request.user)
            profile, profile_created = Profile.objects.get_or_create(user=request.user)
            
            # Check if user has wholesale access
            if user_tier.tier != 'wholesale' or not user_tier.is_paid:
                return redirect('premium_upgrade')
            
            # Check premium status
            if not profile.is_premium_active():
                return redirect('premium_upgrade')
            
            # Check business verification for wholesale access
            if not profile.business_verified:
                return redirect('business_verification')
        
        return None