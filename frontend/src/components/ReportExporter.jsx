import React from 'react';
import { FileText, Code2 } from 'lucide-react';

export default function ReportExporter({ reportData }) {
  if (!reportData) return null;

  const exportMarkdown = () => {
    const mdContent = `
# 🛡️ AI Code Review & Security Audit Report

**File:** \`${reportData.filename}\`  
**Language:** ${reportData.language}  
**Date:** ${new Date(reportData.created_at || Date.now()).toLocaleString()}  

---

## 📊 Summary Metrics
- **Overall Code Quality Score:** ${reportData.metrics.overall_score} / 100
- **Security Score:** ${reportData.metrics.security_score}%
- **Risk Level:** ${reportData.metrics.risk_level}
- **Maintainability Index:** ${reportData.metrics.maintainability_index}
- **Cyclomatic Complexity V(G):** ${reportData.metrics.cyclomatic_complexity}
- **Total Lines of Code:** ${reportData.metrics.total_lines} (${reportData.metrics.code_lines} code, ${reportData.metrics.comment_lines} comments)

---

## ⚠️ Issues & Vulnerabilities Detected (${reportData.issues.length})

${reportData.issues.map((i, idx) => `
### ${idx + 1}. [${i.severity.toUpperCase()}] ${i.title} (Line ${i.line})
- **Type:** ${i.type}
- **Rule ID:** ${i.rule_id || 'N/A'}
- **CWE:** ${i.cwe || 'N/A'}
- **Description:** ${i.description}
- **Suggested Fix:** ${i.suggestion}
`).join('\n')}

---

## 🤖 AI Fix Explanation
${reportData.explanation}

---

## 🔧 AI Refactored Source Code
\`\`\`${reportData.language}
${reportData.refactored_code}
\`\`\`
`.trim();

    const blob = new Blob([mdContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_report_${reportData.filename}_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_report_${reportData.filename}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center justify-end space-x-3 mb-6">
      <button
        onClick={exportMarkdown}
        className="bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
      >
        <FileText className="w-4 h-4 text-indigo-600" />
        <span>Export Markdown Report</span>
      </button>

      <button
        onClick={exportJSON}
        className="bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
      >
        <Code2 className="w-4 h-4 text-emerald-600" />
        <span>Export Raw JSON</span>
      </button>
    </div>
  );
}
