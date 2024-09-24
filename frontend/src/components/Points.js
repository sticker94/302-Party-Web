import React, { useEffect, useState, useCallback } from 'react';
import $ from 'jquery';
import 'datatables.net';
import 'datatables.net-dt/css/dataTables.dataTables.min.css';
import axios from 'axios';

const Points = () => {
    const [members, setMembers] = useState([]);
    const [ranks, setRanks] = useState([]);
    const [search, setSearch] = useState('');
    const [filterRank, setFilterRank] = useState('');
    const [loading, setLoading] = useState(true);

    const fetchMembers = useCallback(async () => {
        try {
            const response = await axios.get('http://localhost:3001/api/members', {
                params: {
                    search: search,
                    rank: filterRank,
                },
            });
            setMembers(response.data.members);
            setRanks(response.data.ranks);
            setLoading(false);

            // Initialize DataTable after data is fetched
            $('#membersTable').DataTable();
        } catch (error) {
            console.error('Error fetching members:', error);
        }
    }, [search, filterRank]);

    useEffect(() => {
        fetchMembers();
    }, [fetchMembers]);

    const handleSearch = (e) => {
        e.preventDefault();
        fetchMembers();
    };

    return (
        <div className="container mt-5">
            <h1>Welcome to 302 Party</h1>
            <form onSubmit={handleSearch} className="mb-4">
                <div className="input-group">
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="form-control"
                        placeholder="Search by name"
                    />
                    <select
                        name="rank"
                        className="form-select"
                        value={filterRank}
                        onChange={(e) => setFilterRank(e.target.value)}
                    >
                        <option value="">All Ranks</option>
                        {ranks.map((rank, index) => (
                            <option key={index} value={rank.rank}>{rank.rank}</option>
                        ))}
                    </select>
                    <button type="submit" className="btn btn-outline-primary">Apply</button>
                </div>
            </form>

            {!loading && (
                <table id="membersTable" className="display">
                    <thead>
                    <tr>
                        <th>Username</th>
                        <th>Rank</th>
                        <th>Points</th>
                        <th>Assign Points</th>
                    </tr>
                    </thead>
                    <tbody>
                    {members.map((member) => (
                        <tr key={member.id}>
                            <td>{member.username}</td>
                            <td>{member.rank}</td>
                            <td>{member.points}</td>
                            <td>
                                <input
                                    type="number"
                                    placeholder="Points"
                                    className="form-control"
                                    onChange={() => {}}
                                />
                                <button className="btn btn-sm btn-outline-success">Assign</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default Points;
