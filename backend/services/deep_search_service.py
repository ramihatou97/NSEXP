"""
Deep Search Integration Service
Integrates with PubMed, Google Scholar, and other medical literature databases
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from xml.etree import ElementTree as ET

from config.settings_simplified import settings

logger = logging.getLogger(__name__)


class DeepSearchService:
    """
    Service for deep literature search across multiple medical databases
    """
    
    def __init__(self):
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.pubmed_api_key = getattr(settings, 'PUBMED_API_KEY', None)
        self.timeout = httpx.Timeout(30.0)
        
    async def search_medical_literature(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search across multiple medical literature sources
        
        Args:
            query: Search query
            sources: List of sources to search (pubmed, scholar, arxiv)
            max_results: Maximum results per source
            filters: Additional filters (year, type, etc.)
            
        Returns:
            Aggregated search results from all sources
        """
        if sources is None:
            sources = ["pubmed"]  # Default to PubMed only
        
        results = {
            "query": query,
            "sources_searched": sources,
            "total_results": 0,
            "results": [],
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "filters_applied": filters or {}
            }
        }
        
        # Search each source concurrently
        search_tasks = []
        
        if "pubmed" in sources:
            search_tasks.append(self._search_pubmed(query, max_results, filters))
        
        if "scholar" in sources:
            search_tasks.append(self._search_google_scholar(query, max_results))
        
        if "arxiv" in sources:
            search_tasks.append(self._search_arxiv(query, max_results))
        
        # Execute searches concurrently
        if search_tasks:
            source_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Aggregate results
            for source_result in source_results:
                if isinstance(source_result, dict) and not isinstance(source_result, Exception):
                    results["results"].extend(source_result.get("results", []))
                    results["total_results"] += source_result.get("count", 0)
                elif isinstance(source_result, Exception):
                    logger.error(f"Search source failed: {source_result}")
        
        # Deduplicate by DOI/PMID
        results["results"] = self._deduplicate_results(results["results"])
        results["total_results"] = len(results["results"])
        
        # Sort by relevance
        results["results"] = self._sort_by_relevance(results["results"], query)
        
        return results
    
    async def _search_pubmed(
        self,
        query: str,
        max_results: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search PubMed database using E-utilities API
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Step 1: Search for PMIDs
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance"
                }
                
                if self.pubmed_api_key:
                    search_params["api_key"] = self.pubmed_api_key
                
                # Add filters
                if filters:
                    if filters.get("year_min"):
                        search_params["mindate"] = f"{filters['year_min']}/01/01"
                    if filters.get("year_max"):
                        search_params["maxdate"] = f"{filters['year_max']}/12/31"
                
                search_url = f"{self.pubmed_base_url}/esearch.fcgi"
                search_response = await client.get(search_url, params=search_params)
                search_response.raise_for_status()
                
                search_data = search_response.json()
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    return {"source": "pubmed", "count": 0, "results": []}
                
                # Step 2: Fetch details for PMIDs
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }
                
                if self.pubmed_api_key:
                    fetch_params["api_key"] = self.pubmed_api_key
                
                fetch_url = f"{self.pubmed_base_url}/efetch.fcgi"
                fetch_response = await client.get(fetch_url, params=fetch_params)
                fetch_response.raise_for_status()
                
                # Parse XML response
                articles = self._parse_pubmed_xml(fetch_response.text)
                
                return {
                    "source": "pubmed",
                    "count": len(articles),
                    "results": articles
                }
                
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return {"source": "pubmed", "count": 0, "results": [], "error": str(e)}
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """
        Parse PubMed XML response into structured data
        """
        articles = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    # Extract PMID
                    pmid = article.find(".//PMID")
                    pmid_text = pmid.text if pmid is not None else ""
                    
                    # Extract title
                    title = article.find(".//ArticleTitle")
                    title_text = title.text if title is not None else ""
                    
                    # Extract abstract
                    abstract_elem = article.find(".//Abstract/AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None else ""
                    
                    # Extract authors
                    authors = []
                    for author in article.findall(".//Author"):
                        lastname = author.find("LastName")
                        forename = author.find("ForeName")
                        if lastname is not None and forename is not None:
                            authors.append(f"{forename.text} {lastname.text}")
                    
                    # Extract journal
                    journal = article.find(".//Journal/Title")
                    journal_text = journal.text if journal is not None else ""
                    
                    # Extract publication date
                    pub_date = article.find(".//PubDate/Year")
                    year = pub_date.text if pub_date is not None else ""
                    
                    # Extract DOI
                    doi = None
                    for article_id in article.findall(".//ArticleId"):
                        if article_id.get("IdType") == "doi":
                            doi = article_id.text
                            break
                    
                    article_data = {
                        "source": "pubmed",
                        "pmid": pmid_text,
                        "title": title_text,
                        "abstract": abstract,
                        "authors": authors,
                        "journal": journal_text,
                        "year": year,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/" if pmid_text else "",
                        "relevance_score": 1.0  # Will be calculated later
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            return []
    
    async def _search_google_scholar(
        self,
        query: str,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search Google Scholar (Note: This is a placeholder - actual implementation
        requires either SerpAPI or scraping with proper rate limiting)
        """
        logger.warning("Google Scholar search not fully implemented - requires API key or scraping")
        
        return {
            "source": "google_scholar",
            "count": 0,
            "results": [],
            "note": "Google Scholar integration requires API key or web scraping setup"
        }
    
    async def _search_arxiv(
        self,
        query: str,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search arXiv for preprints (medical category)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                arxiv_url = "http://export.arxiv.org/api/query"
                
                params = {
                    "search_query": f"all:{query} AND cat:q-bio*",  # Biology category
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending"
                }
                
                response = await client.get(arxiv_url, params=params)
                response.raise_for_status()
                
                # Parse Atom feed
                articles = self._parse_arxiv_atom(response.text)
                
                return {
                    "source": "arxiv",
                    "count": len(articles),
                    "results": articles
                }
                
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return {"source": "arxiv", "count": 0, "results": [], "error": str(e)}
    
    def _parse_arxiv_atom(self, atom_text: str) -> List[Dict[str, Any]]:
        """
        Parse arXiv Atom feed into structured data
        """
        articles = []
        
        try:
            root = ET.fromstring(atom_text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                try:
                    title = entry.find('atom:title', ns)
                    title_text = title.text.strip() if title is not None else ""
                    
                    summary = entry.find('atom:summary', ns)
                    abstract = summary.text.strip() if summary is not None else ""
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name = author.find('atom:name', ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    # Extract ID (arXiv ID)
                    id_elem = entry.find('atom:id', ns)
                    arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else ""
                    
                    # Extract published date
                    published = entry.find('atom:published', ns)
                    year = published.text[:4] if published is not None else ""
                    
                    article_data = {
                        "source": "arxiv",
                        "arxiv_id": arxiv_id,
                        "title": title_text,
                        "abstract": abstract,
                        "authors": authors,
                        "year": year,
                        "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                        "relevance_score": 1.0
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse arXiv entry: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"arXiv Atom parsing failed: {e}")
            return []
    
    def _deduplicate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate results based on DOI, PMID, or title similarity
        """
        seen_identifiers = set()
        deduplicated = []
        
        for result in results:
            # Check DOI
            if result.get("doi") and result["doi"] in seen_identifiers:
                continue
            
            # Check PMID
            if result.get("pmid") and result["pmid"] in seen_identifiers:
                continue
            
            # Check arXiv ID
            if result.get("arxiv_id") and result["arxiv_id"] in seen_identifiers:
                continue
            
            # Add to results
            if result.get("doi"):
                seen_identifiers.add(result["doi"])
            if result.get("pmid"):
                seen_identifiers.add(result["pmid"])
            if result.get("arxiv_id"):
                seen_identifiers.add(result["arxiv_id"])
            
            deduplicated.append(result)
        
        return deduplicated
    
    def _sort_by_relevance(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Sort results by relevance to query
        Simple implementation - can be enhanced with ML
        """
        query_terms = query.lower().split()
        
        for result in results:
            score = 0.0
            
            title = result.get("title", "").lower()
            abstract = result.get("abstract", "").lower()
            
            # Count query term matches
            for term in query_terms:
                if term in title:
                    score += 2.0  # Title matches weighted higher
                if term in abstract:
                    score += 1.0
            
            result["relevance_score"] = score
        
        # Sort by relevance score (descending)
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    async def enrich_reference_metadata(
        self,
        reference: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich a reference with additional metadata from online sources
        """
        enriched = reference.copy()
        
        # Try to find DOI if not present
        if not enriched.get("doi") and enriched.get("title"):
            # Search by title to find DOI
            search_results = await self._search_pubmed(
                enriched["title"],
                max_results=1
            )
            
            if search_results.get("results"):
                first_result = search_results["results"][0]
                enriched["doi"] = first_result.get("doi")
                enriched["pmid"] = first_result.get("pmid")
                enriched["url"] = first_result.get("url")
                
                # Add abstract if missing
                if not enriched.get("abstract"):
                    enriched["abstract"] = first_result.get("abstract")
        
        return enriched


# Global instance
deep_search_service = DeepSearchService()
