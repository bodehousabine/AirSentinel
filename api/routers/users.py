import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from api.core.database import get_db
from api.core.config import get_settings
from api.models.user import User
from api.auth.dependencies import get_current_user

settings = get_settings()

router = APIRouter(prefix="/users", tags=["Users"])

# Initialisation du client Supabase pour le stockage
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Télécharge un avatar vers Supabase Storage et met à jour l'URL de profil de l'utilisateur.
    - Types autorisés : JPEG, PNG, WEBP
    - Taille max : 2 Mo
    """
    # 1. Validation du type de fichier
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté. Types autorisés : {', '.join(ALLOWED_TYPES)}"
        )
    
    # 2. Validation de la taille (2 Mo = 2 * 1024 * 1024 octets)
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    if file_size > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier est trop volumineux (max 2 Mo)."
        )
    # Re-pointer vers le début pour d'éventuelles autres lectures
    await file.seek(0)
    
    # 3. Préparation du nom de fichier unique
    file_ext = file.filename.split(".")[-1]
    file_name = f"{current_user.id}_{uuid.uuid4().hex}.{file_ext}"
    path_on_supabase = f"avatars/{file_name}"
    
    # 4. Upload vers Supabase Storage
    try:
        # On utilise le bucket 'profile-pictures' configuré manuellement par l'utilisateur
        bucket_name = "profile-pictures"
        
        # Note: supabase-py v2 supporte storage.from_(bucket).upload()
        # On passe les octets (contents) directement
        res = supabase.storage.from_(bucket_name).upload(
            path=path_on_supabase,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        # 5. Récupération de l'URL publique
        public_url_res = supabase.storage.from_(bucket_name).get_public_url(path_on_supabase)
        public_url = public_url_res
        
        # 6. Mise à jour de l'utilisateur dans la base de données
        current_user.avatar_url = public_url
        await db.commit()
        await db.refresh(current_user)
        
        return {"avatar_url": public_url}
        
    except Exception as e:
        # Gérer les erreurs Supabase
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload vers Supabase : {str(e)}"
        )
