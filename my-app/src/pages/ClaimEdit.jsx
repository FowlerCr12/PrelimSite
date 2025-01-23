// In a React component
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ClaimsTable() {
    const [claims, setClaims] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/claims')
            .then(res => {
                setClaims(res.data);
            })
            .catch(err => {
                console.error(err);
            });
    }, []);

    return (
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Claim Name</th>
                    <th>Status</th>
                    <th>Download Doc</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {claims.map(claim => (
                    <tr key={claim.id}>
                        <td>{claim.id}</td>
                        <td>{claim.claim_name}</td>
                        <td>{claim.status}</td>
                        <td>
                            {claim.docx_file_path ?
                                <a href={`http://your-domain-or-s3/${claim.docx_file_path}`} download>Download</a>
                                : 'No doc yet'}
                        </td>
                        <td>
                            {/* e.g. an "Edit" button that opens a form or calls regenerate */}
                            <button onClick={() => handleEdit(claim.id)}>Edit</button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default ClaimsTable;
