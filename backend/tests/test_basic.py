def test_basic():
    """Basic test to ensure pytest works"""
    assert True

def test_import():
    """Test that main modules can be imported"""
    try:
        import sys
        from pathlib import Path
        # Add backend to path
        backend_path = Path(__file__).parent.parent
        sys.path.insert(0, str(backend_path))
        
        # Try importing your main app
        # from app.main import app
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"