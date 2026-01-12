import json
import os
from datetime import datetime

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

def parse_semgrep(data):
    findings = []
    if not data: return findings
    for result in data.get('results', []):
        findings.append({
            'tool': 'Semgrep',
            'severity': result['extra']['severity'],
            'message': result['extra']['message'],
            'location': f"{result['path']}:{result['start']['line']}"
        })
    return findings

def parse_checkov(data):
    findings = []
    if not data: return findings
    # Checkov output can be a list (multiple files) or dict
    if isinstance(data, dict):
        data = [data]
    
    for scan in data:
        if 'results' not in scan: continue
        for check in scan['results'].get('failed_checks', []):
            findings.append({
                'tool': 'Checkov',
                'severity': 'HIGH', # Checkov doesn't always have severity in simple JSON, assuming HIGH for failed
                'message': check['check_name'],
                'location': check['file_path']
            })
    return findings

def parse_trivy(data):
    findings = []
    if not data: return findings
    if 'Results' not in data: return findings
    
    for result in data['Results']:
        target = result.get('Target', 'Container')
        for vuln in result.get('Vulnerabilities', []):
            findings.append({
                'tool': 'Trivy',
                'severity': vuln['Severity'],
                'message': f"{vuln['PkgName']} ({vuln['InstalledVersion']}) - {vuln['Title']}",
                'location': target
            })
    return findings

def generate_html(findings):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevSecOps Security Report</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
            .container {{ max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a202c; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
            .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .card {{ flex: 1; padding: 15px; border-radius: 6px; color: white; text-align: center; }}
            .bg-red {{ background: #e53e3e; }}
            .bg-orange {{ background: #dd6b20; }}
            .bg-green {{ background: #38a169; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #e2e8f0; }}
            th {{ background: #f7fafc; color: #4a5568; }}
            .severity-CRITICAL {{ color: #e53e3e; font-weight: bold; }}
            .severity-HIGH {{ color: #dd6b20; font-weight: bold; }}
            .severity-MEDIUM {{ color: #d69e2e; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; color: white; }}
            .badge-Semgrep {{ background: #4299e1; }}
            .badge-Checkov {{ background: #805ad5; }}
            .badge-Trivy {{ background: #319795; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ DevSecOps Pipeline Security Report</h1>
            <p>Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary">
                <div class="card bg-red">
                    <h3>{len([f for f in findings if f['severity'] in ['CRITICAL', 'HIGH']])}</h3>
                    <div>Critical/High Issues</div>
                </div>
                <div class="card bg-orange">
                    <h3>{len([f for f in findings if f['severity'] in ['MEDIUM']])}</h3>
                    <div>Medium Issues</div>
                </div>
                <div class="card bg-green">
                    <h3>{len(findings)}</h3>
                    <div>Total Findings</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Tool</th>
                        <th>Severity</th>
                        <th>Message</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for f in findings:
        html += f"""
        <tr>
            <td><span class="badge badge-{f['tool']}">{f['tool']}</span></td>
            <td class="severity-{f['severity']}">{f['severity']}</td>
            <td>{f['message']}</td>
            <td>{f['location']}</td>
        </tr>
        """
        
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    semgrep_data = load_json("semgrep-report.json")
    checkov_data = load_json("checkov-report.json")
    trivy_data = load_json("trivy-report.json")

    all_findings = []
    all_findings.extend(parse_semgrep(semgrep_data))
    all_findings.extend(parse_checkov(checkov_data))
    all_findings.extend(parse_trivy(trivy_data))

    html_content = generate_html(all_findings)
    
    with open("security-report.html", "w") as f:
        f.write(html_content)
    
    print("Report generated: security-report.html")
