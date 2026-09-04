# CallSense AI — Intelligent Conversation Intelligence Dashboard

## Overview
CallSense AI is a production-ready full-stack application designed to analyze customer service phone conversations. It extracts overall sentiment, sentence-level sentiment, emotional tone, and key performance indicators (KPIs) using an LLM via an n8n orchestration layer.

## Architecture
- **Frontend:** React, Vite, Tailwind CSS, Recharts (Deployed on Vercel/Netlify)
- **Backend:** Python, FastAPI, Pydantic
- **AI Orchestration:** n8n
- **AI Model:** LLM API (e.g., OpenAI, Gemini) via environment variables

## Flow
`React Frontend` → `FastAPI Backend` → `n8n Workflow` → `LLM` → `Structured JSON` → `FastAPI Validation` → `React Dashboard`

## Directory Structure
- `/frontend` - React/Vite application
- `/backend` - FastAPI Python backend
- `/n8n` - n8n workflow exports and schemas

## Getting Started
(Instructions will be added as components are implemented)
