from crewai import Agent, Task, Crew, Process
from langchain.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from domain_tools import DomainTools
from typing import List, Dict
import numpy as np
import random
import string
import requests
import os

class DomainResearchRequest(BaseModel):
    """Domain research request parameters"""
    domain_type: str
    industry: Optional[str] = None
    max_length: Optional[int] = 15
    include_numbers: Optional[bool] = False

class DomainResearchResult(BaseModel):
    """Domain research comprehensive results"""
    domain_name: str
    availability: Dict
    variations: List[str]
    similar_companies: List[Dict]
    estimated_value: Dict
    trademark_conflicts: List[Dict]
    timestamp: datetime

class DomainResearchCrew:
    def __init__(self):
        self.tools = DomainTools().get_tools()
        self.setup_agents()

    def setup_agents(self):
        """Initialize specialized agents for domain research"""
        
        # Domain Generator Agent (removed duplicate name_agent)
        self.name_generator = Agent(
            role='Domain Name Generator',
            goal='Generate creative and relevant domain names based on user requirements',
            backstory="""You are an expert in creating memorable domain names. 
            You understand naming conventions, branding, and what makes a domain name effective.
            You consider industry trends and best practices when generating names.""",
            tools=[],
            verbose=True
        )
        
        # Availability Agent
        self.availability_agent = Agent(
            role='Availability Checker',
            goal='Check domain availability and estimate value',
            backstory="""You are an expert in domain availability and valuation.
            You analyze domain status and potential worth.""",
            tools=[self.tools[0], self.tools[3]],  # check_availability and estimate_value tools
            verbose=True
        )

        # Research Agent
        self.research_agent = Agent(
            role='Market Researcher',
            goal='Research market context and potential conflicts',
            backstory="""You are an expert in market research and trademark analysis.
            You identify similar companies and potential conflicts.""",
            tools=[self.tools[2], self.tools[4]],  # research_companies and check_trademark tools
            verbose=True
        )

    def create_tasks(self, request: DomainResearchRequest) -> List[Task]:
        """Create all tasks with proper dependencies and expected outputs"""
        
        # Task 1: Generate Names
        name_generation_task = Task(
            description=f"""Generate creative domain names based on the following criteria:
            - Industry: {request.industry or 'Not specified'}
            - Type: {request.domain_type}
            - Maximum length: {request.max_length}
            - Include numbers: {request.include_numbers}
            
            Generate at least 10 unique names that are:
            - Memorable and brandable
            - Relevant to the industry and type
            - Available as .ai domains
            - Following modern naming trends
            """,
            expected_output="""A JSON array of objects, each containing:
            {
                "domain_name": "suggested name with .ai",
                "rationale": "explanation of why this name fits the criteria",
                "industry_relevance": "how it relates to the industry"
            }
            Return exactly 10 domain suggestions.""",
            agent=self.name_generator
        )

        # Task 2: Check Availability and Value
        availability_task = Task(
            description="""For each generated domain name:
            1. Check domain availability
            2. Estimate potential value
            3. Provide pricing information
            
            Focus on domains with highest potential value and availability.""",
            expected_output="""A JSON array of objects, each containing:
            {
                "domain_name": "analyzed domain with the suffix of .ai",
                "availability": {
                    "is_available": true/false,
                    "price": "estimated price",
                    "currency": "USD"
                },
                "valuation": {
                    "estimated_value": "value in USD",
                    "factors": {
                        "length": "domain length",
                        "brandability": "score out of 10",
                        "memorable": "score out of 10"
                    }
                }
            }""",
            agent=self.availability_agent,
            dependencies=[name_generation_task]
        )

        # Task 3: Market Research
        market_research_task = Task(
            description="""For the most promising available domains:
            1. Research similar companies
            2. Check trademark conflicts
            3. Analyze competitive landscape
            4. Assess brand potential
            
            Provide detailed findings and risk assessment.""",
            expected_output="""A JSON array of objects, each containing:
            {
                "domain_name": "researched domain with the .ai suffix",
                "availability": {
                    "is_available": true/false,
                    "price": "estimated price",
                    "currency": "USD"
                },
                "similar_companies": [
                    {
                        "name": "company name",
                        "website": "company website",
                        "similarity_score": "score out of 10",
                        "potential_conflict": true/false
                    }
                ],
                "trademark_analysis": {
                    "has_conflicts": true/false,
                    "risk_level": "LOW/MEDIUM/HIGH",
                    "details": "explanation of any conflicts"
                },
                "market_analysis": {
                    "competition_level": "score out of 10",
                    "brand_potential": "score out of 10",
                    "recommendations": "specific recommendations"
                }
            }""",
            agent=self.research_agent,
            dependencies=[availability_task]
        )

        return [name_generation_task, availability_task, market_research_task]

    def process_domain_request(
        self,
        request: DomainResearchRequest
    ) -> Dict[str, List[DomainResearchResult]]:
        """Process a complete domain research request with a single crew"""
        
        # Create all tasks with dependencies
        tasks = self.create_tasks(request)
        
        # Create single crew with all agents
        crew = Crew(
            agents=[self.name_generator, self.availability_agent, self.research_agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute all tasks
        results = crew.kickoff()
        
        # Process the results
        processed_results = self.process_results(results)
        
        return processed_results

    def process_results(self, crew_results: str):
        """Process the crew results into structured format"""
        research_results = []
        
        print(crew_results)
        # names = crew_results.get('generated_names', [])
        # for name in names[:5]:  # Limit to top 5 names
        #     result = DomainResearchResult(
        #         domain_name=name,
        #         availability=self.tools[0](name),  # check_availability
        #         variations=self.tools[1](name),    # generate_variations
        #         similar_companies=self.tools[2](name),  # research_companies
        #         estimated_value=self.tools[3](name),    # estimate_value
        #         trademark_conflicts=self.tools[4](name), # check_trademark
        #         timestamp=datetime.now()
        #     )
        #     research_results.append(result)
        
        # return {
        #     "initial_names": names,
        #     "research_results": research_results
        # }

    def filter_results(
        self,
        results: List[DomainResearchResult],
        min_value: Optional[float] = None,
        must_be_available: bool = True
    ) -> List[DomainResearchResult]:
        """Filter research results based on criteria"""
        filtered = results.copy()
        
        if must_be_available:
            filtered = [r for r in filtered if r.availability['available']]
            
        if min_value:
            filtered = [r for r in filtered if r.estimated_value['estimated_value'] >= min_value]
            
        return filtered

# Example usage
def main():
    crew = DomainResearchCrew()
    
    # Create a research request
    request = DomainResearchRequest(
        domain_type="tech startup",
        industry="Technology",
        max_length=12,
        include_numbers=False
    )
    
    # Process the request
    results = crew.process_domain_request(request)
    
    # # Filter results
    # filtered_results = crew.filter_results(
    #     results['research_results'],
    #     min_value=1000,
    #     must_be_available=True
    # )
    
    # # Print results
    # print("\nInitial Names:", results['initial_names'])
    # print("\nDetailed Research Results:")
    # for result in filtered_results:
    #     print(f"\nDomain: {result.domain_name}")
    #     print(f"Available: {result.availability['available']}")
    #     print(f"Estimated Value: ${result.estimated_value['estimated_value']}")
    #     print(f"Similar Companies: {len(result.similar_companies)}")
    #     print(f"Trademark Conflicts: {len(result.trademark_conflicts)}")

if __name__ == "__main__":
    main()