import httpx
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.models.resume import Resume
from app.services.ai_service import AIService
from app.utils.exceptions import AppException


REMOTEOK_API_URL = "https://remoteok.com/api"


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    async def discover_jobs_for_user(self, user_id: str) -> List[Job]:
        # 1. Get the user's resume
        resume = self.db.query(Resume).filter(Resume.user_id == user_id).first()
        if not resume or not resume.raw_text:
            raise AppException(
                status_code=400,
                message="Please upload your resume first before discovering jobs."
            )

        user_skills = resume.skills or []

        # 2. Fetch jobs from RemoteOK
        raw_jobs = await self._fetch_remoteok_jobs()

        # 3. Filter jobs that are relevant to user's skills
        filtered_jobs = self._filter_relevant_jobs(raw_jobs, user_skills)

        # 4. Score each job against the resume using AI and save to DB
        saved_jobs = []
        for job_data in filtered_jobs[:5]:  # Limit to 5 jobs to save AI credits
            try:
                # Check if this job URL already exists for this user
                existing = self.db.query(Job).filter(
                    Job.user_id == user_id,
                    Job.url == job_data.get("url", "")
                ).first()

                if existing:
                    continue  # Skip duplicates

                # Score with AI
                match_result = await self.ai_service.score_job_match(
                    resume_text=resume.raw_text,
                    job_title=job_data["title"],
                    job_description=job_data["description"],
                )

                # Save to DB
                new_job = Job(
                    user_id=user_id,
                    title=job_data["title"],
                    company=job_data.get("company"),
                    location=job_data.get("location", "Remote"),
                    description=job_data["description"],
                    url=job_data.get("url"),
                    source="remoteok",
                    match_score=match_result.get("match_score", 0),
                    matching_skills=match_result.get("matching_skills", []),
                    missing_skills=match_result.get("missing_skills", []),
                    status=JobStatus.NEW,
                )

                self.db.add(new_job)
                self.db.commit()
                self.db.refresh(new_job)
                saved_jobs.append(new_job)

                print(f"Saved job: {new_job.title} at {new_job.company} (score: {new_job.match_score})")

            except Exception as e:
                print(f"Failed to process job '{job_data.get('title')}': {e}")
                continue

        return saved_jobs

    async def _fetch_remoteok_jobs(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    REMOTEOK_API_URL,
                    headers={"User-Agent": "ApplyFlowAI/1.0"},
                    timeout=15.0,
                )
                response.raise_for_status()
                data = response.json()

                # RemoteOK returns a list where the first item is metadata, skip it
                jobs = data[1:] if len(data) > 1 else []

                return [
                    {
                        "title": job.get("position", "Unknown"),
                        "company": job.get("company", "Unknown"),
                        "location": job.get("location", "Remote"),
                        "description": job.get("description", ""),
                        "url": job.get("url", ""),
                    }
                    for job in jobs
                    if job.get("position")
                ]

        except Exception as e:
            print(f"Failed to fetch from RemoteOK: {e}")
            raise AppException(
                status_code=502,
                message=f"Failed to fetch jobs from RemoteOK: {str(e)}"
            )

    def _filter_relevant_jobs(
        self,
        jobs: List[Dict[str, Any]],
        user_skills: List[str],
    ) -> List[Dict[str, Any]]:
        if not user_skills:
            return jobs[:10]  # No skills to filter by, return first 10

        skill_set = {s.lower() for s in user_skills}

        scored = []
        for job in jobs:
            text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            hits = sum(1 for skill in skill_set if skill in text)
            if hits > 0:
                scored.append((hits, job))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [job for _, job in scored[:10]]

    def get_matched_jobs(self, user_id: str) -> List[Job]:
        return (
            self.db.query(Job)
            .filter(Job.user_id == user_id)
            .order_by(Job.match_score.desc().nullslast())
            .all()
        )

    def get_job_by_id(self, job_id: str, user_id: str) -> Job:
        job = self.db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user_id,
        ).first()

        if not job:
            raise AppException(status_code=404, message="Job not found")
        return job

    def update_job_status(self, job_id: str, user_id: str, new_status: str) -> Job:
        job = self.get_job_by_id(job_id, user_id)

        try:
            job.status = JobStatus(new_status)
        except ValueError:
            raise AppException(
                status_code=400,
                message=f"Invalid status. Must be one of: {[s.value for s in JobStatus]}"
            )

        self.db.commit()
        self.db.refresh(job)
        return job

    async def generate_cover_letter_for_job(self, job_id: str, user_id: str) -> Job:
        # 1. Get the job
        job = self.get_job_by_id(job_id, user_id)

        # 2. Get the user's resume
        resume = self.db.query(Resume).filter(Resume.user_id == user_id).first()
        if not resume or not resume.raw_text:
            raise AppException(
                status_code=400,
                message="Please upload your resume first."
            )

        # 3. Generate cover letter with AI
        cover_letter = await self.ai_service.generate_cover_letter(
            resume_text=resume.raw_text,
            job_title=job.title,
            company=job.company or "the company",
            job_description=job.description or job.title,
        )

        # 4. Save to DB
        job.cover_letter = cover_letter
        self.db.commit()
        self.db.refresh(job)

        return job


from fastapi import Depends
from app.db.session import get_db


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)

