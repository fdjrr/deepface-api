import os
import shutil

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from deepface import DeepFace
from middlewares.api_key import verify_api_key
from utils.minio_client import download_file, list_files

load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FaceRecognitionRequest(BaseModel):
    img_path: str
    db_path: str


def is_real_face_with_deepface(img_path: str) -> bool:
    try:
        analysis = DeepFace.analyze(
            img_path=img_path,
            actions=["gender"],
            enforce_detection=False,
            detector_backend="retinaface",
            anti_spoofing=True,
        )

        print(analysis)

        return analysis
    except Exception as e:
        print("Anti-spoofing detection failed:", e)
        return False


@app.post("/face-recognition")
async def recognize_face(
    payload: FaceRecognitionRequest, _: None = Depends(verify_api_key)
):
    bucket_name = os.getenv("MINIO_BUCKET_NAME")
    temp_dir = os.getenv("TEMP_DIR", "tmp")

    local_img_path = os.path.join(temp_dir, payload.img_path)

    try:
        download_file(bucket_name, payload.img_path, local_img_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {e}")

    if not is_real_face_with_deepface(local_img_path):
        return {"matched": False, "message": "Spoofing detected (fake image)"}

    local_db_path = os.path.join(temp_dir, payload.db_path)
    os.makedirs(local_db_path, exist_ok=True)

    try:
        for obj in list_files(bucket_name, payload.db_path):
            rel_path = obj.object_name
            local_file_path = os.path.join(temp_dir, rel_path)
            download_file(bucket_name, rel_path, local_file_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Database download failed: {e}")

    try:
        result = DeepFace.find(
            img_path=local_img_path,
            db_path=local_db_path,
            enforce_detection=False,
            detector_backend="retinaface",
        )
        if result and len(result) > 0 and not result[0].empty:
            match = result[0].iloc[0].to_dict()
            return {"matched": True, "result": match}
        else:
            return {"matched": False, "message": "No match found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for folder in [payload.img_path, payload.db_path]:
            full_dir_path = os.path.join(temp_dir, os.path.dirname(folder))
            if os.path.exists(full_dir_path):
                shutil.rmtree(full_dir_path, ignore_errors=True)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1234, reload=True)
