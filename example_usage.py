"""
Example usage script for Trade Opportunities API.

This script demonstrates how to:
1. Authenticate and get a JWT token
2. Use the token to analyze a sector
3. Save the report to a file
"""

import requests
import json
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "demo_user"
PASSWORD = "demo_password"

def main():
    """Main function demonstrating API usage."""
    
    print("=" * 60)
    print("Trade Opportunities API - Example Usage")
    print("=" * 60)
    
    # Step 1: Authenticate and get token
    print("\n1. Authenticating...")
    try:
        auth_response = requests.post(
            f"{BASE_URL}/auth/login",
            auth=(USERNAME, PASSWORD),
            timeout=10
        )
        auth_response.raise_for_status()
        token_data = auth_response.json()
        token = token_data["access_token"]
        print(f"✓ Authentication successful!")
        print(f"  Token type: {token_data['token_type']}")
        print(f"  Token (first 30 chars): {token[:30]}...")
    except requests.exceptions.RequestException as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    # Step 2: Analyze a sector
    sector = "pharmaceuticals"
    print(f"\n2. Analyzing sector: {sector}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        analysis_response = requests.get(
            f"{BASE_URL}/analyze/{sector}",
            headers=headers,
            timeout=60  # Longer timeout for AI generation
        )
        analysis_response.raise_for_status()
        analysis_data = analysis_response.json()
        print(f"✓ Analysis complete!")
        print(f"  Sector: {analysis_data['sector']}")
        print(f"  Generated at: {analysis_data['generated_at']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"✗ Rate limit exceeded. Please wait before trying again.")
        else:
            print(f"✗ Analysis failed: {e.response.status_code} - {e.response.text}")
        return
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return
    
    # Step 3: Save report to file
    report = analysis_data["report"]
    output_file = Path(f"report_{sector}.md")
    
    print(f"\n3. Saving report to {output_file}...")
    try:
        output_file.write_text(report, encoding="utf-8")
        print(f"✓ Report saved successfully!")
        print(f"  File: {output_file.absolute()}")
    except Exception as e:
        print(f"✗ Failed to save report: {e}")
        return
    
    # Step 4: Display report preview
    print(f"\n4. Report Preview (first 500 characters):")
    print("-" * 60)
    print(report[:500])
    if len(report) > 500:
        print("...")
    print("-" * 60)
    
    # Step 5: Check rate limit info
    print(f"\n5. Checking rate limit status...")
    try:
        rate_limit_response = requests.get(
            f"{BASE_URL}/rate-limit-info",
            headers=headers,
            timeout=10
        )
        rate_limit_response.raise_for_status()
        rate_limit_data = rate_limit_response.json()
        print(f"✓ Rate limit info retrieved!")
        print(f"  Limit: {rate_limit_data['limit']} requests")
        print(f"  Remaining: {rate_limit_data['remaining']} requests")
        print(f"  Reset after: {rate_limit_data['reset_after']} seconds")
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get rate limit info: {e}")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

