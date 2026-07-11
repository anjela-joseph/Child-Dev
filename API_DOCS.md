# Child Development App — Backend API Reference
> Base URL: `http://localhost:8000/api`  
> All endpoints (except Register and Login) require a JWT Bearer token in the header:  
> `Authorization: Bearer <access_token>`

---

## Authentication

### Register
`POST /auth/register/`

**Body:**
```json
{
  "email": "parent@example.com",
  "username": "sarah",
  "password": "securepass123",
  "password2": "securepass123",
  "phone": "+1234567890"
}
```
**Response `201`:**
```json
{
  "email": "parent@example.com",
  "username": "sarah",
  "phone": "+1234567890"
}
```

---

### Login (Get Token)
`POST /token/`

**Body:**
```json
{
  "email": "parent@example.com",
  "password": "securepass123"
}
```
**Response `200`:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

---

### Refresh Token
`POST /token/refresh/`

**Body:**
```json
{ "refresh": "<jwt_refresh_token>" }
```
**Response `200`:**
```json
{ "access": "<new_access_token>" }
```

---

### Get My Profile
`GET /auth/me/`

**Response `200`:**
```json
{
  "id": 1,
  "email": "parent@example.com",
  "username": "sarah",
  "phone": "+1234567890",
  "created_at": "2025-01-01T10:00:00Z"
}
```

---

## Children

### List Children
`GET /auth/children/`

**Response `200`:**
```json
[
  {
    "id": 1,
    "name": "Liam",
    "date_of_birth": "2020-03-15",
    "gender": "M",
    "notes": "",
    "age_in_years": 5,
    "created_at": "2025-01-01T10:00:00Z"
  }
]
```

---

### Add a Child
`POST /auth/children/`

**Body:**
```json
{
  "name": "Liam",
  "date_of_birth": "2020-03-15",
  "gender": "M",
  "notes": ""
}
```
**Response `201`:** Same as above.

---

### Get / Update / Delete a Child
`GET /auth/children/<id>/`  
`PATCH /auth/children/<id>/`  
`DELETE /auth/children/<id>/`

---

## Milestones

### Get Full Checklist for an Age ⭐
`GET /milestones/checklist/?age=5`

This is the **main endpoint** — returns everything needed to render the checklist screen.

**Response `200`:**
```json
{
  "age": 5,
  "milestone_domains": [
    {
      "domain": "social_emotional",
      "domain_label": "Social & Emotional",
      "items": [
        {
          "id": 29,
          "age_group": 5,
          "description": "Plays in groups and takes turns more reliably.",
          "severity_if_missed": "medium",
          "concern_tags": ["asd", "adhd", "social_delay"],
          "is_red_flag": false,
          "order": 1
        }
      ]
    }
  ],
  "red_flags": [
    {
      "id": 5,
      "description": "Poor eye contact, limited social response, or not responding to name.",
      "scope": "social_communication",
      "concern_tags": ["asd"],
      "applies_to_ages": [3, 4, 5]
    }
  ]
}
```

---

### Get Red Flags for an Age
`GET /milestones/red-flags/?age=4`

---

### Get All Milestone Items (with filters)
`GET /milestones/items/?age_group=4`  
`GET /milestones/items/?age_group=5&category__domain=language_communication`

---

## Assessments

### Start a New Assessment
`POST /assessments/`

**Body:**
```json
{ "child": 1 }
```
**Response `201`:**
```json
{
  "id": 10,
  "child": 1,
  "age_at_assessment": 5,
  "status": "in_progress",
  "created_at": "2025-07-01T09:00:00Z",
  "risk_level": null
}
```

---

### Submit Assessment ⭐
`POST /assessments/<id>/submit/`

This is the **main action endpoint** — submits all responses and triggers scoring in one call. Returns the risk result immediately.

