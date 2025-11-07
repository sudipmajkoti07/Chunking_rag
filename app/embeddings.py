from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(host="qdrant", port=6333)

COLLECTION_NAME = "document_embeddings"

# Create collection if not exists
def init_qdrant():
    try:
        qdrant.get_collection(COLLECTION_NAME)
    except:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

def store_embeddings(chunks, metadata):
    vectors = MODEL.encode(chunks).tolist()
    points = [
        PointStruct(id=i, vector=vectors[i], payload={"metadata": metadata, "text": chunks[i]})
        for i in range(len(chunks))
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
