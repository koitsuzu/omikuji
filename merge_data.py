import re
import json

def parse_kanji_number(text):
    kanji_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if not text: return 0
    if text in kanji_map: return kanji_map[text]
    
    val = 0
    if text.startswith('十'):
        val += 10
        if len(text) > 1:
            val += kanji_map.get(text[1], 0)
    elif text.endswith('十'):
        val += kanji_map.get(text[0], 0) * 10
    elif '十' in text:
        parts = text.split('十')
        val += kanji_map.get(parts[0], 0) * 10
        val += kanji_map.get(parts[1], 0)
    else:
        # Fallback for simple cases greater than 10 not using Ten? Unlikely for 1-50
        pass
    return val

def parse_omikuji_txt(filepath):
    data = {}
    current_no = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        line = line.strip()
        match = re.match(r'第(.+)番', line)
        if match:
            k_num = match.group(1)
            current_no = parse_kanji_number(k_num)
            # The next line is usually the explanation.
            # But need to check if it's empty or another number
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if next_line and not next_line.startswith('第'):
                     data[current_no] = next_line
    return data

def update_script_js(script_path, fortune_data):
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We iterate through the regex matches for "no": X and insert explanation
    # Note: Regex replacement with a callback is best.
    
    def replace_callback(match):
        full_match = match.group(0) # "no": 1,
        no = int(match.group(1))
        
        if no in fortune_data:
            expl = fortune_data[no]
            # Escape quotes
            expl = expl.replace('"', '\\"').replace('\n', '\\n')
            return f'"no": {no},\n        "explanation": "{expl}",'
        return full_match

    new_content = re.sub(r'"no":\s*(\d+),', replace_callback, content)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    omikuji_path = '/Users/qaro/Desktop/omikuji/omikuji.txt'
    script_path = '/Users/qaro/Desktop/omikuji/script.js'
    
    data = parse_omikuji_txt(omikuji_path)
    # print(json.dumps(data, ensure_ascii=False, indent=2))
    update_script_js(script_path, data)
    print("Updated script.js")
