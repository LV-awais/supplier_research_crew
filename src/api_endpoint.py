#!/usr/bin/env python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapeApiResponse
# Import your Crew AI supplier acquisition class.
from ai_suppliers.crew import AiSuppliers

app = FastAPI(
    title="Supplier Acquisition API",
    description="API endpoint to run the Crew AI supplier acquisition process.",
    version="1.0",
)

# ------------------------------
# Pydantic model for input
# ------------------------------

class RunInput(BaseModel):
    topic: str
    country:str
# ------------------------------
# Run Endpoint
# ------------------------------

@app.post("/run", summary="Run the Crew AI Process")
def run_crew(input_data: RunInput):
    """
    Run the Crew AI supplier acquisition process.
    """
    inputs = {
        "topic": input_data.topic,
        "country":input_data.country

    }
    try:
        # Call the kickoff function of your Crew AI application.
        result = AiSuppliers().crew().kickoff(inputs=inputs)
        return {"message": "Crew run completed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while running the crew: {e}")


# ------------------------------
# Run the API server if executed directly
# ------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
