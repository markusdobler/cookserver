import os
import re
import subprocess
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse
import requests

from ..models.job import Job, JobStatus

logger = logging.getLogger(__name__)


class ImportService:
    def __init__(self, import_cli_tool: str, recipes_import_dir: str, images_import_dir: str):
        self.import_cli_tool = import_cli_tool
        self.recipes_import_dir = Path(recipes_import_dir)
        self.images_import_dir = Path(images_import_dir)
        self.jobs: Dict[str, Job] = {}
        
        # Ensure directories exist
        self.recipes_import_dir.mkdir(parents=True, exist_ok=True)
        self.images_import_dir.mkdir(parents=True, exist_ok=True)
    
    def create_job(self, url: str) -> Job:
        """Create a new import job"""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            status=JobStatus.PENDING,
            url=url
        )
        self.jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def process_import(self, job_id: str):
        """Process the import job (runs in background)"""
        job = self.jobs.get(job_id)
        if not job:
            return
        
        try:
            # Update status to processing
            job.status = JobStatus.PROCESSING
            
            # Execute cook import command
            result = subprocess.run(
                [self.import_cli_tool, job.url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Cook command failed: {result.stderr}")
            
            # Parse the output
            content = result.stdout
            
            # Try to download image if present in frontmatter
            image_url = self._extract_image_url(content)
            if image_url:
                logger.info(f"Found image URL in recipe: {image_url}")
                relative_path = self._download_image(image_url)
                if relative_path:
                    # Update frontmatter with relative path
                    content = self._update_frontmatter_image(content, relative_path)
                    logger.info(f"Updated frontmatter image path to: {relative_path}")
            
            # Extract title for filename
            title = self._extract_title(content)
            
            # Sanitize filename and add .cook extension
            filename = self._sanitize_filename(title) + ".cook"
            
            # Create file_path with unique filename
            file_path = self._get_unique_filename(self.recipes_import_dir / filename)
            
            # Write to file
            file_path.write_text(content, encoding="utf-8")
            
            # Update job status
            job.status = JobStatus.COMPLETED
            job.filename = filename
            
        except subprocess.TimeoutExpired:
            job.status = JobStatus.FAILED
            job.error = "Import command timed out"
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
    
    def _extract_title(self, content: str) -> str:
        """Extract title from recipe frontmatter"""
        # Look for title in frontmatter (between --- markers)
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip().strip('"\'')
        
        # Fallback to "Untitled Recipe"
        return "Untitled Recipe"
    
    def _extract_image_url(self, content: str) -> Optional[str]:
        """Extract image URL from recipe frontmatter"""
        # Look for image in frontmatter (between --- markers)
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            image_match = re.search(r'^image:\s*(.+)$', frontmatter, re.MULTILINE)
            if image_match:
                url = image_match.group(1).strip().strip('"\'')
                # Only return if it's a valid HTTP(S) URL
                if url.startswith(('http://', 'https://')):
                    return url
        
        return None
    
    def _get_image_extension(self, url: str, response: requests.Response = None) -> str:
        """
        Determine image file extension.
        Priority: URL extension > Content-Type header > default .jpg
        """
        # Try URL extension first
        parsed = urlparse(url)
        _, ext = os.path.splitext(parsed.path)
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
        if ext.lower() in valid_extensions:
            return ext.lower()
        
        # Fallback to Content-Type if response provided
        if response:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            mime_to_ext = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/svg+xml': '.svg',
                'image/bmp': '.bmp'
            }
            if content_type in mime_to_ext:
                return mime_to_ext[content_type]
        
        # Default fallback
        return '.jpg'
    
    def _download_image(self, url: str) -> Optional[str]:
        """
        Download image from URL and save to images directory.
        Returns relative path (images/filename.ext) on success, None on failure.
        """
        try:
            # Download image with timeout
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Detect extension from response
            ext = self._get_image_extension(url, response)
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}{ext}"
            dest_path = self.images_import_dir / filename
            
            # Write file in chunks
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Downloaded image from {url} to {filename}")
            return f"images/{filename}"
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout downloading image from {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading image from {url}: {e}")
            return None
    
    def _update_frontmatter_image(self, content: str, new_path: str) -> str:
        """
        Replace image URL in frontmatter with relative path.
        """
        # Find and replace image URL in frontmatter
        pattern = r'^(image:\s*)https?://[^\s]+$'
        replacement = rf'\1{new_path}'
        
        updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        return updated_content
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title to create a valid filename"""
        # Convert to lowercase
        filename = title.lower()
        
        # Replace spaces with hyphens
        filename = filename.replace(" ", "-")
        
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Remove leading/trailing dots and hyphens
        filename = filename.strip('.-')
        
        # Limit length (leave room for .cook extension and potential numeric suffix)
        max_length = 240
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        # Ensure we have a valid filename
        if not filename:
            filename = "recipe"
        
        return filename
    
    def _get_unique_filename(self, path: Path) -> Path:
        """Generate unique filename by adding numeric suffix if needed"""
        
        if not path.exists():
            return path
        
        # Try adding numeric suffixes
        counter = 1
        while True:
            new_filename = f"{path.stem}-{counter}{path.suffix}"
            new_path = path.parent / new_filename
            if not new_path.exists():
                return new_path
            counter += 1
