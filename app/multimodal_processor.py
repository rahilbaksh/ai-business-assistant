from PIL import Image

from utils import setup_logging

class MultimodalProcessor:
    def __init__(self):
        self.logger = setup_logging()
        self.image_model_loaded = False
        
        # Try lightweight image analysis instead of heavy BLIP
        try:
            # We'll use a simple approach that works everywhere
            self.image_model_loaded = True
            self.logger.info("Using lightweight image analysis")
        except Exception as e:
            self.logger.warning(f"Image analysis simplified: {e}")
    
    def analyze_image(self, image_path):
        """Simple image analysis that works everywhere"""
        try:
            image = Image.open(image_path)
            
            # Basic image info anyone can get
            width, height = image.size
            format_info = image.format
            mode = image.mode
            
            # Simple analysis based on image characteristics
            if width > height:
                orientation = "landscape (likely a dashboard or wide chart)"
            else:
                orientation = "portrait (might be a report or document)"
            
            # Color analysis
            if mode == 'L':
                color_info = "grayscale (might be a printed report)"
            else:
                color_info = "color image"
            
            return f"This is a {width}x{height} {color_info} in {orientation} format. For detailed chart analysis, please describe what you see."
            
        except Exception as e:
            return f"Could not analyze image: {str(e)}"
    
    def generate_ai_insights(self, text):
        """Better insights using simple AI techniques"""
        # Count important business words to find themes
        business_words = {
            'sales': 0, 'revenue': 0, 'profit': 0, 'growth': 0,
            'customer': 0, 'market': 0, 'product': 0, 'service': 0,
            'problem': 0, 'challenge': 0, 'opportunity': 0, 'risk': 0
        }
        
        text_lower = text.lower()
        total_words = len(text_lower.split())
        
        # Count occurrences
        for word in business_words:
            business_words[word] = text_lower.count(word)
        
        # Generate insights based on word frequency
        insights = []
        
        # Sales focus
        sales_terms = business_words['sales'] + business_words['revenue'] + business_words['profit']
        if sales_terms > 3:
            insights.append(f"Strong sales focus ({sales_terms} mentions) - analyze revenue trends")
        
        # Customer focus
        if business_words['customer'] > 2:
            insights.append("Customer-centric content - review satisfaction and retention")
        
        # Growth opportunities
        if business_words['growth'] > 1 or business_words['opportunity'] > 1:
            insights.append("Growth opportunities mentioned - identify key drivers")
        
        # Problems/risks
        if business_words['problem'] > 1 or business_words['risk'] > 1:
            insights.append("Potential risks identified - needs mitigation planning")
        
        # Market focus
        if business_words['market'] > 2:
            insights.append("Market analysis content - review competitive positioning")
        
        # If no strong signals, provide general insights
        if not insights:
            if total_words > 500:
                insights.append("Comprehensive business document - multiple analysis points available")
            else:
                insights.append("Brief document - consider uploading more detailed reports")
            
            insights.append("Look for patterns in sales, customer, and market data")
        
        return insights
    
    def create_action_plan(self, insights):
        """Create action plan based on insight types"""
        actions = [
            "Review key findings with team within 4 hours",
            "Identify 2-3 immediate next steps",
            "Assign team members to each action item",
            "Schedule progress check for tomorrow morning"
        ]
        
        # Add specific actions based on insights
        insight_text = " ".join(insights).lower()
        
        if any(word in insight_text for word in ['sales', 'revenue']):
            actions.insert(1, "Analyze sales performance metrics and trends")
        
        if 'customer' in insight_text:
            actions.insert(1, "Review customer feedback and satisfaction scores")
        
        if 'growth' in insight_text or 'opportunity' in insight_text:
            actions.insert(1, "Identify growth drivers and expansion opportunities")
        
        if 'risk' in insight_text or 'problem' in insight_text:
            actions.insert(1, "Develop risk mitigation strategies")
        
        return actions
