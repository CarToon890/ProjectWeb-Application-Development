import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
import httpx

from app.auth import get_current_user
from app.models import User
from app.schemas import UploadResponse

router = APIRouter()

UPLOAD_DIR = Path("frontend/uploads")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/uploads", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "รองรับเฉพาะไฟล์รูปภาพ (jpeg, png, webp, gif)")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "ไฟล์ใหญ่เกินไป (จำกัด 5MB)")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    # Supabase Storage Support (Production / Cloud)
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = os.environ.get("SUPABASE_KEY", "").strip() or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    supabase_bucket = os.environ.get("SUPABASE_BUCKET", "uploads").strip()

    if supabase_url and supabase_key:
        try:
            clean_base_url = supabase_url.rstrip("/")
            endpoint = f"{clean_base_url}/storage/v1/object/{supabase_bucket}/{filename}"
            headers = {
                "Authorization": f"Bearer {supabase_key}",
                "apikey": supabase_key,
                "Content-Type": file.content_type or "application/octet-stream",
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(endpoint, content=contents, headers=headers)
                if res.status_code not in (200, 201):
                    raise HTTPException(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        f"อัปโหลดไปยัง Supabase Storage ไม่สำเร็จ ({res.status_code}): {res.text}",
                    )
            public_url = f"{clean_base_url}/storage/v1/object/public/{supabase_bucket}/{filename}"
            return UploadResponse(url=public_url)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"เกิดข้อผิดพลาดในการเชื่อมต่อ Supabase Storage: {str(e)}",
            )

    # Local fallback (Development)
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (UPLOAD_DIR / filename).write_bytes(contents)
        return UploadResponse(url=f"/uploads/{filename}")
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"ไม่สามารถบันทึกไฟล์ลงดิสก์ได้: {str(e)}",
        )
