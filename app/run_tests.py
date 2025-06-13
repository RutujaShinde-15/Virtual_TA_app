import yaml
import requests
import base64
import os
from pathlib import Path

def load_image(image_path):
    """Load and encode image from file path."""
    if not image_path:
        return None
    
    # Remove file:// prefix if present
    if image_path.startswith('file://'):
        image_path = image_path[7:]
    
    # Convert to absolute path
    image_path = os.path.join(os.path.dirname(__file__), image_path)
    
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def run_test(test_case, base_url="http://127.0.0.1:8000/api/"):
    """Run a single test case."""
    print(f"\nRunning test: {test_case.get('vars', {}).get('question', 'Image-only test')}")
    
    # Prepare request data
    data = {}
    files = {}
    
    if 'question' in test_case['vars']:
        data['question'] = test_case['vars']['question']
    
    if 'image' in test_case['vars']:
        image_data = load_image(test_case['vars']['image'])
        if image_data:
            files['image'] = ('image.png', base64.b64decode(image_data), 'image/png')
    
    # Make request
    try:
        response = requests.post(base_url, data=data, files=files)
        response.raise_for_status()
        result = response.json()
        
        # Run assertions
        for assertion in test_case.get('assert', []):
            if assertion['type'] == 'contains':
                assert assertion['value'] in result[assertion['path']], \
                    f"Expected '{assertion['value']}' in {assertion['path']}"
            elif assertion['type'] == 'contains-any':
                assert any(v in result[assertion['path']] for v in assertion['value']), \
                    f"Expected any of {assertion['value']} in {assertion['path']}"
            elif assertion['type'] == 'contains-all':
                assert all(v in result[assertion['path']] for v in assertion['value']), \
                    f"Expected all of {assertion['value']} in {assertion['path']}"
            elif assertion['type'] == 'icontains':
                assert assertion['value'].lower() in result[assertion['path']].lower(), \
                    f"Expected '{assertion['value']}' (case-insensitive) in {assertion['path']}"
        
        print("✅ Test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    # Load test configuration
    yaml_path = os.path.join(os.path.dirname(__file__), 'evaluate.yaml')
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run tests
    total_tests = len(config['tests'])
    passed_tests = 0
    
    print(f"\nRunning {total_tests} tests...")
    
    for test in config['tests']:
        if run_test(test):
            passed_tests += 1
    
    print(f"\nTest Summary: {passed_tests}/{total_tests} tests passed")

if __name__ == "__main__":
    main() 