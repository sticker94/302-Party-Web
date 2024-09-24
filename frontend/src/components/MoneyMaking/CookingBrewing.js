import React, { useEffect, useState } from 'react';
import axios from 'axios';

const CookingBrewing = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get('http://localhost:3001/api/crafting_smithing/cooking_brewing')
            .then((response) => {
                setData(response.data);
            })
            .catch((error) => {
                console.error("Error fetching Cooking/Brewing data", error);
            });
    }, []);

    return (
        <div>
            <h2>Cooking/Brewing</h2>
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

export default CookingBrewing;
