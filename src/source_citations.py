"""
Source Citations Module for AI-Powered Public Services Assistant.
Provides structured tracking and UI rendering of verified sources.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    """Structured representation of a retrieved source citation."""
    source_title: str = Field(..., description="Title of official document or policy")
    page_number: Optional[int] = Field(None, description="Page number if extracted from PDF")
    source_url: Optional[str] = Field(None, description="Official government / bank portal URL")
    category: str = Field(..., description="Public service category")
    snippet: Optional[str] = Field(None, description="Brief context excerpt from the document")
    chunk_id: Optional[str] = Field(None, description="Unique chunk identifier")

    def to_display_string(self) -> str:
        """Format as a clean markdown citation string."""
        parts = [f"**{self.source_title}**"]
        if self.page_number is not None and self.page_number > 0:
            parts.append(f"(Page {self.page_number})")
        if self.category:
            parts.append(f"[{self.category}]")
        if self.source_url:
            parts.append(f"| [Official Portal]({self.source_url})")
        return " ".join(parts)


def deduplicate_citations(citations: List[SourceCitation]) -> List[SourceCitation]:
    """Remove duplicate citations by title, page, and url while preserving order."""
    seen = set()
    unique = []
    for c in citations:
        key = (c.source_title.strip().lower(), c.page_number, (c.source_url or "").strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def format_citations_markdown(citations: List[SourceCitation]) -> str:
    """Render a list of citations as professional markdown."""
    if not citations:
        return ""
    
    unique_citations = deduplicate_citations(citations)
    lines = ["\n\n---", "### 📚 Verified Official Sources"]
    for i, c in enumerate(unique_citations, 1):
        page_str = f", Page {c.page_number}" if (c.page_number and c.page_number > 0) else ""
        link_str = f" — [Visit Official Portal]({c.source_url})" if c.source_url else ""
        lines.append(f"{i}. **{c.source_title}**{page_str} ({c.category}){link_str}")
        if c.snippet:
            clean_snippet = c.snippet.replace("\n", " ").strip()
            if len(clean_snippet) > 180:
                clean_snippet = clean_snippet[:180] + "..."
            lines.append(f"   > *\"{clean_snippet}\"*")
            
    return "\n".join(lines)

