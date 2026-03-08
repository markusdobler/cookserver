import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Optional
from ..models.job import Job, JobStatus


class ImportService:
    def __init__(self, cook_path: str, recipes_dir: str):
        self.cook_path = cook_path
        self.recipes_dir = Path(recipes_dir)
        self.jobs: Dict[str, Job] = {}
        
        # Ensure recipes directory exists
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
    
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
                [self.cook_path, job.url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Cook command failed: {result.stderr}")
            
            # Parse the output to extract title
            content = result.stdout
            title = self._extract_title(content)
            
            # Sanitize filename and add .cook extension
            filename = self._sanitize_filename(title) + ".cook"
            
            # Handle duplicate filenames
            filename = self._get_unique_filename(filename)
            
            # Write to file
            file_path = self.recipes_dir / filename
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
    
    def _get_unique_filename(self, filename: str) -> str:
        """Generate unique filename by adding numeric suffix if needed"""
        base_path = self.recipes_dir / filename
        
        if not base_path.exists():
            return filename
        
        # Split filename and extension
        name_without_ext = filename[:-5]  # Remove .cook
        ext = ".cook"
        
        # Try adding numeric suffixes
        counter = 1
        while True:
            new_filename = f"{name_without_ext}-{counter}{ext}"
            new_path = self.recipes_dir / new_filename
            if not new_path.exists():
                return new_filename
            counter += 1
