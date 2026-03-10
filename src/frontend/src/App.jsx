import { useState } from 'react';
import './App.css';

function App() {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDiagnose = async (e) => {
    e.preventDefault();
    if (!symptoms.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // The backend is running on port 8000
      const response = await fetch('http://localhost:8000/api/diagnose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: symptoms }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong connecting to the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>ICD-10 AI Prompt Engineer</h1>
        <p>Analyze symptoms using official BfArM data and Gemini AI</p>
      </header>

      <main className="main-content">
        <section className="input-section">
          <h2>Patient Symptoms</h2>
          <form onSubmit={handleDiagnose}>
            <textarea
              className="symptom-input"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="E.g., Patient complains about severe headache, nausea, and sensitivity to light since yesterday morning..."
              rows={6}
            />
            <button
              type="submit"
              className={`submit-btn ${loading ? 'loading' : ''}`}
              disabled={loading || !symptoms.trim()}
            >
              {loading ? 'Analyzing...' : 'Generate Diagnosis'}
            </button>
          </form>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </section>

        {result && (
          <section className="results-section">
            <div className="card ai-response">
              <h2>🤖 Gemini Analysis</h2>
              <div className="markdown-body">
                {/* Simplified rendering - in a real app you'd use react-markdown */}
                {result.llm_answer.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>

            <div className="card source-data">
              <h2>📚 Official BfArM Sources Used</h2>
              <p className="source-subtitle">Top vector search results for your input:</p>
              <ul className="source-list">
                {result.sources?.map((item, index) => (
                  <li key={index} className="source-item">
                    <span className="source-code">{item.icd_code}</span>
                    <span className="source-type">[{item.similarity.toFixed(2)} Match]</span>
                    <span className="source-text">{item.title} - {item.term}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
