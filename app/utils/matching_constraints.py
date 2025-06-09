"""
matching_constraints.py

WORK-IN-PROGRESS

This module defines the MatchingConstraints class, which enforces and 
validates constraints on mentor-mentee group assignments. It supports:

- Group size limits
- Skill matching enforcement
- Diversity checking
- Minimum match score validation

Dependencies:
- calculateMatchingRate from app.utils.matching
- find_common_element from app.utils.array
"""

from app.utils.matching import calculateMatchingRate
from app.utils.array import find_common_element


class MatchingConstraints: 
    def __init__(self, min_group_size=1, max_group_size=None, required_skills=False, enforce_diversity=False, min_match_score=0.5): 
        self.min_group_size = min_group_size
        self.max_group_size = max_group_size
        self.required_skills = required_skills
        self.enforce_diversity = enforce_diversity
        self.min_match_score = min_match_score
    
    def validate_assignment(self, groups): 
        valid = True 
        issues = []

        for group in groups: 
            
            if len(group["mentees"]) < self.min_group_size: 
                valid = False 
                issues.append(f"Group for mentor {group['mentor']['id']} has fewer than "
                              f"{self.min_group_size} mentees")
                
            if self.max_group_size and len(group["mentees"]) > self.max_group_size: 
                valid = False 
                issues.append(f"Group for mentor {group['mentor']['id']} has more than "
                              f"{self.max_group_size} mentees") 

            if self.enforce_diversity: 
                province = set(mentee.currentLocation for mentee in group["mentees"])
                
                if len(province) < 2: 
                    valid = False 
                    issues.append(f"Mentor group {group['mentor']['id']} lacks diversity")

            for mentee in group["mentees"]: 
                mentor = group["mentor"]
                score = calculateMatchingRate(mentee, mentor)
                
                if score < self.min_match_score: 
                    valid = False 
                    issues.append(f"Mentor {group['mentor']['id']} and mentee match score doesn't meet minimum threshold") 
                
                if self.required_skills: 
                    wanted_fields = find_common_element(mentee.mentee.industries, mentor.mentor.industries)
                    wanted_soft_skills = find_common_element(mentee.mentee.softSkills, mentor.mentor.softSkills)
                    
                    if not wanted_fields and not wanted_soft_skills: 
                        valid = False 
                        issues.append(f"Mentor {group['mentor']['id']} skills don't match mentee requested skills")
                
        return valid, issues
