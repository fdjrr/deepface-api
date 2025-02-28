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

@app.post("/face_verification")
async def face_verification(file1: UploadFile= File(...), file2: UploadFile= File(...)):
    try:
        with NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file1, NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file2:
            shutil.copyfileobj(file1.file, temp_file1)
            shutil.copyfileobj(file2.file, temp_file2)
            temp_file1.flush()
            temp_file2.flush()
            
            result = DeepFace.verify(
                img1_path=temp_file1.name,
                img2_path=temp_file2.name
            )
            
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

