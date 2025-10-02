from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document as LangchainDoc
from transformers import pipeline
import re

from utils import setup_logging


class RAGEngine:
    def __init__(self):
        self.logger = setup_logging()
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.documents = []

       
        try:
            self.llm = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",   
                max_length=300,
                truncation=True
            )
            self.llm_available = False  
            self.logger.info("✅ Flan-T5 Small loaded but DISABLED to prevent gibberish")
        except Exception as e:
            self.llm_available = False
            self.logger.warning(f"⚠️ LLM not available, using safe fallback: {e}")

    def add_document(self, content, source=""):
        """Add a document to our knowledge base"""
        if not content.strip():
            return

        doc = LangchainDoc(
            page_content=content,
            metadata={"source": source}
        )

        if self.vector_store is None:
            self.vector_store = Chroma.from_documents(
                [doc],
                self.embeddings,
                persist_directory="./chroma_db"
            )
        else:
            self.vector_store.add_documents([doc])

        self.documents.append(content)
        self.logger.info(f"📄 Added document from {source}")

    def search(self, query, num_results=3):
        """Search for relevant information"""
        if self.vector_store is None:
            return []

        try:
            results = self.vector_store.similarity_search(query, k=num_results)
            return [doc.page_content for doc in results]
        except Exception as e:
            self.logger.error(f"❌ Search error: {e}")
            return []

    def _expand_business_query(self, query):
        """Expand common business questions with relevant keywords"""
        query_lower = query.lower()
        
        expansions = {
            'litigation': 'talc opioids lawsuits legal proceedings baby powder',
            'sales': 'revenue growth operational sales billion dollars 2023',
            'risk': 'risk factors legal proceedings competition',
            'r&d': 'research development innovation pipeline investment',
            'segment': 'innovative medicine medtech business segments',
            'growth': 'operational sales revenue increase percentage',
            'income': 'earnings profit revenue financial',
            'dividend': 'dividend shareholders payment',
            'patent': 'patent intellectual property exclusivity',
            'inflation': 'inflation reduction act ira medicare drug price',
            'medicare': 'medicare price negotiation inflation reduction act',
            'stelara': 'stelara biosimilar patent exclusivity',
            'employees': 'employees workforce human capital',
            'manufacturing': 'manufacturing facilities plants operations'
        }
        
        for key, expansion in expansions.items():
            if key in query_lower:
                return f"{query} {expansion}"
        
        return query

    def get_context(self, query):
        """Get context with better search strategy"""
       
        relevant_docs = self.search(query, num_results=5)
        
        
        if not relevant_docs or len(' '.join(relevant_docs)) < 100:
            expanded_query = self._expand_business_query(query)
            if expanded_query != query:
                additional_docs = self.search(expanded_query, num_results=3)
                relevant_docs.extend(additional_docs)
        
        
        unique_docs = list(dict.fromkeys(relevant_docs))
        unique_docs.sort(key=len, reverse=True)  
        
        context = " ".join(unique_docs)
        return context[:2000] 

    def _is_gibberish(self, text):
        """Check if the text looks like garbage output"""
        if len(text) < 10:
            return True
        
      
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace() and c not in ['.', ',', '!', '?', ':', ';', '-', '$', '%'])
        special_char_ratio = special_chars / len(text)
        if special_char_ratio > 0.2: 
            return True
            
       
        if any(pattern in text for pattern in ["++", "//", "&&", "(+", ")/", "*0", "*1", ".*"]):
            return True
            
       
        if re.search(r'[A-Za-z][0-9][A-Za-z]', text):  
            return True
            
        return False

    def _extract_best_answer(self, context, question):
        """Extract the most relevant answer from context without LLM"""
        question_lower = question.lower()
        sentences = re.split(r'[.!?]+', context)
        
      
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:  
                continue
                
            score = 0
            sentence_lower = sentence.lower()
            
           
            question_words = set(question_lower.split())
            for word in question_words:
                if len(word) > 3 and word in sentence_lower:
                    score += 3
            
           
            if any(term in question_lower for term in ['sales', 'revenue', 'growth', 'financial']):
                if any(term in sentence_lower for term in ['billion', 'million', 'dollar', 'percent', 'growth', 'sales']):
                    score += 2
            
            
            if any(term in question_lower for term in ['litigation', 'lawsuit', 'legal', 'talc', 'opioid']):
                if any(term in sentence_lower for term in ['lawsuit', 'litigation', 'talc', 'opioid', 'legal']):
                    score += 2
            
            if score > 0:
                scored_sentences.append((score, sentence.strip()))
        
        
        if scored_sentences:
            scored_sentences.sort(reverse=True, key=lambda x: x[0])
            return scored_sentences[0][1] + "."
        
        
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                return sentence.strip() + "."
        
        return "Relevant information found but cannot extract specific answer."

    def answer_question(self, question):
        """Answer question using safe extraction without LLM gibberish"""
        context = self.get_context(question)

        if not context or len(context.strip()) < 50:
            return "I couldn't find relevant information about this topic in your documents."

       
        try:
            answer = self._extract_best_answer(context, question)
            
           
            if self._is_gibberish(answer):
                return "The document contains relevant information, but I cannot provide a clear answer at this time."
                
            return answer
            
        except Exception as e:
            self.logger.error(f"Error extracting answer: {e}")
            return "I encountered an error while processing your question. Please try rephrasing it."

    def get_document_stats(self):
        """Get statistics about loaded documents"""
        if not self.documents:
            return "No documents loaded"
        
        total_chunks = len(self.documents)
        total_text = sum(len(doc) for doc in self.documents)
        
        return f"Loaded {total_chunks} document chunks with {total_text:,} total characters"