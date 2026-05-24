"""
ResuMatch AI — Memory Manager
Utilities for explicit memory cleanup and monitoring.
Critical for staying under 512MB RAM on free-tier hosting.
"""

import gc
import os
from contextlib import contextmanager
from typing import Optional


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        # Fallback for systems without psutil
        return -1.0


def cleanup():
    """
    Perform aggressive memory cleanup.
    Call after each request to prevent memory leaks.
    """
    gc.collect()
    
    # Force gc of unreachable objects
    gc.collect(generation=2)


def log_memory(label: str = ""):
    """Log current memory usage with optional label."""
    mb = get_memory_usage_mb()
    if mb >= 0:
        print(f"[Memory] {label}: {mb:.1f} MB")
    return mb


@contextmanager
def memory_guard(label: str = "operation", max_mb: float = 450.0):
    """
    Context manager that tracks memory before/after an operation
    and performs cleanup if memory exceeds threshold.
    
    Usage:
        with memory_guard("resume_analysis"):
            result = analyze_resume(pdf_bytes)
    """
    before = get_memory_usage_mb()
    try:
        yield
    finally:
        after = get_memory_usage_mb()
        delta = after - before
        
        if delta > 10:  # Log if more than 10MB was used
            print(f"[Memory] {label}: {before:.1f}MB → {after:.1f}MB (Δ{delta:+.1f}MB)")
        
        if after > max_mb:
            print(f"[Memory] WARNING: {after:.1f}MB exceeds {max_mb}MB threshold. Running cleanup...")
            cleanup()
            
            # Unload models if still too high
            final = get_memory_usage_mb()
            if final > max_mb:
                _emergency_unload()
                cleanup()
                print(f"[Memory] Emergency unload complete: {get_memory_usage_mb():.1f}MB")


def _emergency_unload():
    """Emergency: unload all ML models to free memory."""
    try:
        from matcher import unload_model as unload_matcher
        unload_matcher()
    except ImportError:
        pass
    
    try:
        from skill_extractor import unload_model as unload_spacy
        unload_spacy()
    except ImportError:
        pass


def get_system_info() -> dict:
    """Get system memory and resource info."""
    info = {
        "process_memory_mb": round(get_memory_usage_mb(), 1),
        "python_gc_counts": gc.get_count(),
        "python_gc_threshold": gc.get_threshold(),
    }
    
    try:
        import psutil
        vm = psutil.virtual_memory()
        info["system_total_mb"] = round(vm.total / (1024 * 1024), 1)
        info["system_available_mb"] = round(vm.available / (1024 * 1024), 1)
        info["system_percent_used"] = vm.percent
    except ImportError:
        pass
    
    return info
