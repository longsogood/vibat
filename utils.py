import requests
import re

def query(API_URL, payload):
    response = requests.post(API_URL, json=payload)
    return response

def extract_scores(detail_section):
    patterns = {
        "Information Coverage": r"Độ bao phủ thông tin[^:]*:\s*(\d+)",
        "Information Accuracy and Relevance": r"Độ chính xác và liên quan của thông tin[^:]*:\s*(\d+)",
        "Format": r"Định dạng và cấu trúc[^:]*:\s*(\d+)",
        "Language": r"Ngôn ngữ và phong cách[^:]*:\s*(\d+)",
        "Handling Unknown": r"Xử lý trường hợp không tìm thấy câu trả lời[^:]*:\s*(\d+)"
    }
    
    score_dict = {}
    
    for criterion, pattern in patterns.items():
        match = re.search(pattern, detail_section, re.IGNORECASE)
        if match:
            score_dict[criterion] = float(match.group(1))
        else:
            score_dict[criterion] = 0
    
    return score_dict

def extract_section(text):
    results = {}
    
    # Trích xuất điểm chi tiết
    scores = extract_scores(text)
    results["scores"] = scores
    
    # Trích xuất điểm tổng thể
    total_score_pattern = r'Điểm tổng thể:\s*(\d+(?:\.\d+)?)'
    total_score = re.search(total_score_pattern, text)
    if total_score:
        results["scores"]["Average"] = float(total_score.group(1))
        
    # Trích xuất nhận xét
    feedback_patterns = [
        r'(?:\d+\.)?\s*Nhận xét và góp ý cải thiện:[\r\n\s]*(.*?)(?=\d+\.\s*Điểm tổng thể|\Z)',
        r'(?:\d+\.)?\s*Nhận xét và góp ý cải thiện:\s*(.*?)(?=\d+\.\s*Điểm tổng thể|\Z)',
        r'(?:\d+\.)?\s*Nhận xét và góp ý cải thiện:[\r\n\s]*(.*?)(?=\n\n\d+\.|\Z)',
        r'(?:\d+\.)?\s*Nhận xét và góp ý cải thiện:\s*(.*?)(?=\n\n\d+\.|\Z)'
    ]
    
    for pattern in feedback_patterns:
        feedback = re.search(pattern, text, re.DOTALL)
        if feedback and feedback.group(1).strip():
            results["Nhận xét và góp ý cải thiện"] = feedback.group(1).strip()
            break
        
    return results