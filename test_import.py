import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
try:
    from app import app
    print("Flask import OK!")
    print("Routes:", len(app.url_map._rules))
    for rule in sorted(app.url_map._rules, key=lambda r: r.rule):
        print(f"  {rule.rule} -> {rule.endpoint}")
    print("\nImport test PASSED.")
except Exception as e:
    print(f"Import FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)