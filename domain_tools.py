from typing import List, Dict, Optional
from langchain.tools import BaseTool, StructuredTool, Tool
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class DomainTools:
    def __init__(self):
        self.godaddy_api_key = os.getenv('GODADDY_API_KEY')
        self.godaddy_api_secret = os.getenv('GODADDY_API_SECRET')
        self.api_headers = {
            'Authorization': f'sso-key {self.godaddy_api_key}:{self.godaddy_api_secret}',
            'Content-Type': 'application/json'
        }

    def get_tools(self) -> List[Tool]:
        """Return list of tools compatible with crewAI"""
        
        tools = [
            Tool(
                name="check_domain_availability",
                func=self.check_domain_availability,
                description="""Check if a domain name is available for registration.
                Input should be a domain name without extension.
                Returns availability status and pricing information."""
            ),
            
            Tool(
                name="generate_domain_variations",
                func=self.generate_domain_variations,
                description="""Generate variations of a domain name using common patterns.
                Input should be a base domain name. Domain name should always be of .ai type
                Returns list of domain variations with different prefixes and suffixes."""
            ),
            
            Tool(
                name="research_similar_companies",
                func=self.research_similar_companies,
                description="""Research companies with similar names or in similar business domains.
                Input should be a domain name or company name.
                Returns information about similar companies."""
            ),
            
            Tool(
                name="estimate_domain_value",
                func=self.estimate_domain_value,
                description="""Estimate the market value of a domain name.
                Input should be a domain name.
                Returns estimated value and factors affecting the valuation."""
            ),
            
            Tool(
                name="check_trademark_conflicts",
                func=self.check_trademark_conflicts,
                description="""Check for potential trademark conflicts for a domain name.
                Input should be a domain name.
                Returns list of potential trademark conflicts."""
            )
        ]
        
        return tools

    def check_domain_availability(self, domain_name: str) -> Dict:
        """Check domain availability using GoDaddy API"""
        url = f'https://api.godaddy.com/v1/domains/available?domain={domain_name}'
        
        try:
            response = requests.get(url, headers=self.api_headers)
            data = response.json()
            
            return {
                'domain': domain_name,
                'available': data.get('available', False),
                'price': data.get('price'),
                'currency': data.get('currency', 'USD')
            }
        except Exception as e:
            return {
                'domain': domain_name,
                'available': False,
                'error': str(e)
            }

    def generate_domain_variations(self, base_name: str) -> List[Dict]:
        """Generate domain name variations"""
        variations = []
        prefixes = ['get', 'try', 'use', 'my', 'the']
        suffixes = ['app', 'io', 'co', 'net', 'org']
        
        for prefix in prefixes:
            name = f"{prefix}{base_name}"
            if len(name) <= 63:
                variations.append({
                    'name': name.lower(),
                    'type': 'prefix',
                    'score': 0.8
                })
        
        for suffix in suffixes:
            name = f"{base_name}{suffix}"
            if len(name) <= 63:
                variations.append({
                    'name': name.lower(),
                    'type': 'suffix',
                    'score': 0.9
                })
        
        return variations

    def research_similar_companies(self, domain_name: str) -> List[Dict]:
        """Research similar companies"""
        return [{
            'name': f"Similar{domain_name}",
            'description': "A similar company in the industry",
            'website': f"https://similar{domain_name}.com",
            'industry': "Technology",
            'founded_year': 2020
        }]

    def estimate_domain_value(self, domain_name: str) -> Dict:
        """Estimate domain value"""
        length = len(domain_name)
        has_numbers = any(char.isdigit() for char in domain_name)
        
        base_value = 1000
        if length < 6:
            base_value *= 2
        if not has_numbers:
            base_value *= 1.5
            
        return {
            'estimated_value': base_value,
            'factors': {
                'length': length,
                'has_numbers': has_numbers,
                'brandability_score': 7.5
            },
            'confidence_score': 0.8
        }

    def check_trademark_conflicts(self, domain_name: str) -> List[Dict]:
        """Check trademark conflicts"""
        return [{
            'trademark': domain_name.upper(),
            'owner': "Sample Company Inc",
            'registration_number': "US123456",
            'risk_level': "LOW"
        }]