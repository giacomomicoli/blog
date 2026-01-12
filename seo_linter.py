import os
import sys
import frontmatter
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION (STRICT SEO STANDARDS) ---
POSTS_DIR = 'post'

# 1. Critical Errors (Commit will fail)
CRITICAL_LIMITS = {
    'title_max': 70,       # Absolute max before it looks broken
    'title_min': 10,       # Prevents "Home" or "Test" titles
    'desc_max': 300,       # Spam prevention
    'desc_min': 10,        # Empty descriptions are useless
    'slug_max': 100,       # URLs shouldn't be paragraphs
}

# 2. Warnings (Commit proceeds, but you get a stern look)
WARNING_LIMITS = {
    'title_optimal_max': 60,  # Google's 600px pixel limit
    'desc_optimal_max': 160,  # Standard snippet limit
    'desc_optimal_min': 50,   # Ensure meaningful content
    'slug_optimal_max': 75,   # Clean URL standard
}

REQUIRED_KEYS = ['title', 'description', 'image', 'slug', 'author', 'created_at']

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def lint_file(filepath):
    errors = []
    warnings = []
    
    try:
        logger.info(f'trying to parse every post file')
        with open(filepath, 'r', encoding='utf-8') as f:
            logger.info(f'reading {f}')
            post = frontmatter.load(f)
            meta = post.metadata
            
            # 1. EXISTENCE CHECKS (Critical)
            for key in REQUIRED_KEYS:
                if key not in meta or not meta[key]:
                    errors.append(f"MISSING KEY: '{key}' is required.")

            # 2. TITLE CHECKS
            title = meta.get('title', '')
            if len(title) > CRITICAL_LIMITS['title_max']:
                errors.append(f"TITLE CRITICAL: {len(title)} chars (Max allowed: {CRITICAL_LIMITS['title_max']}).")
            elif len(title) > WARNING_LIMITS['title_optimal_max']:
                warnings.append(f"Title truncated: {len(title)} chars (Google cuts off at ~{WARNING_LIMITS['title_optimal_max']}).")
            
            if len(title) < CRITICAL_LIMITS['title_min']:
                errors.append(f"TITLE CRITICAL: Too short ({len(title)} chars).")

            # 3. DESCRIPTION CHECKS
            desc = meta.get('description', '')
            if len(desc) > CRITICAL_LIMITS['desc_max']:
                errors.append(f"DESC CRITICAL: Spam length detected ({len(desc)} chars).")
            elif len(desc) > WARNING_LIMITS['desc_optimal_max']:
                warnings.append(f"Desc truncated: {len(desc)} chars (Best is < {WARNING_LIMITS['desc_optimal_max']}).")
            
            if len(desc) < CRITICAL_LIMITS['desc_min']:
                 errors.append(f"DESC CRITICAL: Empty or near-empty.")
            elif len(desc) < WARNING_LIMITS['desc_optimal_min']:
                 warnings.append(f"Desc weak: Only {len(desc)} chars (Recommended > {WARNING_LIMITS['desc_optimal_min']}).")

            # 4. SLUG CHECKS
            slug = meta.get('slug', '')
            if not re.match(r'^[a-z0-9-]+$', str(slug)):
                errors.append(f"SLUG INVALID: '{slug}' contains forbidden characters. Use lowercase a-z, 0-9, and hyphens.")
            if len(str(slug)) > CRITICAL_LIMITS['slug_max']:
                errors.append(f"SLUG CRITICAL: URL is massively long ({len(slug)} chars).")
            elif len(str(slug)) > WARNING_LIMITS['slug_optimal_max']:
                warnings.append(f"Slug long: {len(slug)} chars. Consider shortening.")

    except Exception as e:
        errors.append(f"FILE READ ERROR: {str(e)}")

    return errors, warnings

def main():
    has_critical_errors = False
    print(f"{Colors.HEADER}🔍 STARTING SEO PRE-FLIGHT CHECK...{Colors.ENDC}")
    
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]
    
    for filename in files:
        filepath = os.path.join(POSTS_DIR, filename)
        errors, warnings = lint_file(filepath)
        
        if errors or warnings:
            print(f"\n📄 {Colors.OKBLUE}{filename}{Colors.ENDC}")
            
            # Print Errors
            for err in errors:
                print(f"   ❌ {Colors.FAIL}{err}{Colors.ENDC}")
                has_critical_errors = True
                
            # Print Warnings
            for warn in warnings:
                print(f"   ⚠️  {Colors.WARNING}{warn}{Colors.ENDC}")
    
    print("-" * 30)
    if has_critical_errors:
        print(f"{Colors.FAIL}⛔ SEO CHECK FAILED. COMMIT REJECTED.{Colors.ENDC}")
        print("Fix the ❌ errors above to proceed.")
        sys.exit(1)
    else:
        print(f"{Colors.OKGREEN}✅ SEO CHECK PASSED. Code is compliant.{Colors.ENDC}")
        sys.exit(0)

if __name__ == "__main__":
    main()
