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
        <p>Analysiere Symptome mit offiziellen BfArM Daten und der Gemini KI</p>
      </header>

      <main className="main-content">
        <section className="input-section">
          <h2>Symptome des Patienten</h2>
          <p className="instruction-text">
            Um eine optimale Diagnose-Einschätzung zu gewährleisten, beschreiben Sie bitte alle Symptome, deren zeitlichen Verlauf und mögliche Vorerkrankungen so präzise und detailliert wie möglich.
          </p>
          <form onSubmit={handleDiagnose}>
            <textarea
              className="symptom-input"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Z.B.: Patient klagt über starke, pulsierende Kopfschmerzen, Übelkeit und extreme Lichtempfindlichkeit seit gestern Morgen..."
              rows={6}
            />
            <button
              type="submit"
              className={`submit-btn ${loading ? 'loading' : ''}`}
              disabled={loading || !symptoms.trim()}
            >
              {loading ? 'Analysiere...' : 'Diagnose Generieren'}
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
              <h2>🤖 Gemini Analyse</h2>
              <div className="markdown-body">
                {/* Simplified rendering - in a real app you'd use react-markdown */}
                {result.llm_answer.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>

            <div className="card source-data">
              <h2>📚 Verwendete offizielle BfArM Quellen</h2>
              <p className="source-subtitle">Beste Vektorsuch-Treffer auf Basis deiner Eingabe:</p>
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
