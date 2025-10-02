import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import io
import base64

def create_simple_chart(insights, document_text):
    """Create a simple visualization of insights"""
   
    business_terms = ['sales', 'customer', 'growth', 'market', 'profit', 'risk']
    counts = [document_text.lower().count(term) for term in business_terms]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    
    bars = ax1.bar(business_terms, counts, color='skyblue')
    ax1.set_title('Business Term Frequency')
    ax1.set_ylabel('Number of Mentions')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom')
    
    insight_types = {
        'Sales/Revenue': sum(1 for i in insights if any(word in i.lower() for word in ['sales', 'revenue', 'profit'])),
        'Customer': sum(1 for i in insights if 'customer' in i.lower()),
        'Growth': sum(1 for i in insights if any(word in i.lower() for word in ['growth', 'opportunity'])),
        'Risk': sum(1 for i in insights if any(word in i.lower() for word in ['risk', 'problem', 'challenge']))
    }
    
    labels = [k for k, v in insight_types.items() if v > 0]
    sizes = [v for k, v in insight_types.items() if v > 0]
    
    if sizes:  
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Insight Categories')
    else:
        ax2.text(0.5, 0.5, 'No specific insights\nto visualize yet', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Insight Categories')
    
    plt.tight_layout()
    
   
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{img_str}"

def create_word_cloud(text):
    """Create a simple word cloud from document text"""
    if len(text.split()) < 10:
        return None
        
    try:
        wordcloud = WordCloud(
            width=400, 
            height=200, 
            background_color='white',
            max_words=50
        ).generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Frequent Words in Your Documents')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    except:
        return None
