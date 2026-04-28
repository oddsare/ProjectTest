# Graph Report - .  (2026-04-23)

## Corpus Check
- Corpus is ~7,328 words - fits in a single context window. You may not need a graph.

## Summary
- 46 nodes · 62 edges · 8 communities detected
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Core UI & Shared Resources|Core UI & Shared Resources]]
- [[_COMMUNITY_Authentication Utilities|Authentication Utilities]]
- [[_COMMUNITY_Profile Management & Matching|Profile Management & Matching]]
- [[_COMMUNITY_Matching Algorithm|Matching Algorithm]]
- [[_COMMUNITY_Login Logic|Login Logic]]
- [[_COMMUNITY_Auth API & Forms|Auth API & Forms]]
- [[_COMMUNITY_Survey System|Survey System]]
- [[_COMMUNITY_Global Scripts|Global Scripts]]

## God Nodes (most connected - your core abstractions)
1. `Dashboard Page` - 10 edges
2. `Profile Page` - 8 edges
3. `Roommate Survey Page` - 7 edges
4. `Authentication Module (auth.js)` - 6 edges
5. `Roomi Brand (Ole Miss Roommate Matching)` - 6 edges
6. `Global Stylesheet (styles.css)` - 6 edges
7. `Survey Prompt Page` - 5 edges
8. `Profile API Endpoint` - 5 edges
9. `Login Page` - 4 edges
10. `Registration Page` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Password Change Form` --semantically_similar_to--> `Profile API Endpoint`  [INFERRED] [semantically similar]
  Public_html/profile.html → Public_html/dashboard.html
- `Login Form` --semantically_similar_to--> `Registration Form`  [INFERRED] [semantically similar]
  Public_html/login_improved.html → Public_html/register.html
- `Registration Form` --conceptually_related_to--> `Roomi Brand (Ole Miss Roommate Matching)`  [INFERRED]
  Public_html/register.html → Public_html/login_improved.html
- `Dashboard Page` --conceptually_related_to--> `Roomi Brand (Ole Miss Roommate Matching)`  [INFERRED]
  Public_html/dashboard.html → Public_html/login_improved.html
- `Profile Page` --calls--> `Profile API Endpoint`  [EXTRACTED]
  Public_html/profile.html → Public_html/dashboard.html

## Hyperedges (group relationships)
- **Authentication Flow** — login_improved_page, register_page, auth_module, dashboard_page [EXTRACTED 1.00]
- **User Setup Journey** — register_page, profile_page, survey_prompt_page, survey_page, dashboard_page [EXTRACTED 0.95]
- **Profile Completion and Management** — profile_page, profile_form, hobby_management, profile_picture_cropper, api_profile, api_upload_profile_picture [INFERRED 0.90]

## Communities

### Community 0 - "Core UI & Shared Resources"
Cohesion: 0.47
Nodes (11): Authentication Module (auth.js), CropperJS Library, Dashboard Page, Login Page, Profile Page, Registration Page, Roomi Brand (Ole Miss Roommate Matching), Survey Script (script.js) (+3 more)

### Community 1 - "Authentication Utilities"
Cohesion: 0.22
Nodes (0): 

### Community 2 - "Profile Management & Matching"
Cohesion: 0.22
Nodes (9): Matches API Endpoint, Profile API Endpoint, Profile Picture Upload Endpoint, Hobby Tag Management, Password Change Form, Profile Edit Form, Image Cropper Tool, Setup Progress Tracking (+1 more)

### Community 3 - "Matching Algorithm"
Cohesion: 0.5
Nodes (4): calculate_match_score(), find_best_matches(), Calculates a compatibility score between two users.     A lower score indicates, Greedy matching algorithm: finds the best available pair for each user.     Note

### Community 4 - "Login Logic"
Cohesion: 0.5
Nodes (2): authenticatedRequest(), logout()

### Community 5 - "Auth API & Forms"
Cohesion: 0.5
Nodes (4): Login API Endpoint, Register API Endpoint, Login Form, Registration Form

### Community 6 - "Survey System"
Cohesion: 1.0
Nodes (2): Roommate Survey Form, Survey Questions (21 questions)

### Community 7 - "Global Scripts"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **12 isolated node(s):** `Calculates a compatibility score between two users.     A lower score indicates`, `Greedy matching algorithm: finds the best available pair for each user.     Note`, `Password Change Form`, `Roommate Survey Form`, `Login API Endpoint` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Survey System`** (2 nodes): `Roommate Survey Form`, `Survey Questions (21 questions)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Global Scripts`** (1 nodes): `script.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Dashboard Page` connect `Core UI & Shared Resources` to `Profile Management & Matching`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `Roomi Brand (Ole Miss Roommate Matching)` connect `Core UI & Shared Resources` to `Auth API & Forms`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `Profile API Endpoint` connect `Profile Management & Matching` to `Core UI & Shared Resources`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Profile Page` (e.g. with `Image Cropper Tool` and `Roomi Brand (Ole Miss Roommate Matching)`) actually correct?**
  _`Profile Page` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Roomi Brand (Ole Miss Roommate Matching)` (e.g. with `Login Form` and `Registration Form`) actually correct?**
  _`Roomi Brand (Ole Miss Roommate Matching)` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Calculates a compatibility score between two users.     A lower score indicates`, `Greedy matching algorithm: finds the best available pair for each user.     Note`, `Password Change Form` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._