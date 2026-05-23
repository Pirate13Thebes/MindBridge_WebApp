import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { Article } from '../types';
import Modal from '../components/Modal';

interface EducationHubProps {
  userRole: string;
}

const EducationHub: React.FC<EducationHubProps> = ({ userRole }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Publish Form State
  const [title, setTitle] = useState('');
  const [topic, setTopic] = useState('');
  const [body, setBody] = useState('');
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchArticles = async (query = '') => {
    setLoading(true);
    try {
      const response = await apiClient.get<Article[]>('/articles', {
        params: query ? { q: query } : {}
      });
      setArticles(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchArticles(searchQuery);
  };

  const handlePublish = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !topic || !body) {
      setMsg({ text: 'All publishing fields are required.', type: 'err' });
      return;
    }

    try {
      await apiClient.post('/articles', { title, topic, body });
      setMsg({ text: 'Article published successfully!', type: 'success' });
      setIsModalOpen(false);
      // Reset form fields
      setTitle('');
      setTopic('');
      setBody('');
      fetchArticles();
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Publishing failed.', type: 'err' });
    }
  };

  const handleDelete = async (articleId: number) => {
    if (!window.confirm('Are you sure you want to permanently delete this article?')) return;
    try {
      await apiClient.delete(`/articles/${articleId}`);
      fetchArticles();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Deletion failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide text-slate-100">Psychoeducational Library</h2>
          <p className="text-xs text-slate-400">Discover guidelines, counseling insights, and postpartum coping strategies.</p>
        </div>
        {userRole === 'admin' && (
          <button
            onClick={() => {
              setMsg({ text: '', type: '' });
              setIsModalOpen(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-teal-500/10 transition-colors"
          >
            + Publish Article
          </button>
        )}
      </div>

      {/* Dynamic FULLTEXT Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by keywords (e.g., self-care, anxiety, breathing)..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
        />
        <button
          type="submit"
          className="px-6 py-3 rounded-xl bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 border border-teal-500/20 text-xs font-bold transition-all"
        >
          Search
        </button>
        {searchQuery && (
          <button
            type="button"
            onClick={() => {
              setSearchQuery('');
              fetchArticles();
            }}
            className="px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 text-xs font-bold hover:text-slate-200 transition-colors"
          >
            Reset
          </button>
        )}
      </form>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Searching articles database...</div>
      ) : articles.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">📚</span>
          <p className="text-sm font-medium text-slate-300">No articles matched your query</p>
          <p className="text-xs text-slate-500 mt-1">Try resetting the keyword search or broadening your terms.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {articles.map((art) => (
            <div key={art.article_id} className="glass-panel p-5 rounded-2xl flex flex-col justify-between border border-slate-800 space-y-4 hover:border-slate-700 transition-all">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider bg-teal-400/5 px-2.5 py-0.5 rounded-full border border-teal-500/10">
                    {art.topic}
                  </span>
                  <span className="text-[10px] text-slate-500 font-medium">{art.created_at.split('T')[0]}</span>
                </div>
                <h3 className="font-bold text-slate-100 text-base leading-snug">{art.title}</h3>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">{art.body}</p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800/40">
                <span className="text-[10px] text-slate-500 font-semibold">Author: {art.author_name || 'System Specialist'}</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedArticle(art)}
                    className="py-1 px-3 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 text-xs font-bold border border-teal-500/20 transition-colors"
                  >
                    Read More →
                  </button>
                  {userRole === 'admin' && (
                    <button
                      onClick={() => handleDelete(art.article_id)}
                      className="p-1 px-2.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-bold border border-rose-500/20 transition-colors"
                      title="Delete Article"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Reading Article Modal Overlay */}
      <Modal isOpen={!!selectedArticle} onClose={() => setSelectedArticle(null)} title={selectedArticle?.title || ''}>
        {selectedArticle && (
          <div className="space-y-4">
            <div className="flex justify-between items-center bg-slate-950/40 p-3 rounded-xl">
              <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider bg-teal-400/5 px-2.5 py-0.5 rounded-full border border-teal-500/10">
                Category: {selectedArticle.topic}
              </span>
              <span className="text-[10px] text-slate-500 font-medium">Published: {selectedArticle.created_at.split('T')[0]}</span>
            </div>
            <div className="text-xs text-slate-300 leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-line pr-2 border-b border-slate-800 pb-4">
              {selectedArticle.body}
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-500 font-semibold pt-1">
              <span>Author: {selectedArticle.author_name || 'System Specialist'}</span>
              <button
                type="button"
                onClick={() => setSelectedArticle(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-400 text-xs font-bold border border-slate-800 transition-colors"
              >
                Close Article
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Publish Article Modal Overlay */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Publish Psychoeducational Resource">
        <form onSubmit={handlePublish} className="space-y-4">
          {msg.text && (
            <div className={`text-xs p-3 rounded-lg border ${
              msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/10 text-rose-400' : 'bg-teal-500/5 border-teal-500/10 text-teal-400'
            }`}>
              {msg.text}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Article Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="E.g., Overcoming Sleep Fatigue in the First 6 Weeks"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Topic/Category</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="E.g., Coping, Self-Care, Rest"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Article Body (Educational Text)</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={6}
              placeholder="Type or paste the clinical information contents here..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500 resize-none"
              required
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="flex-1 py-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-400 border border-slate-800 text-xs font-bold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold shadow-lg shadow-teal-500/10 transition-colors"
            >
              Publish Article
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EducationHub;
