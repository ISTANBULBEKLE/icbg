"use client";

import React, { useState, useEffect } from 'react';
import styles from './page.module.css';
import UploadZone from '@/components/UploadZone';
import DocumentSegmentation from '@/components/DocumentSegmentation';
import BookSpecs from '@/components/BookSpecs';
import BookHistoryDrawer, { Book } from '@/components/BookHistoryDrawer';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [segmentation, setSegmentation] = useState({
    sectionDescription: '',
    additionalContext: '',
    pageStart: null as number | null,
    pageEnd: null as number | null
  });
  const [specs, setSpecs] = useState({
    theme: '',
    humor: 5,
    ageGroup: '6-8'
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [history, setHistory] = useState<Book[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('bookHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error("Failed to parse history", e);
      }
    }
  }, []);

  const addToHistory = (book: Book) => {
    setHistory(prev => {
      const newHistory = [book, ...prev].slice(0, 5);
      localStorage.setItem('bookHistory', JSON.stringify(newHistory));
      return newHistory;
    });
  };

  const handleDeleteBook = (id: string) => {
    setHistory(prev => {
      const newHistory = prev.filter(book => book.id !== id);
      localStorage.setItem('bookHistory', JSON.stringify(newHistory));
      return newHistory;
    });
  };

  const handleReset = () => {
    setFile(null);
    setSegmentation({
      sectionDescription: '',
      additionalContext: '',
      pageStart: null,
      pageEnd: null
    });
    setSpecs({
      theme: '',
      humor: 5,
      ageGroup: '6-8'
    });
    setIsGenerating(false);
    setProgress(0);
    setStatusMessage('');
    setDownloadUrl(null);
  };

  const handleSegmentationChange = (field: string, value: any) => {
    setSegmentation(prev => ({ ...prev, [field]: value }));
  };

  const handleSpecChange = (field: string, value: any) => {
    setSpecs(prev => ({ ...prev, [field]: value }));
  };

  const handleGenerate = async () => {
    if (!file) return;
    setIsGenerating(true);
    setProgress(0);
    setStatusMessage('Starting...');
    setDownloadUrl(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('sectionDescription', segmentation.sectionDescription);
    formData.append('additionalContext', segmentation.additionalContext);
    if (segmentation.pageStart !== null) {
      formData.append('pageStart', segmentation.pageStart.toString());
    }
    if (segmentation.pageEnd !== null) {
      formData.append('pageEnd', segmentation.pageEnd.toString());
    }
    formData.append('theme', specs.theme);
    formData.append('humor', specs.humor.toString());
    formData.append('ageGroup', specs.ageGroup);

    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      const jobId = data.job_id;

      // Start SSE
      const eventSource = new EventSource(`http://localhost:8000/events/${jobId}`);

      eventSource.onmessage = (event) => {
        const eventData = JSON.parse(event.data);

        if (eventData.error) {
          console.error("Job Error:", eventData.error);
          setStatusMessage(`Error: ${eventData.error}`);
          eventSource.close();
          setIsGenerating(false);
          return;
        }

        setProgress(eventData.progress);
        setStatusMessage(eventData.message);

        if (eventData.status === 'completed') {
          const url = `http://localhost:8000${eventData.result_url}`;
          setDownloadUrl(url);
          const bookTitle = eventData.book_title || file.name.replace(/\.[^/.]+$/, "");

          // Add to history
          addToHistory({
            id: jobId,
            title: bookTitle,
            date: new Date().toLocaleDateString(),
            url: url
          });

          eventSource.close();
          setIsGenerating(false);
        } else if (eventData.status === 'failed') {
          eventSource.close();
          setIsGenerating(false);
          alert(`Generation failed: ${eventData.message}`);
        }
      };

      eventSource.onerror = (err) => {
        console.error("EventSource failed:", err);
        eventSource.close();
        setIsGenerating(false);
      };

    } catch (error) {
      console.error("Error generating book:", error);
      alert("Error connecting to backend");
      setIsGenerating(false);
    }
  };

  return (
    <div className={styles.pageWrapper}>
      <header className={styles.header}>
        <h1 className={styles.title}>Islamic Children's Book Generator</h1>
        <p className={styles.subtitle}>Transform Islamic literature into engaging, fact-based stories for children.</p>
      </header>

      <div className={styles.contentWrapper}>
        <BookHistoryDrawer books={history} onDelete={handleDeleteBook} />

        <main className={styles.mainContent}>
          {/* Section 1: Upload */}
          <div className={styles.card}>
            <UploadZone onFileSelect={setFile} />
            {file && (
              <div style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--primary)' }}>
                Selected: <strong>{file.name}</strong>
              </div>
            )}
          </div>

          {/* Section 2: Segmentation */}
          {file && (
            <div className={styles.card}>
              <DocumentSegmentation
                segmentation={segmentation}
                onChange={handleSegmentationChange}
              />
            </div>
          )}

          {/* Section 3: Specs */}
          {file && (
            <div className={styles.card}>
              <BookSpecs specs={specs} onChange={handleSpecChange} />
            </div>
          )}

          {/* Section 4: Actions */}
          <div className={styles.card}>
            {/* Progress Bar Area */}
            {(isGenerating || progress > 0) && (
              <div style={{ marginBottom: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>{statusMessage}</span>
                  <span>{progress}%</span>
                </div>
                <div style={{ width: '100%', height: '10px', background: '#e0e0e0', borderRadius: '5px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${progress}%`,
                      height: '100%',
                      background: 'var(--primary)',
                      transition: 'width 0.3s ease'
                    }}
                  />
                </div>
              </div>
            )}

            <div className={styles.actions} style={{ marginTop: 0 }}>
              {!downloadUrl ? (
                <button
                  className={styles.button}
                  onClick={handleGenerate}
                  disabled={!file || isGenerating}
                >
                  {isGenerating ? 'Generating Book...' : 'Produce Children Book'}
                </button>
              ) : (
                <>
                  <a
                    href={downloadUrl}
                    download="my_islamic_book.pdf"
                    className={styles.button}
                  >
                    Download Book PDF
                  </a>
                  <button
                    className={styles.buttonSecondary}
                    onClick={handleReset}
                  >
                    Create New Book
                  </button>
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
