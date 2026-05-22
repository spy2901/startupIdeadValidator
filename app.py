from fastapi import FastAPI, Query, HTTPException
from agent import analyze_market

app = FastAPI(
    title="Startup Idea Validator",
    description="Analyzes product-market fit for startup ideas using AI.",
    version="1.0.0",
)


@app.get("/analyze")
def analyze(
    startup_idea: str = Query(..., description="Your startup idea"),
    target_audience: str = Query(..., description="Target audience or subreddit (e.g. r/running)"),
):
    try:
        return analyze_market(idea=startup_idea, audience=target_audience)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mistral API error: {str(e)}")
