import os
import sys
import sqlite3
import httpx
import fitz

def create_sample_resume(filename="sample_resume.pdf"):
    print(f"Creating sample PDF: {filename}...")
    doc = fitz.open()
    page = doc.new_page()
    
    resume_text = (
        "John Doe\n"
        "Email: john.doe@example.com\n"
        "Phone: +1-555-0199\n"
        "LinkedIn: linkedin.com/in/johndoe\n\n"
        "Summary\n"
        "Highly motivated software engineer with 3+ years of experience building web applications using modern technologies.\n\n"
        "Experience\n"
        "Software Engineer at TechCorp (2022 - Present)\n"
        "- Developed backend microservices using Python, FastAPI, and PostgreSQL.\n"
        "- Built interactive frontend dashboards using React, TypeScript, and Tailwind CSS.\n"
        "- Improved API response time by 40% using redis caching.\n\n"
        "Education\n"
        "Bachelor of Science in Computer Science\n"
        "Stanford University (2018 - 2022)\n\n"
        "Skills\n"
        "Python, React, TypeScript, FastAPI, PostgreSQL, SQL, Docker, Git"
    )
    
    rect = fitz.Rect(50, 50, 550, 750)
    page.insert_textbox(rect, resume_text, fontsize=11, fontname="helv")
    doc.save(filename)
    doc.close()
    print("Sample PDF created successfully.")

