import { useState } from 'react';
import api from '../services/api';
import NavBar from '../components/NavBar';

function ImportCSV() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setReport(null);
    if (!file) {
      setError('Please choose a CSV file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await api.post('/imports/run/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setReport(response.data);
    } catch (uploadError) {
      setError(uploadError.response?.data?.detail || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <NavBar />
      <div style={{ padding: 24 }}>
        <h1>CSV Import</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            accept=".csv"
            onChange={(event) => setFile(event.target.files[0])}
          />
          <br />
          <button type="submit" disabled={loading} style={{ marginTop: 12 }}>
            {loading ? 'Importing...' : 'Upload CSV'}
          </button>
        </form>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        {report && (
          <div style={{ marginTop: 24 }}>
            <h2>Import summary</h2>
            <p>Imported file: {report.batch.file_name}</p>
            <p>Created expenses: {report.summary.created.expenses}</p>
            <p>Created settlements: {report.summary.created.settlements}</p>
            <p>Skipped rows: {report.summary.created.skipped}</p>
            <h3>Anomalies</h3>
            {report.summary.issues.length === 0 ? (
              <p>No anomalies detected.</p>
            ) : (
              <ul>
                {report.summary.issues.map((issue) => (
                  <li key={`${issue.row_number}-${issue.issue_type}`}>
                    Row {issue.row_number}: {issue.issue_type} — {issue.description} <strong>Action:</strong> {issue.action_taken}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ImportCSV;
