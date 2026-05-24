"""
ResuMatch AI — Semantic Matcher
Generates embeddings via ONNX Runtime and calculates cosine similarity
between resume text and job descriptions.
Uses all-MiniLM-L6-v2 INT8 quantized model for memory efficiency.
"""

import os
import numpy as np
from typing import Optional

# Lazy-loaded model singletons
_session = None
_tokenizer = None

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model_quantized.onnx")
TOKENIZER_PATH = os.path.join(MODEL_DIR, "tokenizer.json")
MAX_SEQ_LENGTH = 256  # Reduced from 512 for memory efficiency
EMBEDDING_DIM = 384


def _get_session():
    """Lazy load ONNX inference session."""
    global _session
    if _session is None:
        import onnxruntime as ort
        
        # Configure for minimal memory usage
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.enable_mem_pattern = True
        sess_options.enable_cpu_mem_arena = False  # Disable arena to reduce peak memory
        
        if os.path.exists(MODEL_PATH):
            _session = ort.InferenceSession(MODEL_PATH, sess_options, providers=["CPUExecutionProvider"])
        else:
            raise FileNotFoundError(
                f"ONNX model not found at {MODEL_PATH}. "
                "Run quantize_model.py first to generate the model."
            )
    return _session


def _get_tokenizer():
    """Lazy load tokenizer (uses tokenizers library, not full transformers)."""
    global _tokenizer
    if _tokenizer is None:
        if os.path.exists(TOKENIZER_PATH):
            from tokenizers import Tokenizer
            _tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
            _tokenizer.enable_truncation(max_length=MAX_SEQ_LENGTH)
            _tokenizer.enable_padding(length=MAX_SEQ_LENGTH)
        else:
            # Fallback: use transformers AutoTokenizer (heavier)
            from transformers import AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    return _tokenizer


def _tokenize(text: str) -> dict:
    """Tokenize text for ONNX model input."""
    tokenizer = _get_tokenizer()
    
    # Check if it's a tokenizers.Tokenizer or transformers AutoTokenizer
    if hasattr(tokenizer, 'encode_batch'):
        # tokenizers library
        encoded = tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)
    else:
        # transformers library fallback
        encoded = tokenizer(
            text,
            max_length=MAX_SEQ_LENGTH,
            padding="max_length",
            truncation=True,
            return_tensors="np",
        )
        input_ids = encoded["input_ids"].astype(np.int64)
        attention_mask = encoded["attention_mask"].astype(np.int64)
        token_type_ids = encoded.get("token_type_ids", np.zeros_like(input_ids)).astype(np.int64)
    
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids,
    }


def _mean_pooling(model_output: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Apply mean pooling to token embeddings using attention mask."""
    # model_output shape: [batch, seq_len, hidden_size]
    # attention_mask shape: [batch, seq_len]
    mask_expanded = np.expand_dims(attention_mask, axis=-1)  # [batch, seq_len, 1]
    mask_expanded = np.broadcast_to(mask_expanded, model_output.shape).astype(np.float32)
    
    sum_embeddings = np.sum(model_output * mask_expanded, axis=1)
    sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
    
    return sum_embeddings / sum_mask


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """L2 normalize vectors."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.clip(norms, a_min=1e-9, a_max=None)
    return vectors / norms


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate a 384-dimensional embedding for the input text.
    Uses ONNX Runtime with INT8 quantized all-MiniLM-L6-v2.
    
    Returns:
        np.ndarray of shape (384,) — L2-normalized embedding vector
    """
    session = _get_session()
    inputs = _tokenize(text)
    
    # Get model input names
    input_names = [inp.name for inp in session.get_inputs()]
    
    # Build feed dict based on what the model expects
    feed = {}
    for name in input_names:
        if "input_ids" in name:
            feed[name] = inputs["input_ids"]
        elif "attention_mask" in name:
            feed[name] = inputs["attention_mask"]
        elif "token_type" in name:
            feed[name] = inputs["token_type_ids"]
    
    # Run inference
    outputs = session.run(None, feed)
    
    # outputs[0] is typically [batch, seq_len, hidden_size] or [batch, hidden_size]
    token_embeddings = outputs[0]
    
    if len(token_embeddings.shape) == 3:
        # Apply mean pooling
        embedding = _mean_pooling(token_embeddings, inputs["attention_mask"])
    else:
        embedding = token_embeddings
    
    # L2 normalize
    embedding = _normalize(embedding)
    
    return embedding[0]  # Return 1D vector


def calculate_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings.
    Both vectors should already be L2-normalized.
    """
    return float(np.dot(embedding_a, embedding_b))


def match_jobs(resume_text: str, jobs: list[dict], top_k: int = 20) -> list[dict]:
    """
    Match resume against a list of job descriptions.
    Returns jobs sorted by similarity score (highest first).
    
    Args:
        resume_text: Full resume text
        jobs: List of job dicts with at least 'description' and 'title' fields
        top_k: Number of top matches to return
    
    Returns:
        List of job dicts with added 'match_score' field (0-100)
    """
    if not jobs:
        return []
    
    # Generate resume embedding
    resume_embedding = generate_embedding(resume_text[:5000])  # Limit text length
    
    scored_jobs = []
    for job in jobs:
        # Combine title + description for better matching
        job_text = f"{job.get('title', '')} {job.get('description', '')}"[:3000]
        
        try:
            job_embedding = generate_embedding(job_text)
            similarity = calculate_similarity(resume_embedding, job_embedding)
            
            # Convert to 0-100 score (cosine similarity ranges from -1 to 1)
            match_score = round(max(0, min(100, (similarity + 1) * 50)), 1)
            
            scored_job = {**job, "match_score": match_score}
            scored_jobs.append(scored_job)
        except Exception:
            # Skip jobs that fail to encode
            scored_job = {**job, "match_score": 0}
            scored_jobs.append(scored_job)
    
    # Sort by match score descending
    scored_jobs.sort(key=lambda j: j["match_score"], reverse=True)
    
    return scored_jobs[:top_k]


def is_model_loaded() -> bool:
    """Check if the ONNX model is currently loaded."""
    return _session is not None


def model_exists() -> bool:
    """Check if the ONNX model file exists on disk."""
    return os.path.exists(MODEL_PATH)


def unload_model():
    """Explicitly unload model to free memory."""
    global _session, _tokenizer
    _session = None
    _tokenizer = None
