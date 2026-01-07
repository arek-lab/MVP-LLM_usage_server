"""
Shared service instances for dependency injection
"""
from app.services.graph_service import GraphService

# Singleton instance
_graph_service = None

def get_graph_service() -> GraphService:
    """Get or create GraphService singleton"""
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
