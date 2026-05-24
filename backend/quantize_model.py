"""
ResuMatch AI — Model Quantization Script
Converts all-MiniLM-L6-v2 to INT8 quantized ONNX format.

THIS SCRIPT IS NOT NEEDED IN PRODUCTION.
Run it once locally to generate the quantized model file.

Usage:
    python quantize_model.py

Requirements (dev only):
    pip install optimum[onnxruntime] sentence-transformers torch
"""

import os
import shutil
import sys


def quantize_model():
    """Download, export, and quantize all-MiniLM-L6-v2 to INT8 ONNX."""
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    output_dir = os.path.join(os.path.dirname(__file__), "model")
    temp_dir = os.path.join(os.path.dirname(__file__), "_temp_model")
    
    print(f"[1/4] Creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Step 1: Export to ONNX
    print(f"[2/4] Exporting {model_name} to ONNX format...")
    try:
        from optimum.onnxruntime import ORTModelForFeatureExtraction
        
        model = ORTModelForFeatureExtraction.from_pretrained(
            model_name, export=True
        )
        model.save_pretrained(temp_dir)
        print(f"  → ONNX model saved to {temp_dir}")
    except ImportError:
        print("ERROR: 'optimum' package not installed.")
        print("Install with: pip install optimum[onnxruntime] torch")
        sys.exit(1)
    
    # Step 2: Quantize to INT8
    print("[3/4] Quantizing to INT8 (dynamic quantization)...")
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        input_model = os.path.join(temp_dir, "model.onnx")
        output_model = os.path.join(output_dir, "model_quantized.onnx")
        
        quantize_dynamic(
            model_input=input_model,
            model_output=output_model,
            weight_type=QuantType.QInt8,
            optimize_model=True,
        )
        
        # Report size comparison
        original_size = os.path.getsize(input_model) / (1024 * 1024)
        quantized_size = os.path.getsize(output_model) / (1024 * 1024)
        reduction = (1 - quantized_size / original_size) * 100
        
        print(f"  → Original:  {original_size:.1f} MB")
        print(f"  → Quantized: {quantized_size:.1f} MB")
        print(f"  → Reduction: {reduction:.1f}%")
    except Exception as e:
        print(f"ERROR during quantization: {e}")
        sys.exit(1)
    
    # Step 3: Copy tokenizer files
    print("[4/4] Copying tokenizer files...")
    try:
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(output_dir)
        
        # Also save the fast tokenizer JSON for the tokenizers library
        if hasattr(tokenizer, "backend_tokenizer"):
            tokenizer_json_path = os.path.join(output_dir, "tokenizer.json")
            if not os.path.exists(tokenizer_json_path):
                tokenizer.backend_tokenizer.save(tokenizer_json_path)
        
        print(f"  → Tokenizer saved to {output_dir}")
    except Exception as e:
        print(f"WARNING: Could not save tokenizer: {e}")
    
    # Cleanup temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\n✅ Quantization complete!")
    print(f"   Model: {os.path.join(output_dir, 'model_quantized.onnx')}")
    print(f"   Tokenizer: {os.path.join(output_dir, 'tokenizer.json')}")
    print("\n   These files should be committed to your repo or uploaded to your deployment.")


if __name__ == "__main__":
    quantize_model()
