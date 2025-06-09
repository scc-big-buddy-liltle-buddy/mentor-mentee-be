"""
group_assignment.py

WORK-IN-PROGRESS

This module provides functionality to generate balanced groups of mentees 
assigned to mentors based on computed match scores.

Functions:
- calculate_balanced_group_size: Computes the number of mentees per mentor for a balanced distribution.
- generate_balanced_group: Assigns mentees to mentors to form balanced groups based on match score.
"""


from app.utils.matching import calculateMatchingRate

def calculate_balanced_group_size(mentee_count, mentor_count): 
    base_size = mentee_count // mentor_count
    extra_mentees = mentee_count % mentor_count

    group_sizes = [base_size + 1 if i < extra_mentees else base_size for i in range(mentor_count)]
   
    return group_sizes
    
def generate_balanced_group(mentees, mentors): 
    group_sizes = calculate_balanced_group_size(len(mentees), len(mentors)) 

    all_matches = [] 
    for mentor_idx, mentor in enumerate(mentors): 
        for mentee in mentees: 
            score = calculateMatchingRate(mentee, mentor) 
            all_matches.append({ 
                "mentee": mentee, 
                "mentor": mentor, 
                "mentor_idx": mentor_idx,
                "score": score 
            })

    all_matches.sort(key=lambda x: x["score"], reverse=True)

    groups = [{"mentor": mentor, "mentees": []} for mentor in mentors] 
    unmatched_mentees = set(mentees) 

    for match in all_matches: 
        mentor_idx = match["mentor_idx"] 
        mentee = match["mentee"] 

        if mentee in unmatched_mentees and len(groups[mentor_idx]["mentees"]) < group_sizes[mentor_idx]: 
            groups[mentor_idx]["mentees"].append(mentee) 
            unmatched_mentees.remove(mentee)

    return groups


def generate_groups_with_constraints(mentees, mentors, constraints): 
    base_sizes = calculate_balanced_group_size(len(mentees), len(mentors))

    groups = [{"mentor": mentor, "mentees": []} for mentor in mentors]

    all_matches = [] 
    for mentor_idx, mentor in enumerate(mentors): 
        for mentee_idx, mentee in enumerate(mentees): 
            score = calculateMatchingRate(mentee, mentor)
            all_matches.append({
                "mentee_idx": mentee_idx,
                "mentor_idx": mentor_idx,
                "score": score
            })
    
    all_matches.sort(key=lambda x: x["score"], reverse=True)

    assigned_mentees=set()
    current_sizes = [0] * len(mentors)

    for match in all_matches: 
        mentee_idx = match["mentee_idx"]
        mentor_idx = match["mentor_idx"]

        if mentee_idx not in assigned_mentees and current_sizes[mentor_idx] < base_sizes[mentor_idx]: 
            groups[mentor_idx]["mentees"].append(mentees[mentee_idx]) 
            assigned_mentees.add(mentee_idx)
            current_sizes[mentor_idx] += 1

    valid, issues = constraints.validate_assignment(groups)

    if not valid: 
        pass 

    return groups, valid, issues
