import time
from utils import setup_logging

class Evaluator:
    def __init__(self):
        self.logger = setup_logging()
        self.start_time = time.time()
        self.queries_processed = 0
        self.documents_processed = 0
        
        
        self.sample_queries = [
            "What are the main sales trends?",
            "Are there any customer concerns?",
            "What growth opportunities are mentioned?",
            "Any risks or challenges discussed?"
        ]
    
    def log_processing(self, file_type):
        """Log when we process files"""
        self.documents_processed += 1
        self.logger.info(f"Processed {file_type}. Total: {self.documents_processed}")
    
    def log_query(self):
        """Log when we answer queries"""
        self.queries_processed += 1
    
    def get_performance_stats(self):
        """Get simple performance metrics"""
        current_time = time.time()
        runtime_minutes = (current_time - self.start_time) / 60
        
        return {
            "runtime_minutes": round(runtime_minutes, 1),
            "documents_processed": self.documents_processed,
            "queries_answered": self.queries_processed,
            "queries_per_minute": round(self.queries_processed / max(runtime_minutes, 1), 2)
        }
    
    def test_sample_queries(self, rag_engine):
        """Test the system with sample queries"""
        results = []
        
        for query in self.sample_queries:
            start_time = time.time()
            answer = rag_engine.answer_question(query)
            response_time = time.time() - start_time
            
            
            context = rag_engine.get_context(query)
            has_context = len(context) > 50  
            results.append({
                "query": query,
                "response_time_seconds": round(response_time, 2),
                "found_relevant_info": has_context,
                "answer_length": len(answer)
            })
        
        return results
    
    def calculate_simple_score(self, test_results):
        """Calculate a simple performance score"""
        if not test_results:
            return 0
            
        total_score = 0
        for result in test_results:
            score = 0
            if result['found_relevant_info']:
                score += 50
            if result['response_time_seconds'] < 2:
                score += 30
            elif result['response_time_seconds'] < 5:
                score += 20
            if result['answer_length'] > 100:
                score += 20
            
            total_score += score
        
        return total_score / len(test_results)
