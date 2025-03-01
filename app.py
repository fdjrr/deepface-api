import os
import shutil
from tempfile import NamedTemporaryFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

from fastapi import FastAPI, File, UploadFile

from deepface import DeepFace

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index():
    return {"message": "DeepFace API"}

@app.post("/verify")
async def face_verify(img1: UploadFile= File(...), img2: UploadFile= File(...)):
    try:
        with NamedTemporaryFile(delete=True, suffix=".jpg") as temp_img1, NamedTemporaryFile(delete=True, suffix=".jpg") as temp_img2:
            shutil.copyfileobj(img1.file, temp_img1)
            shutil.copyfileobj(img2.file, temp_img2)
            temp_img1.flush()
            temp_img2.flush()
            
            result = DeepFace.verify(
                img1_path=temp_img1.name,
                img2_path=temp_img2.name
            )
            
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": str(e)})

@app.post('/anti-spoofing')
async def face_anti_spoofing(img: UploadFile= File(...)):
    try:
        with NamedTemporaryFile(delete=True, suffix=".jpg") as temp_img:
            shutil.copyfileobj(img.file, temp_img)
            temp_img.flush()

            face_objs = DeepFace.extract_faces(
                img_path=temp_img.name,
                anti_spoofing = True
            )
        
        if face_objs:
            result = face_objs[0]

            print(result)

            return {
                "success": True,
                "result": {
                    "confidence": result["confidence"],
                    "is_real": result["is_real"],
                    'antispoof_score': result['antispoof_score']
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": str(e)})

@app.post('/analyze')
async def face_analyze(img: UploadFile= File(...)):
    try:
        with NamedTemporaryFile(delete=True, suffix=".jpg") as temp_img:
            shutil.copyfileobj(img.file, temp_img)
            temp_img.flush()

            face_objs = DeepFace.analyze(
                img_path=temp_img.name
            )
        
        if face_objs:
            result = face_objs[0]

            return {
                "success": True,
                "result": result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": str(e)})

@app.post("/face-recognition")
async def face_recognition(img: UploadFile= File(...), path: str = "db"):
    try:
        with NamedTemporaryFile(delete=True, suffix=".jpg") as temp_img:
            shutil.copyfileobj(img.file, temp_img)
            temp_img.flush()

            dfs = DeepFace.find(
                img_path=temp_img.name,
                db_path=path
            )

        if dfs and isinstance(dfs, list) and len(dfs) > 0:
            result = [df.to_dict(orient="records") for df in dfs]

            return {
                "success": True,
                "matches": result
            }
        else:
            return {
                "success": False,
                "message": "No face match found."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": str(e)})

@app.post("/upload-db")
async def upload_db(img: UploadFile= File(...), dir: str = "db"):
    try:
        os.makedirs(dir, exist_ok=True)

        img_path = os.path.join(dir, img.filename)
        with open(img_path, "wb") as f:
            shutil.copyfileobj(img.file, f)

        return {
            "success": True,
            "message": f"Gambar '{img.filename}' berhasil diunggah ke folder '{dir}/'",
            "path": img_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": str(e)})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

