import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null, copied: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught an error", error, info);
    this.setState({ info });

    // Auto-reload on chunk load failure after a new build deployment
    const msg = String(error?.message || '');
    const isChunkError =
      msg.includes('dynamically imported module') ||
      msg.includes('Failed to fetch') ||
      msg.includes('Loading chunk') ||
      msg.includes('Importing a module script failed') ||
      error?.name === 'ChunkLoadError';

    if (isChunkError) {
      try {
        const lastRetry = sessionStorage.getItem('crs_chunk_retry');
        const now = Date.now();
        if (!lastRetry || now - parseInt(lastRetry, 10) > 15000) {
          sessionStorage.setItem('crs_chunk_retry', String(now));
          if ('caches' in window) {
            caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))).then(() => {
              window.location.reload();
            });
          } else {
            window.location.reload();
          }
        }
      } catch (e) {
        window.location.reload();
      }
    }
  }

  handleReload = () => {
    try {
      if ('caches' in window) {
        caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))).then(() => {
          window.location.reload();
        });
      } else {
        window.location.reload();
      }
    } catch (e) {
      window.location.reload();
    }
  };

  handleGoHome = () => {
    try {
      if ('caches' in window) {
        caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))).finally(() => {
          window.location.href = '/';
        });
      } else {
        window.location.href = '/';
      }
    } catch (e) {
      window.location.href = '/';
    }
  };

  handleCopy = () => {
    const errorDetails = `${this.state.error?.toString() || 'Unknown Error'}\n\nStack:\n${this.state.info?.componentStack || this.state.error?.stack || 'No stack trace'}`;
    navigator.clipboard.writeText(errorDetails).then(() => {
      this.setState({ copied: true });
      setTimeout(() => this.setState({ copied: false }), 2000);
    }).catch(() => {});
  };

  render() {
    if (this.state.hasError) {
      const errorText = this.state.error?.toString() || 'An unexpected error occurred';
      const stackText = this.state.info?.componentStack || this.state.error?.stack || '';

      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f8fafc',
          padding: '16px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          color: '#1e293b'
        }}>
          <div style={{
            maxWidth: '640px',
            width: '100%',
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
            border: '1px solid #fee2e2',
            padding: '24px',
            boxSizing: 'border-box'
          }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#fee2e2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#dc2626',
                flexShrink: 0
              }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <div>
                <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', margin: 0, lineHeight: 1.2 }}>
                  Something went wrong
                </h2>
                <p style={{ fontSize: '13px', color: '#64748b', margin: '4px 0 0 0' }}>
                  A new app version may have deployed, or a temporary issue occurred.
                </p>
              </div>
            </div>

            {/* Error Message Box */}
            <div style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              color: '#991b1b',
              fontSize: '13px',
              fontWeight: '600',
              wordBreak: 'break-word',
              lineHeight: 1.4
            }}>
              {errorText}
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
              <button
                onClick={this.handleReload}
                style={{
                  backgroundColor: '#1B3A6B',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 18px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
                </svg>
                Reload App
              </button>

              <button
                onClick={this.handleGoHome}
                style={{
                  backgroundColor: '#ffffff',
                  color: '#334155',
                  border: '1px solid #cbd5e1',
                  borderRadius: '8px',
                  padding: '10px 18px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Go to Dashboard
              </button>

              <button
                onClick={this.handleCopy}
                style={{
                  backgroundColor: '#f1f5f9',
                  color: '#475569',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  marginLeft: 'auto'
                }}
              >
                {this.state.copied ? '✓ Copied' : 'Copy Details'}
              </button>
            </div>

            {/* Stack Details (Open by Default) */}
            <details open style={{
              fontSize: '12px',
              color: '#475569',
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '10px 12px'
            }}>
              <summary style={{ fontWeight: '600', cursor: 'pointer', color: '#334155', marginBottom: '8px' }}>
                Technical Details
              </summary>
              <pre style={{
                margin: 0,
                padding: '8px',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
                maxHeight: '180px',
                overflowY: 'auto',
                fontFamily: 'monospace',
                fontSize: '11px',
                color: '#64748b'
              }}>
                {stackText || 'No additional stack details available.'}
              </pre>
            </details>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
