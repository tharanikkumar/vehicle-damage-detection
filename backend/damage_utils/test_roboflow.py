from inference_sdk import InferenceHTTPClient
import os

# Make sure this file exists and is a valid image
image_path = "../uploads/3.jpg"


if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found: {image_path}")

# Roboflow hosted API client
client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="UBP6gDsmvPFrDbUncyUP"
)

# Use the absolute path string
result = client.run_workflow(
    workspace_name="seai-sq6is",
    workflow_id="custom-workflow",
    images={
        "image": image_path  # 👈 IMPORTANT: Pass path string
    },
    use_cache=True
)

print("✅ Inference Result:\n", result)