def get_verification_token_from_db(email):
    """Retrieve the verification token directly from the database for testing."""
    db_path = os.path.join(os.path.dirname(__file__), "backend", "resumatch.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT verification_token, is_verified FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def test_api():
    base_url = "http://localhost:8080"
    print(f"Testing ResuMatch AI API at {base_url}...")
    print("=" * 60)
    
    # 1. Health check
    print("\n[TEST 1] Health Check")
    try:
        r = httpx.get(f"{base_url}/health")
        print(f"  Status: {r.status_code}")
        assert r.status_code == 200, "Health check failed"
        print("  [PASS]")
    except Exception as e:
        print(f"  Error connecting to backend: {e}")
        sys.exit(1)
        
    # 2. Register user (should require verification now)
    print("\n[TEST 2] Register User (Email Verification Required)")
    email = f"verify_test_{int(os.getpid())}@example.com"
    register_payload = {
        "email": email,
        "name": "Verify Test User",
        "password": "password123"
    }
    r = httpx.post(f"{base_url}/auth/register", json=register_payload)
    print(f"  Status: {r.status_code}")
    reg_data = r.json()
    print(f"  Message: {reg_data.get('message')}")
    print(f"  Requires verification: {reg_data.get('requires_verification')}")
    assert r.status_code == 200, f"Registration failed: {reg_data}"
    assert reg_data.get("requires_verification") == True, "Expected requires_verification=True"
    print("  [PASS]")
    
    # 3. Try to login BEFORE verification (should fail with 403)
    print("\n[TEST 3] Login Before Verification (Should Fail)")
    login_payload = {
        "email": email,
        "password": "password123"
    }
    r = httpx.post(f"{base_url}/auth/login", json=login_payload)
    print(f"  Status: {r.status_code}")
    login_err = r.json()
    print(f"  Detail: {login_err.get('detail')}")
    assert r.status_code == 403, f"Expected 403 but got {r.status_code}"
    assert "verify" in login_err.get("detail", "").lower(), "Expected verification error message"
    print("  [PASS] Login correctly blocked for unverified user")
    
    # 4. Get verification token from DB and verify via endpoint
    print("\n[TEST 4] Email Verification via Token")
    db_info = get_verification_token_from_db(email)
    assert db_info is not None, "User not found in database"
    assert db_info["verification_token"] is not None, "Verification token is NULL"
    assert db_info["is_verified"] == 0, "User should not be verified yet"
    token = db_info["verification_token"]
    print(f"  Token from DB: {token[:10]}...")
    print(f"  is_verified before: {db_info['is_verified']}")
    
    # Call the verify endpoint (don't follow redirects so we can check)
    r = httpx.get(f"{base_url}/auth/verify?token={token}", follow_redirects=False)
    print(f"  Verify endpoint status: {r.status_code}")
    print(f"  Redirect location: {r.headers.get('location', 'N/A')}")
    assert r.status_code == 302, f"Expected 302 redirect but got {r.status_code}"
    assert "verified=true" in r.headers.get("location", ""), "Expected redirect with verified=true"
    
    # Confirm in DB
    db_info_after = get_verification_token_from_db(email)
    print(f"  is_verified after: {db_info_after['is_verified']}")
    print(f"  token after: {db_info_after['verification_token']}")
    assert db_info_after["is_verified"] == 1, "User should now be verified"
    assert db_info_after["verification_token"] is None, "Token should be cleared after verification"
    print("  [PASS] User successfully verified")
    
    # 5. Login AFTER verification (should succeed)
    print("\n[TEST 5] Login After Verification (Should Succeed)")
    r = httpx.post(f"{base_url}/auth/login", json=login_payload)
    print(f"  Status: {r.status_code}")
    assert r.status_code == 200, f"Login failed after verification: {r.json()}"
    login_data = r.json()
    jwt_token = login_data["token"]
    print(f"  User: {login_data['user']['email']}")
    print("  [PASS] Login successful after verification")
    
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    # 6. Get profile
    print("\n[TEST 6] Get Current User Profile")
    r = httpx.get(f"{base_url}/auth/me", headers=headers)
    print(f"  Status: {r.status_code}")
    assert r.status_code == 200, "Get profile failed"
    print("  [PASS]")
    
    # 7. Fetch Jobs
    print("\n[TEST 7] Fetch Jobs")
    r = httpx.get(f"{base_url}/jobs", headers=headers)
    print(f"  Status: {r.status_code}")
    jobs_data = r.json()
    print(f"  Jobs found: {len(jobs_data.get('jobs', []))}")
    assert r.status_code == 200, "Get jobs failed"
    print("  [PASS]")
    
    # 8. Analyze Resume
    print("\n[TEST 8] Full Resume Analysis")
    pdf_filename = "sample_resume.pdf"
    create_sample_resume(pdf_filename)
    
    with open(pdf_filename, "rb") as f:
        files = {"file": (pdf_filename, f, "application/pdf")}
        params = {"target_keywords": "React,FastAPI,Python"}
        r = httpx.post(
            f"{base_url}/analyze-resume",
            files=files,
            params=params,
            headers=headers,
            timeout=60.0
        )
        
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    print(f"  Status: {r.status_code}")
    if r.status_code != 200:
        print(f"  Error: {r.text}")
    assert r.status_code == 200, f"Resume analysis failed"
    
    analysis = r.json()
    ats = analysis.get("ats_score", {})
    skills = analysis.get("skills", {})
    print(f"  ATS Score: {ats.get('total_score')}/100 ({ats.get('grade')})")
    print(f"  Skills found: {len(skills.get('skills', []))}")
    print(f"  Career paths: {len(analysis.get('career_paths', []))}")
    print(f"  Interview questions: {analysis.get('interview_questions', {}).get('total', 0)}")
    print(f"  Rewrite suggestions: {analysis.get('rewrite_suggestions', {}).get('improvements_count', 0)}")
    print("  [PASS]")
    
    # 9. Test expired/invalid token verification
    print("\n[TEST 9] Verify with Invalid Token (Should Redirect with Error)")
    r = httpx.get(f"{base_url}/auth/verify?token=totally_invalid_fake_token_abcdefg", follow_redirects=False)
    print(f"  Status: {r.status_code}")
    redirect_url = r.headers.get("location", "")
    print(f"  Redirect: {redirect_url}")
    assert r.status_code == 302, f"Expected 302 but got {r.status_code}"
    assert "verification=expired" in redirect_url, "Expected expired verification redirect"
    print("  [PASS] Invalid token correctly handled")
    
    # 10. Logout
    print("\n[TEST 10] Logout")
    r = httpx.post(f"{base_url}/auth/logout", headers=headers)
    print(f"  Status: {r.status_code}")
    assert r.status_code == 200, "Logout failed"
    print("  [PASS]")
    
    # 11. Admin login (should work without verification since is_verified defaults to 1 for existing users)
    print("\n[TEST 11] Admin Login (Pre-verified)")
    r = httpx.post(f"{base_url}/auth/login", json={"email": "admin@resumatch.ai", "password": "admin123"})
    print(f"  Status: {r.status_code}")
    assert r.status_code == 200, f"Admin login failed: {r.json()}"
    print("  [PASS] Admin login works (pre-verified)")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All 11 tests passed! Email verification flow is working perfectly!")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
