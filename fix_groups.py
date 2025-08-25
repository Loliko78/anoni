#!/usr/bin/env python3
import re

def fix_group_searches():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences of .encode('utf-8') in group searches
    content = re.sub(
        r"Group\.query\.filter_by\(invite_link_enc=invite_link\.encode\('utf-8'\)\)\.first\(\)",
        "Group.query.filter_by(invite_link_enc=invite_link).first()",
        content
    )
    
    # Also fix any other similar patterns
    content = re.sub(
        r"invite_link_enc=([^)]+)\.encode\('utf-8'\)",
        r"invite_link_enc=\1",
        content
    )
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed group searches")

if __name__ == '__main__':
    fix_group_searches()