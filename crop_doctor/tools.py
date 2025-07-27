import hashlib
from typing import Dict
from google.cloud import firestore

db = firestore.Client()

class _Done(Exception):
    """Signals the ADK runtime that the turn is complete."""
    pass

def store_crop_analysis(analysis_text: str) -> Dict[str, str]:
    """
    Persist the analysis text in Firestore only once (idempotent),
    then raise _Done to force an immediate exit.
    """
    doc_id = hashlib.sha256(analysis_text.encode()).hexdigest()[:20]
    ref = db.collection("crop_analysis").document(doc_id)

    if not ref.get().exists:
        ref.set(
            {   
                "analysis": analysis_text,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )

    # Stop the turn right here
    raise _Done({"doc_id": doc_id})