# AI-Powered Restaurant Recommendation System

An intelligent, hybrid Zomato-inspired restaurant recommendation engine. It applies deterministic structured filters to candidate records (location, cuisine, rating, budget) from the public Zomato dataset, capped to control tokens, and then leverages Groq's high-speed Llama-3 inference model to rank options and generate natural-language reasoning explaining exactly why each fits the user's explicit preferences.

## 🍽️ Hybrid Intelligence & Success Criteria
- **Deterministic Filtering First**: Structured filtering on location, cuisine, minimum rating, and budget tier occurs locally before invoking any LLM, ensuring zero hallucinations or fictitious candidate listings.
- **Explainability**: Every surfaced recommendation features a natural-language rationale tailored directly to user preferences (including special notes like "family-friendly", "quick service", etc.).
- **Resilient Fallback**: Operates using a robust rating-based fallback with templated explanations if the Groq API key is missing, a rate limit (HTTP 429) occurs, or parsing fails.
- **Observe & Debug**: Tracks candidate counts, LLM query latency, prompt SHA256 hashes, and candidate IDs under a built-in `DEBUG` mode.

## 🚀 Setup & Installation
Ensure you have Python 3.9+ installed.

### Virtual Environment Setup
Clone the repository and initialize your environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Environment Configuration (`.env`)
Generate your Groq API key at the [Groq Console](https://console.groq.com/keys) and specify it in your `.env` file:
```env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
DEBUG=false
```
*Note: If no API key is specified, the application automatically runs using local rating-based fallback explanations.*

---

## 🛠️ Developer Workflow (`Makefile`)
We provide a structured `Makefile` for standard development tasks. Run these within your activated virtual environment:

- **Run CLI App**: Launch the interactive CLI prompts
  ```bash
  make run-cli
  ```
- **Run Web UI**: Launch the Streamlit dashboard
  ```bash
  make run-web
  ```
- **Run Tests**: Execute the unit and E2E integration test suite
  ```bash
  make test
  ```
- **Style Linting**: Ensure flake8 syntactical compliance and black formatting
  ```bash
  make lint
  ```
- **Clean Cache**: Remove compiled cache files and cached Parquet dataset
  ```bash
  make clean
  ```

---

## 📂 Project Architecture & Dataset
- **Hugging Face Dataset Source**: Backed by [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation). It is loaded dynamically and cached locally under `data/cache/restaurants.parquet`.
- **System Architecture**: Detailed in [`docs/architecture.md`](docs/architecture.md) (Logical layers, C4 context, Data flows, NFRs, Security, Appendix).
- **Edge Case Matrix**: Detailed in [`docs/edge-case.md`](docs/edge-case.md) (Cataloged system states, validation bounds, severity levels).
- **Implementation plan**: Detailed in [`docs/implementation-plan.md`](docs/implementation-plan.md) (Phased build deliverables and sequence dependency graphs).
- **Data Schema**: Detailed in [`docs/data-schema.md`](docs/data-schema.md) (Field lists, normalizations, and budget thresholds).
