"""
routers/seo_cache.py

Description: Defines all HTTP endpoints related to Search Engine Optimization (SEO) and Caching.
             Delegates all business logic to search_service.py.
"""
# Standard library
import os
import re

# Third-party — Web framework
from fastapi import APIRouter

# Internal
from models import SubcodeResponse, SubcodeResult
from services.db_service import get_cached_conditions_from_db, get_sitemap_codes

router = APIRouter()


@router.get("/api/cached-conditions")
def get_cached_conditions():
    """
    GET /api/cached-conditions

    Returns all unique ICD codes that have been cached along with their titles.
    Used for generating the landing page overview and sitemap.

    Returns:
        dict: A dictionary containing a list of condition objects with
            code and title fields.

    Raises:
        HTTPException 500: If the database connection fails.
    """
    rows = get_cached_conditions_from_db()

    if not rows:
        raise HTTPException(status_code=500, detail="Database connection failed")

    results = [
        {"code": row[0], "title": row[1] or "Unbekannte Diagnose"}
        for row in rows
    ]
    return {"conditions": results}

@router.get("/sitemap.xml")
def get_sitemap():
    """
    Generates a dynamic sitemap.xml for all cached diseases
    to improve Google / Search Engine indexing.
    """
    import datetime
    from fastapi import Response

    rows = get_sitemap_codes()
    if not rows:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    # Simple slugify logic mirroring the frontend
    def slugify(text):
        if not text:
            return "diagnose"
        text = text.lower()
        text = re.sub(r'[^a-z0-9öäüß]+', '-', text) # basic german support
        text = text.replace('ö', 'oe').replace('ä', 'ae').replace('ü', 'ue').replace('ß', 'ss')
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = re.sub(r'(^-|-$)+', '', text)
        return text

    base_url = "https://medcode.ch"
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
    xml_urls = []
    xml_urls.append(f'''
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>''')
        
    # Add all cached pages
    for row in rows:
        code = row[0]
        title = row[1] or ""
        slug = slugify(title)
        url = f"{base_url}/{slug}/{code}"
        xml_urls.append(f'''
    <url>
        <loc>{url}</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>''')
            
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{''.join(xml_urls)}
</urlset>'''

    return Response(content=xml_content, media_type="application/xml")