# Project Context: AI-Powered Restaurant Recommendation System

This document captures the full context from the project problem statement. Use it as the single source of truth for scope, workflow, and deliverables when building or extending this system.

## Overview

Build an **AI-powered restaurant recommendation service** inspired by **Zomato**. The system suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations.

## Primary Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and optional extras)
2. Uses a real-world restaurant dataset
3. Leverages an LLM to generate personalized, natural-language recommendations
4. Displays clear, useful results to the user

## Data Source

| Item | Detail |
|------|--------|
| Dataset | Zomato restaurant data on Hugging Face |
| URL | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| Expected fields | Restaurant name, location, cuisine, cost, rating, and related attributes |

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract relevant fields: restaurant name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect preferences from the user:

| Preference | Examples / notes |
|------------|------------------|
| Location | Delhi, Bangalore, etc. |
| Budget | low, medium, high |
| Cuisine | Italian, Chinese, etc. |
| Minimum rating | Numeric or threshold filter |
| Additional | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant records that match user input
- Pass structured, filtered results into an LLM prompt
- Design a prompt that enables the LLM to **reason** and **rank** options

### 4. Recommendation Engine (LLM)

The LLM should:

- Rank restaurants against user preferences
- Explain why each recommendation fits
- Optionally summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format. Each result should include:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation (why it was recommended)

## Architecture Summary

```
[Hugging Face Dataset] → [Preprocess / Filter] → [Structured candidates]
                                                        ↓
[User preferences] ─────────────────────────────→ [LLM prompt + ranking]
                                                        ↓
                                              [Formatted recommendations]
```

## Key Design Constraints

- **Hybrid approach**: Deterministic filtering on structured data first; LLM for ranking, explanation, and optional summary—not as the sole data source.
- **Explainability**: Every top recommendation should include an LLM-generated rationale tied to user preferences.
- **Usability**: Output must be readable and actionable (not raw JSON or model dumps unless wrapped in a clear UI).

## Out of Scope (unless extended later)

The problem statement does not specify:

- Deployment platform (web, CLI, API)
- Specific LLM provider or model
- Authentication or user accounts
- Real-time Zomato API integration (dataset-only)

Clarify these when implementing; defaults can be a simple local app (CLI or web) with one configurable LLM backend.

## Success Criteria

The project is complete when a user can:

1. Enter location, budget, cuisine, minimum rating, and optional preferences
2. Receive a ranked list of restaurants from the Zomato dataset that match filters
3. See name, cuisine, rating, cost, and a personalized explanation per recommendation
4. Understand why each option was suggested without reading raw model internals

## Reference

- Original problem statement: `docs/problemstatement.txt`
