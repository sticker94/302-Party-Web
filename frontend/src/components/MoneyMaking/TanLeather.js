import React, { useEffect, useState } from 'react';
import axios from 'axios';
import $ from 'jquery';
import 'datatables.net';
import 'datatables.net-dt/css/dataTables.dataTables.min.css';

const TanLeather = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [runeCosts, setRuneCosts] = useState({ natureRune: 0, astralRune: 0 });  // Store rune prices

    useEffect(() => {
        // Fetch rune costs for Nature and Astral runes
        const fetchRuneCosts = async () => {
            try {
                // Fetch Nature Rune Price
                const natureRuneResponse = await axios.get('http://localhost:3001/api/item_price/nature%20rune');
                const natureRunePrice = natureRuneResponse.data.price;

                // Fetch Astral Rune Price
                const astralRuneResponse = await axios.get('http://localhost:3001/api/item_price/astral%20rune');
                const astralRunePrice = astralRuneResponse.data.price;

                // Set the prices in the state
                setRuneCosts({
                    natureRune: natureRunePrice,
                    astralRune: astralRunePrice
                });
            } catch (error) {
                console.error("Error fetching rune prices", error);
            }
        };

        // Fetch Tan Leather data
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:3001/api/crafting_smithing/tan_leather');
                setData(response.data.data);
                setLoading(false);

                // Initialize DataTable after data is fetched
                setTimeout(() => {
                    if ($.fn.DataTable.isDataTable('#tanLeatherTable')) {
                        $('#tanLeatherTable').DataTable().destroy();
                    }
                    $('#tanLeatherTable').DataTable({
                        "order": [[5, "desc"]],  // Sort the 6th column (profit) in descending order
                        "columnDefs": [
                            {
                                "targets": 5,  // Target the profit column (index 5)
                                "render": function (data, type, row) {
                                    // Remove the 'gp' and '+' for sorting purposes
                                    return parseFloat(data.replace(/[^\d.-]/g, ''));
                                },
                                "type": "num"  // Force numeric sorting
                            }
                        ]
                    });
                }, 100);
            } catch (error) {
                console.error("Error fetching Tan Leather data", error);
                setLoading(false);
            }
        };

        fetchRuneCosts();  // Fetch rune prices first
        fetchData();  // Then fetch the leather data
    }, []);

    // Helper function to generate the wiki image URL
    const getWikiImageUrl = (itemName) => {
        const formattedName = itemName.replace(/\s/g, '_');
        return `https://oldschool.runescape.wiki/images/${formattedName}_detail.png`;
    };

    if (loading) {
        return <p>Loading data...</p>;
    }

    if (!data) {
        return <p>No data available</p>;
    }

    // Constants for calculations
    const hidesPerHour = 8000;
    const hidesPerSpell = 5;
    const expPerSpell = 81;
    const spellsPerHour = hidesPerHour / hidesPerSpell;
    const runeCostPerSpell = runeCosts.natureRune + (runeCosts.astralRune * 2);
    const totalRuneCostPerHour = spellsPerHour * runeCostPerSpell;

    return (
        <div>
            <h2>Tan Leather</h2>
            <table id="tanLeatherTable" className="display">
                <thead>
                <tr>
                    <th>Item</th>
                    <th>Icon</th>
                    <th>Approx. Cost (gp)</th>
                    <th>Approx. Sell Price (gp)</th>
                    <th>Tax (gp)</th>
                    <th>Approx. Profit (gp)</th>
                    <th>Buying Quantity (per hour)</th>
                    <th>Selling Quantity (per hour)</th>
                    <th>Profit w/ Tanner (per hour/gp)</th>
                    <th>Profit w/ Lunars (per hour/gp)</th>
                    <th>Exp Gained (per hour/xp)</th>
                    <th>GE Tracker</th>
                </tr>
                </thead>
                <tbody>
                {data.map((item, index) => {
                    const profitPerHide = item.cost.profit;
                    const profitWithTannerPerHour = profitPerHide * hidesPerHour;
                    const profitWithLunarsPerHour = profitWithTannerPerHour - totalRuneCostPerHour;
                    const expGainedPerHour = spellsPerHour * expPerSpell;

                    return (
                        <tr key={index}>
                            <td>
                                <a href={item.tanned.data.wikiUrl} target="_blank" rel="noopener noreferrer">
                                    {item.tanned.data.name}
                                </a>
                            </td>
                            <td>
                                <img
                                    src={getWikiImageUrl(item.tanned.data.name)}
                                    alt={item.tanned.data.name}
                                    width="30"
                                    onError={(e) => { e.target.src = item.tanned.data.icon; }}  // Fallback to original icon if the constructed one fails
                                />
                            </td>
                            <td>{item.cost.cost.toLocaleString()}</td>
                            <td>{item.tanned.data.selling.toLocaleString()}</td>
                            <td>{item.tanned.data.tax.toLocaleString()}</td>
                            <td>{profitPerHide >= 0 ? `+${profitPerHide.toLocaleString()}` : `${profitPerHide.toLocaleString()}`}</td>
                            <td>{item.tanned.data.buyingQuantity.toLocaleString()}</td>
                            <td>{item.tanned.data.sellingQuantity.toLocaleString()}</td>
                            <td>{profitWithTannerPerHour.toLocaleString()}</td>
                            <td>{profitWithLunarsPerHour.toLocaleString()}</td>
                            <td>{expGainedPerHour.toLocaleString()}</td>
                            <td>
                                <a href={item.tanned.data.url} target="_blank" rel="noopener noreferrer">
                                    View on GE Tracker
                                </a>
                            </td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </div>
    );
};

export default TanLeather;
