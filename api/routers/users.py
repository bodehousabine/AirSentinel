import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from api.core.database import get_db
from api.core.config import get_settings
from api.models.user import User
from api.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

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
    
    # 4. Upload vers Supabase Storage (Tentatives sur plusieurs buckets)
    bucket_name = "profile-pictures" # Nom initial
    buckets_to_try = [bucket_name, "avatars", "profile"]
    last_error = ""
    upload_success = False
    final_bucket = bucket_name
    
    try:
        for b in buckets_to_try:
            try:
                supabase.storage.from_(b).upload(
                    path=path_on_supabase,
                    file=contents,
                    file_options={"content-type": file.content_type}
                )
                upload_success = True
                final_bucket = b
                break
            except Exception as e:
                last_error = str(e)
                continue
        
        if not upload_success:
            # Gérer les erreurs Supabase de façon plus explicite
            error_msg = last_error
            if "bucket_not_found" in error_msg.lower() or "bucket not found" in error_msg.lower():
                error_msg = f"Aucun bucket valide trouvé (tentés : {', '.join(buckets_to_try)}). Veuillez en créer un dans Supabase."
            elif "policy" in error_msg.lower():
                error_msg = "Erreur de permissions (RLS Policy) sur Supabase. L'accès en écriture est refusé."

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur Supabase : {error_msg}"
            )

        # 5. Récupération de l'URL publique
        public_url = str(supabase.storage.from_(final_bucket).get_public_url(path_on_supabase))
        
        # 6. Mise à jour de l'utilisateur dans la base de données
        current_user.avatar_url = public_url
        await db.commit()
        await db.refresh(current_user)
        
        return {"avatar_url": public_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de l'upload : {str(e)}"
        )
class SubscriptionUpdate(BaseModel):
    subscribed_city: Optional[str] = None

@router.put("/me/subscription")
async def update_subscription(
    payload: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour la ville d'abonnement pour les alertes mail en temps réel.
    """
    current_user.subscribed_city = payload.subscribed_city
    # Réinitialiser le cool-down si on change de ville pour être averti immédiatement
    current_user.last_alert_sent = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "status": "success",
        "subscribed_city": current_user.subscribed_city,
        "message": f"Vous êtes maintenant abonné aux alertes pour {payload.subscribed_city or 'aucune ville'}"
    }
