import subprocess
import os

base_path = r"c:\Users\agregorio1\OneDrive - KPMG\Desktop\VS Code Projects\AI Agent Safety\Safety Testing\planning"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def convert_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using Edge's headless print-to-pdf feature"""
    html_path = os.path.join(base_path, html_file)
    pdf_path = os.path.join(base_path, pdf_file)
    file_url = f'file:///{html_path.replace(os.sep, "/")}'
    
    cmd = [
        edge_path,
        '--headless',
        '--disable-gpu',
        f'--print-to-pdf={pdf_path}',
        '--no-pdf-header-footer',
        file_url
    ]
    
    print(f"Converting {html_file}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if os.path.exists(pdf_path):
        print(f"  Created: {pdf_file}")
        return True
    else:
        print(f"  Failed: {result.stderr}")
        return False

# Convert both files
convert_to_pdf('testing-strategy-v2.html', 'testing-strategy-v2.pdf')
convert_to_pdf('test-plan-v2.html', 'test-plan-v2.pdf')

print('Done!')
