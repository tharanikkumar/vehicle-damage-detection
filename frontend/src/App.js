import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/upload', formData);
            setResult(response.data);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    };

    return (
        <div className="container">
            <h1>Vehicle Damage Detection</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
            {result && (
                <div>
                    <h3>Damage Report</h3>
                    <p>Damage: {JSON.stringify(result.damage)}</p>
                    <p>Estimated Cost: ${result.cost}</p>
                </div>
            )}
        </div>
    );
}

export default App;
