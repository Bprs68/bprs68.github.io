#!/usr/bin/env python3
import os
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape

def clean_html(content):
    """Clean WordPress HTML content"""
    if content is None:
        return ""
        
    # Replace WordPress shortcodes and HTML blocks
    content = re.sub(r'<!-- wp:(.*?)-->', '', content)
    content = re.sub(r'<!-- /wp:(.*?)-->', '', content)
    
    # Convert <p> tags to markdown paragraphs
    content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content)
    
    # Convert <strong> tags to markdown bold
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
    
    # Convert <em> tags to markdown italic
    content = re.sub(r'<em>(.*?)</em>', r'_\1_', content)
    
    # Convert <blockquote> tags to markdown blockquotes
    content = re.sub(r'<blockquote>(.*?)</blockquote>', r'> \1', content)
    
    # Convert <ul> and <li> tags to markdown lists
    content = re.sub(r'<ul>(.*?)</ul>', r'\1', content)
    content = re.sub(r'<li>(.*?)</li>', r'* \1\n', content)
    
    # Convert <ol> and <li> tags to markdown ordered lists
    content = re.sub(r'<ol>(.*?)</ol>', r'\1', content)
    content = re.sub(r'<li value="(\d+)">(.*?)</li>', r'\1. \2\n', content)
    
    # Convert <a> tags to markdown links
    content = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', content)
    
    # Convert <img> tags to markdown images
    content = re.sub(r'<img src="(.*?)" alt="(.*?)".*?/>', r'![\2](\1)', content)
    
    # Handle figure captions
    content = re.sub(r'<figure.*?>(.*?)<figcaption.*?>(.*?)</figcaption></figure>', 
                    r'\1\n\n*\2*', content)
    
    # Remove any remaining HTML tags
    content = re.sub(r'<.*?>', '', content)
    
    # Unescape HTML entities
    content = unescape(content)
    
    return content

def create_jekyll_post(title, content, date, categories, tags, status, slug):
    """Create Jekyll formatted front matter and content"""
    # Format date for Jekyll
    if date:
        post_date = date.strftime('%Y-%m-%d')
    else:
        post_date = datetime.now().strftime('%Y-%m-%d')
        
    # Clean up categories and tags
    if categories:
        categories_str = '[' + ', '.join(f'"{cat}"' for cat in categories) + ']'
    else:
        categories_str = '[]'
        
    if tags:
        tags_str = '[' + ', '.join(f'"{tag}"' for tag in tags) + ']'
    else:
        tags_str = '[]'
    
    # Clean title
    if title:
        title = title.replace('"', '\\"')
    else:
        title = "Untitled"
    
    # Create Jekyll front matter
    front_matter = f"""---
layout: single
title: "{title}"
date: {date.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: {categories_str}
tags: {tags_str}
permalink: /{slug}/
---

"""
    
    # Clean content
    clean_content = clean_html(content)
    
    # Return complete Jekyll post
    return front_matter + clean_content

def parse_wordpress_xml(xml_file, output_dir):
    """Parse WordPress XML export and create Jekyll posts"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Parse XML
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML file: {e}")
        return
    
    # Find all posts
    namespaces = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }
    
    # Get all items (posts)
    count = 0
    
    for item in root.findall('.//item'):
        # Check if it's a post
        post_type = item.find('./wp:post_type', namespaces)
        if post_type is None or post_type.text != 'post':
            continue
        
        # Check post status
        status = item.find('./wp:status', namespaces)
        if status is None or status.text != 'publish':
            continue
            
        # Get post title
        title_elem = item.find('./title')
        title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"
        
        # Get post content
        content_elem = item.find('./content:encoded', namespaces)
        content = content_elem.text if content_elem is not None and content_elem.text else ""
        
        # Get post date
        date_elem = item.find('./wp:post_date_gmt', namespaces)
        if date_elem is not None and date_elem.text:
            try:
                date = datetime.strptime(date_elem.text, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                date = datetime.now()
        else:
            date = datetime.now()
            
        # Get post slug
        slug_elem = item.find('./wp:post_name', namespaces)
        slug = slug_elem.text if slug_elem is not None and slug_elem.text else f"post-{count}"
        
        # Get categories and tags
        categories = []
        tags = []
        
        for cat in item.findall('./category'):
            domain = cat.get('domain')
            name = cat.text
            
            if name:
                if domain == 'category':
                    categories.append(name)
                elif domain == 'post_tag':
                    tags.append(name)
        
        # Create Jekyll post
        jekyll_post = create_jekyll_post(title, content, date, categories, tags, status.text, slug)
        
        # Create filename for Jekyll post
        filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
        file_path = os.path.join(output_dir, filename)
        
        # Write Jekyll post to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(jekyll_post)
            
        count += 1
        
    print(f"Converted {count} posts to Jekyll format")

if __name__ == "__main__":
    # Replace with your WordPress export file
    wordpress_xml = "/workspaces/bprs68.github.io/_import/ withbhaskar.WordPress.2025-04-16.xml"
    
    # Replace with your desired output directory
    output_dir = "../_posts"
    
    parse_wordpress_xml(wordpress_xml, output_dir)
