import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ItemPriceFetcher = ({ itemName }) => {
    const [itemPrice, setItemPrice] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchItemPrice = async () => {
            try {
                const response = await axios.get(`http://localhost:3001/api/item_price/${itemName}`);
                setItemPrice(response.data.price);
                setLoading(false);
            } catch (error) {
                console.error(`Error fetching price for ${itemName}`, error);
                setLoading(false);
            }
        };

        if (itemName) {
            fetchItemPrice();
        }
    }, [itemName]);

    if (loading) {
        return <p>Loading {itemName} price...</p>;
    }

    return (
        <div>
            <h3>{itemName}</h3>
            {itemPrice ? <p>Price: {itemPrice.toLocaleString()} gp</p> : <p>Price not available</p>}
        </div>
    );
};

export default ItemPriceFetcher;
