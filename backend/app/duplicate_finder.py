"""
Duplicate Issue Detection for IssuePilot
"""
import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
from .schemas import SimilarIssue, GitHubIssue


class DuplicateFinder:
    """Finds similar/duplicate issues using text similarity"""
    
    def __init__(
        self,
        use_embeddings: bool = True,
        similarity_threshold: float = 0.75,
        api_key: Optional[str] = None
    ):
        """
        Initialize Duplicate Finder
        
        Args:
            use_embeddings: Use OpenAI embeddings (True) or TF-IDF (False)
            similarity_threshold: Minimum similarity score to consider as similar
            api_key: OpenAI API key for embeddings
        """
        self.use_embeddings = use_embeddings
        self.similarity_threshold = similarity_threshold
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if self.use_embeddings and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.use_embeddings = False
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2)
            )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for similarity comparison
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", " ", text)
        
        # Remove URLs
        text = re.sub(r"https?://\S+", " ", text)
        
        # Remove special characters but keep spaces
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        return text
    
    def _combine_issue_text(self, title: str, body: str) -> str:
        """
        Combine issue title and body for comparison
        
        Args:
            title: Issue title
            body: Issue body
            
        Returns:
            Combined preprocessed text
        """
        combined = f"{title} {title} {body}"  # Title weighted more
        return self._preprocess_text(combined)
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get OpenAI embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Limit input length
        )
        return response.data[0].embedding
    
    async def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Process in batches of 100
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=[t[:8000] for t in batch]
            )
            all_embeddings.extend([d.embedding for d in response.data])
        
        return all_embeddings
    
    async def find_similar_issues(
        self,
        issue: GitHubIssue,
        existing_issues: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[SimilarIssue]:
        """
        Find issues similar to the given issue
        
        Args:
            issue: Issue to find duplicates for
            existing_issues: List of existing open issues
            top_k: Number of similar issues to return
            
        Returns:
            List of similar issues with similarity scores
        """
        if not existing_issues:
            return []
        
        # Filter out the same issue
        existing_issues = [
            e for e in existing_issues 
            if e["number"] != issue.number
        ]
        
        if not existing_issues:
            return []
        
        # Prepare texts
        target_text = self._combine_issue_text(issue.title, issue.body or "")
        existing_texts = [
            self._combine_issue_text(e["title"], e.get("body", ""))
            for e in existing_issues
        ]
        
        if self.use_embeddings:
            similarities = await self._compute_embedding_similarity(
                target_text, existing_texts
            )
        else:
            similarities = self._compute_tfidf_similarity(
                target_text, existing_texts
            )
        
        # Get top similar issues above threshold
        similar_issues = []
        for idx, score in sorted(enumerate(similarities), key=lambda x: x[1], reverse=True):
            if score >= self.similarity_threshold and len(similar_issues) < top_k:
                issue_data = existing_issues[idx]
                similar_issues.append(SimilarIssue(
                    issue_number=issue_data["number"],
                    title=issue_data["title"],
                    url=issue_data["url"],
                    similarity=round(float(score), 2)
                ))
        
        return similar_issues
    
    async def _compute_embedding_similarity(
        self,
        target_text: str,
        comparison_texts: List[str]
    ) -> List[float]:
        """
        Compute similarity using embeddings
        
        Args:
            target_text: Text to compare against
            comparison_texts: Texts to compare
            
        Returns:
            List of similarity scores
        """
        # Get embeddings
        all_texts = [target_text] + comparison_texts
        embeddings = await self._get_embeddings_batch(all_texts)
        
        # Compute cosine similarity
        target_embedding = np.array(embeddings[0]).reshape(1, -1)
        comparison_embeddings = np.array(embeddings[1:])
        
        similarities = cosine_similarity(target_embedding, comparison_embeddings)[0]
        return similarities.tolist()
    
    def _compute_tfidf_similarity(
        self,
        target_text: str,
        comparison_texts: List[str]
    ) -> List[float]:
        """
        Compute similarity using TF-IDF
        
        Args:
            target_text: Text to compare against
            comparison_texts: Texts to compare
            
        Returns:
            List of similarity scores
        """
        all_texts = [target_text] + comparison_texts
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Compute similarity
        target_vector = tfidf_matrix[0:1]
        comparison_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(target_vector, comparison_vectors)[0]
        return similarities.tolist()
    
    def check_exact_duplicate(self, issue: GitHubIssue, existing_issues: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Check for exact title match (likely duplicate)
        
        Args:
            issue: Issue to check
            existing_issues: Existing issues
            
        Returns:
            Matching issue if found, None otherwise
        """
        normalized_title = self._preprocess_text(issue.title)
        
        for existing in existing_issues:
            if existing["number"] == issue.number:
                continue
            
            existing_title = self._preprocess_text(existing["title"])
            if normalized_title == existing_title:
                return existing
        
        return None
