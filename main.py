from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from face_service import analyze_face, recognize_faces, verify_faces
from storage import (
    delete_db_images,
    delete_image,
    download_db_images,
    download_image,
    get_image_path,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    img1_path: str
    img2_path: str


class RecognitionRequest(BaseModel):
    img_path: str
    db_path: str


class AnalyzeRequest(BaseModel):
    img_path: str


@app.post("/verify")
async def verify(req: VerifyRequest):
    try:
        download_image(req.img1_path)
        download_image(req.img2_path)

        img1_path = get_image_path(req.img1_path)
        img2_path = get_image_path(req.img2_path)

        result = verify_faces(img1_path, img2_path)

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        delete_image(req.img1_path)
        delete_image(req.img2_path)


@app.post("/recognition")
async def recognition(req: RecognitionRequest):
    try:
        download_image(req.img_path)
        download_db_images(req.db_path)

        img_path = get_image_path(req.img_path)
        db_path = get_image_path(req.db_path)

        persons = recognize_faces(img_path, db_path)

        result = []

        if isinstance(persons, list):
            for df in persons:
                if not df.empty:
                    for _, row in df.iterrows():
                        result.append(
                            {
                                "identity": row["identity"],
                                "threshold": float(row["threshold"]),
                                "distance": float(row["distance"]),
                            }
                        )
        else:
            for _, row in persons.iterrows():
                result.append(
                    {
                        "identity": row["identity"],
                        "threshold": float(row["threshold"]),
                        "distance": float(row["distance"]),
                    }
                )

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        delete_image(req.img_path)
        delete_db_images(req.db_path)


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        download_image(req.img_path)

        img_path = get_image_path(req.img_path)

        result = analyze_face(img_path)

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        delete_image(req.img_path)
