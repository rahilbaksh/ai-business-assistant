import logging

def setup_logging():
    """Simple logging setup"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

def format_actions(steps):
    """Format action steps nicely"""
    result = []
    for i, step in enumerate(steps, 1):
        result.append(f"{i}. {step}")
    return "\n".join(result)

def get_file_type(filename):
    """Get file extension"""
    return filename.lower().split('.')[-1]
