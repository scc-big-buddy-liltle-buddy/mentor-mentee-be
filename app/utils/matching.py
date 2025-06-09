import datetime
import math
import uuid

from typing import List, Optional

from app.models import (
    Group, Match, MatchMentee, Mentee, Mentor
)
from app.utils.array import find_common_element
from app.utils.selfintro_similarity import calculateSelfIntroScore
from app.utils.global_matching import generate_global_match


def calculateMatchingRate(mentee:Mentee, mentor:Mentor):
    total_points = 0
    # Accessing attributes using dict[key]
    if (mentee.education.major == mentor.occupation.industry):
        total_points += 2
        
    # Assuming find_common_element is a helper function you've defined
    wanted_fields = find_common_element(mentee.mentee.industries, mentor.mentor.industries)
    total_points += len(wanted_fields) * 1
    
    wanted_soft_skills = find_common_element(mentee.mentee.softSkills, mentor.mentor.softSkills)
    total_points += len(wanted_soft_skills) * 2   
        
    if(mentee.gender == mentor.gender):
        total_points += 1
    
    if(mentee.education.currentSchoolYear == mentor.mentor.preferredMenteeCollegeYear):
        total_points += 1 

    selfintro_similarity_score = calculateSelfIntroScore(mentee, mentor)
    total_points += selfintro_similarity_score
    
    return total_points

# High level switch to determine which generate group method to use
def generate_match(mentees, mentors, method="greedy"):
    if method == "global":
        return generate_global_match(
            mentees, mentors,
            max_group_size=math.ceil(len(mentees)/len(mentors))
        )
    return generateGroup(mentees, mentors)

#  Read list of mentees and mentors from mentor.json and mentee.json
#  Generate a match with the mentees and mentors

def generateGroup(mentees, mentors, matchName:Optional[str] = None):
    groups:List[Group] = []
    candidates = []
    

    max_group_size = math.ceil(len(mentees) / len(mentors))



    print("max_gr_sz",max_group_size)
    for mentor in mentors:
        for mentee in mentees:
            score = calculateMatchingRate(mentee, mentor)
            candidates.append({
                "mentee": mentee,
                "mentor": mentor,
                "score": score
            })
    
    candidates.sort(key=lambda x: x["score"], reverse=True)
    unmatched_mentees = mentees.copy()
    target_mentor = 0
    
    while len(unmatched_mentees) > 0:
        group:Group = {
            "id":target_mentor,
            "mentorId": mentors[target_mentor]["id"],
            "mentees": [],
        }
        for candidate in candidates:
            if candidate["mentor"] == mentors[target_mentor] and candidate["mentee"] in unmatched_mentees and len(group['mentees']) < max_group_size:
                new_match_mentee:MatchMentee = {
                    "menteeId": candidate["mentee"]["id"],
                    "menteeName": candidate["mentee"]["fullName"],
                    "matchRate": candidate["score"]
                }
                group["mentees"].append(new_match_mentee)
                unmatched_mentees.remove(candidate["mentee"])
                candidates.remove(candidate)
        groups.append(group)
        target_mentor += 1
        target_mentor = target_mentor % len(mentors)
        
    new_match:Match = {
        "uid": str(uuid.uuid4()),
        "createdAt": str(datetime.datetime.now()),
        "groups": groups,
        "matchName": matchName if matchName else "Match " + str(datetime.datetime.now())
    }

    return new_match        
            

