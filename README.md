# Fake Job Detector

An AI-powered system that detects fraudulent job postings using a hybrid approach combining rule-based pattern matching, machine learning, domain verification, and community reporting.

## Live Deployment

- Backend API: https://fake-job-detector-backend-pzxt.onrender.com
- Health Check: https://fake-job-detector-backend-pzxt.onrender.com/

Job seekers in India are frequently targeted by fraudulent job postings on WhatsApp, Telegram, and social media — fake recruiters demanding upfront "registration fees," promising unrealistic salaries, and using urgency tactics to pressure victims. This system analyzes job post text and returns a scam risk score with explainable reasoning.

## Architecture

```
Flutter App  →  Django REST API  →  PostgreSQL (Neon)
                      ↓
            Analysis Engine
            ├── Rule-Based Pattern Matcher
            ├── ML Model (TF-IDF + Logistic Regression)
            ├── Domain Verification (WHOIS/DNS)
            └── Community Report Aggregation
```

## Tech Stack

**Backend:** Django, Django REST Framework, JWT Authentication, PostgreSQL
**ML:** scikit-learn, pandas, TF-IDF Vectorization, Logistic Regression, SMOTE
**Frontend:** Flutter, Provider (state management), SharedPreferences
**Deployment:** Render (backend), Neon (database)

## How It Works

Each submitted job post is analyzed through four independent signals, then combined into a single risk score:

1. **Rule-based detection** — regex pattern matching for known scam indicators: upfront payment requests, urgency language, unrealistic salary claims, suspicious contact methods (WhatsApp/Telegram-only), and registration fees.

2. **ML classification** — a Logistic Regression model trained on 17,880 labeled job postings (Kaggle Employment Scam dataset), using TF-IDF features. The original dataset was heavily imbalanced (95% genuine, 5% fake); SMOTE oversampling was applied to the minority class before training.

3. **Domain verification** — extracts the company email domain from the post and checks DNS resolution, MX records, and domain registration age via WHOIS. Newly registered or non-existent domains increase the risk score.

4. **Community signal** — posts reported as scams by 3+ independent users get flagged, and structurally similar future posts inherit a risk boost.

The combined score weights ML output at 60% and rule-based output at 40%, with additional boosts from domain and community signals.

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|--------------|
| `/api/auth/register/` | POST | No | Create account |
| `/api/auth/login/` | POST | No | Get JWT tokens |
| `/api/analyze/` | POST | Yes | Analyze a job post |
| `/api/history/` | GET | Yes | Get user's past analyses |
| `/api/report/` | POST | Yes | Report a post as a scam |

### Example Request

```json
POST /api/analyze/
{
  "title": "Work from home job",
  "content": "Urgent hiring. Earn 5000 daily. Registration fee 999 rupees. Contact WhatsApp only.",
  "source": "Telegram"
}
```

### Example Response

```json
{
  "analysis": {
    "scam_score": 97,
    "risk_level": "High",
    "reasons": [
      "Upfront payment detected",
      "Urgency language found",
      "Unrealistic salary mentioned",
      "Contact via WhatsApp/Telegram only",
      "ML model confidence: 95%",
      "Key flagged words: earn, urgent, hiring, apply, fee"
    ]
  }
}
```

## Key Technical Decisions

**Why combine rules and ML instead of using ML alone?**
Rule-based detection is fully explainable and catches known patterns instantly with zero training data. ML generalizes to scam phrasing the rules don't explicitly cover. Combining both gives interpretable reasoning (required for user trust) alongside the ML model's pattern generalization.

**Why optimize for recall over precision on the fake-job class?**
A false negative (missing a real scam) results in financial harm to the user. A false positive (flagging a genuine post) costs only minor inconvenience. Given this asymmetry, the model is tuned to catch more scams even at the cost of occasional over-flagging.

**Why SMOTE instead of just collecting more fake job data?**
The original dataset had only 866 fake job examples against 17,014 genuine ones. Manually collecting thousands more real-world labeled scam examples was infeasible in the project timeline. SMOTE synthetically generates minority-class examples by interpolating between existing ones, which improved recall on the fake class from 0.46 to 0.99 without requiring additional real-world data collection.

## Known Limitations

- The base dataset is predominantly Western/US job postings; Indian-specific scam phrasing (e.g. "lakh," "WhatsApp only," "refer and earn") is partially covered by custom rule patterns added separately, not by the ML model's original training data.
- Domain verification (WHOIS/DNS) adds 1-3 seconds of latency per request and is not cached, so repeated checks on the same domain are redundant.
- SMOTE-balanced training data is partially synthetic; real-world generalization beyond the test set has not been independently validated against a held-out set of authentic Indian scam posts.

## Future Improvements

- Replace TF-IDF + Logistic Regression with a transformer-based model (e.g. DistilBERT) for better contextual understanding
- Add OCR support to analyze scam screenshots shared via WhatsApp/Telegram
- Cache domain verification results to reduce redundant WHOIS lookups
- Multilingual support for regional language job scams

## Setup

### Backend
```bash
git clone https://github.com/afroz7973/fake-job-detector-backend.git
cd fake-job-detector
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
git clone <flutter-repo-url>
cd fake_job_detector_app
flutter pub get
flutter run
```