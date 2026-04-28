import math

def calculate_match_score(user1, user2):
    """
    Calculates a compatibility score between two users.
    A lower score indicates higher compatibility (Euclidean distance).
    """
    score = 0
    
    # 1. HARD FILTERS (Gender & Dorm Preference)
    # These are non-negotiable for University Housing.
    # If they don't match, we return infinity to prevent a pair.
    if user1.get('question1') != user2.get('question1'):
        return float('inf')
    
    if user1.get('question2') != user2.get('question2'):
        return float('inf')

    # 2. CATEGORICAL WEIGHTING
    # Lifestyle choices where a mismatch is a fixed "friction" point.
    # Weight of 10 is used to prioritize these over single-point slider differences.
    categorical_keys = [
        'question4',  # Greek Life
        'question7',  # Morning/Night
        'question9',  # Weekend habits (Oxford vs Home)
        'question12', # Study location
        'question14', # Bedtime
        'question16', # Nicotine use
        'question18'  # Primary Focus
    ]
    
    for key in categorical_keys:
        if user1.get(key) != user2.get(key):
            score += 10 

    # 3. SLIDER/NUMERICAL SCALING (Euclidean Distance)
    # Scales values 1-5. Squaring the difference penalizes extreme opposites 
    # (e.g., a "1" and a "5" creates a distance of 16).
    slider_keys = [
        'question3', 'question5', 'question6', 'question8', 'question10', 
        'question11', 'question13', 'question15', 'question17', 'question19', 
        'question20', 'question21'
    ]
    
    for key in slider_keys:
        try:
            # Data from HTML forms often comes in as strings; cast to int for math.
            val1 = int(user1.get(key, 3))
            val2 = int(user2.get(key, 3))
            diff = (val1 - val2) ** 2
            score += diff
        except (ValueError, TypeError):
            # Fallback if a value is missing or malformed
            continue

    # Result is the square root of the sum of squares (standard Euclidean metric).
    return math.sqrt(score)

def find_best_matches(users):
    """
    Greedy matching algorithm: finds the best available pair for each user.
    Note: For a 'Turing' or SQL database, 'users' would be the result of:
    SELECT * FROM survey_responses WHERE matched = 0
    """
    matches = []
    already_matched = set()

    # Iterate through the list of users to find pairings
    for i in range(len(users)):
        u1_id = users[i].get('name') # Use a unique ID or Name
        
        if u1_id in already_matched:
            continue
            
        best_score = float('inf')
        best_partner = None
        
        for j in range(i + 1, len(users)):
            u2_id = users[j].get('name')
            
            if u2_id in already_matched:
                continue
                
            current_score = calculate_match_score(users[i], users[j])
            
            # Update best partner if this current score is the lowest found so far
            if current_score < best_score and current_score != float('inf'):
                best_score = current_score
                best_partner = users[j]
        
        # If a valid partner was found (within hard filters), lock the pair
        if best_partner:
            u2_name = best_partner.get('name')
            matches.append({
                "pair": (u1_id, u2_name),
                "score": round(best_score, 2)
            })
            already_matched.add(u1_id)
            already_matched.add(u2_name)
            
    return matches