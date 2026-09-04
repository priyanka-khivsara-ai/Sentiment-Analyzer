import React, { useState } from 'react';
import { UploadCloud, Activity, BarChart2, MessageSquare, AlertCircle, CheckCircle, ShieldAlert, Heart, Zap, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

// Simple mockup for auth
function LoginScreen({ onLogin }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-ai-dark p-4">
      <div className="bg-ai-card backdrop-blur-glass p-8 rounded-2xl shadow-glass border border-white/10 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-white">CallSense <span className="text-ai-cyan">AI</span></h1>
        <p className="text-gray-400 text-center mb-8">Agentic Conversation Intelligence</p>
        <button 
          onClick={onLogin}
          className="w-full bg-glass-gradient border border-ai-cyan/30 text-ai-cyan hover:bg-ai-cyan hover:text-black font-semibold py-3 rounded-lg transition-all duration-300 shadow-neon"
        >
          Authenticate to Dashboard
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  if (!isAuthenticated) return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.name.endsWith('.txt')) {
      setFile(selected);
      setError(null);
    } else {
      setFile(null);
      setError("Please upload a valid .txt conversation transcript.");
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Proxy intercepts /api and sends to FastAPI
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message || "Failed to connect to the analysis engine. Is the backend running?");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  const renderDashboard = () => {
    if (!results) return null;

    const sentimentColors = { positive: '#10B981', negative: '#EF4444', neutral: '#6B7280' };

    // Chart Data formatting: Dynamic Distribution based on ALL sentences
    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
    (results.sentences || []).forEach(s => {
      const sent = s.sentiment.toLowerCase();
      if (sentimentCounts[sent] !== undefined) sentimentCounts[sent]++;
    });

    const pieData = [
      { name: 'Positive', value: sentimentCounts.positive, fill: '#10B981' },
      { name: 'Negative', value: sentimentCounts.negative, fill: '#EF4444' },
      { name: 'Neutral', value: sentimentCounts.neutral, fill: '#6B7280' }
    ].filter(d => d.value > 0); // Only show pieces of the pie that actually exist
    
    // Emotion parsing for charts
    const emotionData = results.emotions.map(e => ({ name: e, intensity: Math.random() * 50 + 50 }));

    return (
      <div className="animate-fade-in space-y-6">
        
        {/* Top KPI row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-ai-card p-4 rounded-xl shadow-glass border border-white/10 flex items-center gap-4">
            <div className={`p-3 rounded-lg ${results.overall_sentiment === 'negative' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
              <Activity size={24} />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Overall Sentiment</p>
              <h3 className="text-xl font-bold capitalize text-white">{results.overall_sentiment}</h3>
            </div>
          </div>

          <div className="bg-ai-card p-4 rounded-xl shadow-glass border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-ai-cyan/20 text-ai-cyan">
              <CheckCircle size={24} />
            </div>
            <div>
              <p className="text-gray-400 text-sm">AI Confidence</p>
              <h3 className="text-xl font-bold text-white">{(results.confidence * 100).toFixed(0)}%</h3>
            </div>
          </div>
          
          <div className="bg-ai-card p-4 rounded-xl shadow-glass border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-yellow-500/20 text-yellow-400">
              <ShieldAlert size={24} />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Escalation Risk</p>
              <h3 className="text-xl font-bold text-white">{results.kpis?.escalation_risk || "Unknown"}</h3>
            </div>
          </div>

          <div className="bg-ai-card p-4 rounded-xl shadow-glass border border-white/10 flex items-center gap-4">
            <div className="p-3 rounded-lg bg-ai-violet/20 text-ai-violet">
              <Heart size={24} />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Agent Helpfulness</p>
              <h3 className="text-xl font-bold text-white">{results.kpis?.agent_helpfulness || "Unknown"}</h3>
            </div>
          </div>
        </div>

        {/* Charts & Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="col-span-2 bg-ai-card p-6 rounded-xl shadow-glass border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <MessageSquare size={18} className="text-ai-cyan" /> Conversation Summary
            </h3>
            <p className="text-gray-300 leading-relaxed bg-white/5 p-4 rounded-lg">
              {results.conversation_summary}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap size={18} className="text-ai-violet" /> Emotion Detection
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.emotions.map((em, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-ai-violet/20 text-ai-violet text-sm border border-ai-violet/30 capitalize shadow-neon">
                      {em}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <CheckCircle size={18} className="text-green-400" /> Action Items / Next Steps
                </h3>
                <ul className="space-y-2">
                  {(results.action_items || []).map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                      <div className="mt-1 w-1.5 h-1.5 rounded-full bg-ai-cyan shrink-0"></div>
                      {item}
                    </li>
                  ))}
                  {(!results.action_items || results.action_items.length === 0) && (
                    <li className="text-gray-500 italic text-sm">No action items detected.</li>
                  )}
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-ai-card p-6 rounded-xl shadow-glass border border-white/10 flex flex-col items-center justify-center">
            <h3 className="text-lg font-semibold text-white mb-2 w-full text-center">Conversation Sentiment Breakdown</h3>
            <p className="text-xs text-gray-400 mb-4 text-center">Distribution of positive/negative sentences</p>
            <div className="h-48 w-full relative">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie 
                      data={pieData} 
                      innerRadius={45} 
                      outerRadius={70} 
                      paddingAngle={5} 
                      dataKey="value" 
                      stroke="none"
                      labelLine={false}
                      label={({ name, percent }) => percent > 0 ? `${(percent * 100).toFixed(0)}%` : ''}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <RechartsTooltip contentStyle={{ backgroundColor: '#111928', borderColor: 'rgba(255,255,255,0.1)', color: 'white', borderRadius: '8px' }} />
                    <Legend verticalAlign="bottom" height={24} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-gray-500 italic text-sm">No sentence data</div>
              )}
            </div>
          </div>
        </div>

        {/* Sentence Level Analysis */}
        <div className="bg-ai-card p-6 rounded-xl shadow-glass border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Clock size={18} className="text-ai-cyan" /> Key Sentence Analysis
          </h3>
          <div className="space-y-3">
            {results.sentences.map((item, i) => (
              <div key={i} className="border-l-4 p-4 bg-white/5 rounded-r-lg" 
                   style={{ borderLeftColor: sentimentColors[item.sentiment] }}>
                <p className="text-gray-200 italic mb-1">"{item.sentence}"</p>
                <div className="flex gap-4 text-xs text-gray-400">
                  <span className="font-semibold">{item.speaker || 'Unknown'}</span>
                  <span className="capitalize" style={{ color: sentimentColors[item.sentiment] }}>{item.sentiment}</span>
                  <span>Confidence: {(item.confidence * 100).toFixed(0)}%</span>
                </div>
                {item.explanation && <p className="text-sm text-gray-400 mt-2">↳ {item.explanation}</p>}
              </div>
            ))}
            {results.sentences.length === 0 && (
              <p className="text-gray-500 italic">No key sentences extracted.</p>
            )}
          </div>
        </div>

        <button onClick={reset} className="mt-8 text-ai-cyan hover:text-white transition-colors text-sm">
          ← Analyze another conversation
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen p-6 md:p-12">
      <header className="mb-10 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            CallSense <span className="text-ai-cyan bg-ai-cyan/10 px-2 py-0.5 rounded text-sm">AI</span>
          </h1>
          <p className="text-gray-400 text-sm mt-1">Intelligence Dashboard</p>
        </div>
        <button onClick={() => setIsAuthenticated(false)} className="text-gray-500 hover:text-white text-sm">Logout</button>
      </header>

      <main className="max-w-6xl mx-auto">
        {!results ? (
          <div className="bg-ai-card border border-white/10 shadow-glass rounded-2xl p-12 text-center max-w-2xl mx-auto backdrop-blur-glass">
            <UploadCloud size={48} className="mx-auto text-ai-violet mb-6" />
            <h2 className="text-2xl font-semibold text-white mb-2">Upload Conversation Transcript</h2>
            <p className="text-gray-400 mb-8">Supports .txt files containing customer service dialogue.</p>
            
            <input 
              type="file" 
              accept=".txt" 
              onChange={handleFileChange} 
              className="hidden" 
              id="file-upload"
            />
            <label 
              htmlFor="file-upload"
              className="cursor-pointer inline-flex items-center gap-2 bg-white/5 border border-white/10 hover:border-ai-cyan/50 text-white py-3 px-6 rounded-lg transition-all"
            >
              {file ? file.name : "Select .txt file"}
            </label>

            {error && (
              <div className="mt-6 flex items-center justify-center gap-2 text-red-400 bg-red-400/10 p-3 rounded-lg border border-red-400/20">
                <AlertCircle size={18} />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <div className="mt-8">
              <button 
                onClick={handleAnalyze}
                disabled={!file || isAnalyzing}
                className="w-full bg-ai-cyan text-black font-bold py-3 px-6 rounded-lg shadow-neon disabled:opacity-50 disabled:shadow-none hover:bg-white transition-all flex justify-center items-center gap-2"
              >
                {isAnalyzing ? (
                  <span className="animate-pulse">Synthesizing insights...</span>
                ) : (
                  <span>Analyze with AI</span>
                )}
              </button>
            </div>
          </div>
        ) : renderDashboard()}
      </main>
    </div>
  );
}
