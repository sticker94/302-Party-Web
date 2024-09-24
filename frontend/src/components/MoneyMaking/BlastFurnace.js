import React, { useEffect, useState } from 'react';
import axios from 'axios';

const BlastFurnace = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get('http://localhost:3001/api/crafting_smithing/blast_furnace')
            .then((response) => {
                setData(response.data);
            })
            .catch((error) => {
                console.error("Error fetching Blast Furnace data", error);
            });
    }, []);

    return (
        <div>
            <h2>Blast Furnace</h2>
            {data ? (
                <ul>
                    {data.items.map((item, index) => (
                        <li key={index}>{item.name}: {item.profit} gp</li>
                    ))}
                </ul>
            ) : (
                <p>Loading data...</p>
            )}
        </div>
    );
};

export default BlastFurnace;
