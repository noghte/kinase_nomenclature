import os
from futurehouse_client import FutureHouseClient, JobNames
from pathlib import Path
from aviary.core import DummyEnv
import ldp
from dotenv import load_dotenv
load_dotenv()

client = FutureHouseClient(
    api_key=os.getenv("FUTUREHOUSE_API_KEY"),
)

# JobNames.CROW: Fast Search, Ask a question of scientific data sources, and receive a high-accuracy, cited response.
# JobNames.FALCON: Deep Search, Use a plethora of sources to deeply research. Receive a detailed, structured report as a response.
# JobNames.OWL: Precedent Search, Formerly known as HasAnyone, query if anyone has ever done something in science.

task_data = {
    "name": JobNames.CROW,
    "query": "Which protein kinases are less studied?",
    # "pdf_path": str(Path(__file__).parent / "data" / "example.pdf"),
}

print("Task data:", task_data)
task_response = client.run_tasks_until_done(task_data)
print(task_response)