**Body:**
```json
{
  "milestone_responses": [
    { "milestone_item": 29, "response": "met", "parent_note": "" },
    { "milestone_item": 30, "response": "not_yet", "parent_note": "Still clingy at drop-off" },
    { "milestone_item": 32, "response": "emerging", "parent_note": "" }
  ],
  "red_flag_responses": [
    { "red_flag": 5, "is_present": false },
    { "red_flag": 8, "is_present": false }
  ]
}
```

**Response values for `response` field:**  
`met` | `emerging` | `not_yet` | `concerned`

**Response `200`:**
```json
{
  "assessment_id": 10,
  "risk_level": "yellow",
  "domains_with_concerns": ["social_emotional"],
  "flags": {
    "asd_pattern": false,
    "adhd_pattern": false,
    "dyslexia_pattern": false,
    "ocd_pattern": false,
    "red_flag_triggered": false
  },
  "summary_message": "Your child is doing well overall, with one area to keep an eye on..."
}
```

**Risk level values:** `green` | `yellow` | `orange` | `red`

---

### Get Assessment Detail
`GET /assessments/<id>/`

Returns the full assessment including all responses and the risk score breakdown.

**Response `200`:**
```json
{
  "id": 10,
  "child": 1,
  "age_at_assessment": 5,
  "status": "completed",
  "created_at": "2025-07-01T09:00:00Z",
  "completed_at": "2025-07-01T09:05:00Z",
  "responses": [...],
  "red_flag_responses": [...],
  "risk_score": {
    "risk_level": "yellow",
    "social_emotional_score": 1.5,
    "language_score": 0.0,
    "cognitive_score": 0.25,
    "gross_motor_score": 0.0,
    "fine_motor_score": 0.0,
    "behavior_score": 0.0,
    "flags_asd_pattern": false,
    "flags_adhd_pattern": false,
    "flags_dyslexia_pattern": false,
    "flags_ocd_pattern": false,
    "red_flag_triggered": false,
    "domains_with_concerns": ["social_emotional"],
    "summary_message": "Your child is doing well overall...",
    "calculated_at": "2025-07-01T09:05:00Z"
  }
}
```

---

### List All Assessments
`GET /assessments/`

---

### Child Progress History
`GET /assessments/child/<child_id>/history/`

Returns all completed assessments for one child in chronological order. Use this to show progress over time on the history screen.

---

## Referrals

### Get Referral Guidance After an Assessment
`GET /referrals/assessment/<assessment_id>/`

Call this after submitting an assessment to get the guidance content to show the parent.

**Response `200`:**
```json
[
  {
    "id": 3,
    "guidance": {
      "id": 2,
      "risk_level": "yellow",
      "concern_tag": "",
      "heading": "One area to keep an eye on",
      "message": "Your child is doing well overall...",
      "action_items": [
        "Revisit this checklist in 4 to 6 weeks.",
        "Mention the concern at your next pediatrician appointment."
      ],
      "suggested_specialists": ["pediatrician"]
    },
    "created_at": "2025-07-01T09:05:00Z",
    "parent_acknowledged": false,
    "acknowledged_at": null
  }
]
```

---

### Acknowledge Referral
`POST /referrals/<id>/acknowledge/`

Call this when the parent taps "I understand" on the guidance screen.

**Response `200`:**
```json
{ "acknowledged": true }
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Bad request — check your body fields |
| `401` | Missing or invalid token |
| `403` | You do not own this resource |
| `404` | Resource not found |

---

## Typical Flutter Flow

```
1. POST /token/               → get access token
2. POST /auth/children/       → add child profile
3. GET  /milestones/checklist/?age=5   → load checklist UI
4. POST /assessments/         → start assessment (get assessment id)
5. POST /assessments/<id>/submit/      → submit responses → get risk_level
6. GET  /referrals/assessment/<id>/    → load guidance screen
7. POST /referrals/<id>/acknowledge/   → parent confirms they read it
8. GET  /assessments/child/<id>/history/ → show progress over time
```
