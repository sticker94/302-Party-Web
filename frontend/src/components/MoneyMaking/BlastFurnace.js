import React, { useEffect, useState } from 'react';
import axios from 'axios';
import $ from 'jquery';
import 'datatables.net';
import 'datatables.net-dt/css/dataTables.dataTables.min.css';

const BlastFurnace = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [staminaCost, setStaminaCost] = useState(0);
    const [includeStamina, setIncludeStamina] = useState(true);  // Toggle stamina cost inclusion
    const [xpOption, setXpOption] = useState("default"); // To handle different XP calculations

    const xpPerHourMapping = {
        'Bronze bar': { default: [2900, 3400], xp: 6.2 },
        'Iron bar': { default: [5800, 6850], xp: 12.5 },
        'Silver bar': { default: [5800, 6850], xp: 13.6 },
        'Steel bar': { default: [2900, 3400], coalBag: [4650, 5450], xp: 17.5 },
        'Gold bar': { default: [5800, 6850], gauntlets: [5600, 6600], cape: [5800, 6850], xp: 22.5, gauntletsXp: 56.2 },
        'Mithril bar': { default: [1900, 2250], coalBag: [3150, 3700], xp: 30 },
        'Adamantite bar': { default: [1450, 1700], coalBag: [2400, 2800], xp: 37.5 },
        'Runite bar': { default: [1150, 1350], coalBag: [1900, 2250], xp: 50 },
    };

    // Helper function to get the proper wiki image URL
    const getWikiImageUrl = (itemName) => {
        const formattedName = itemName.replace(/\s/g, '_');
        return `https://oldschool.runescape.wiki/images/${formattedName}_detail.png`;
    };

    useEffect(() => {
        // Fetch Stamina Potion cost
        const fetchStaminaCost = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/item_price/Stamina%20Potion(4)`);
                setStaminaCost(response.data.price * 9);  // 9 potions per hour
            } catch (error) {
                console.error('Error fetching stamina potion cost:', error);
            }
        };

        // Fetch Blast Furnace data
        const fetchData = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/crafting_smithing/blast_furnace`);
                setData(response.data.data);
                setLoading(false);

                // Initialize DataTable after data is fetched
                setTimeout(() => {
                    if ($.fn.DataTable.isDataTable('#blastFurnaceTable')) {
                        $('#blastFurnaceTable').DataTable().destroy();
                    }
                    $('#blastFurnaceTable').DataTable({
                        "order": [[9, "desc"]],  // Sort by "Profit per hour"
                        "columnDefs": [
                            {
                                "targets": [1, 2, 3, 4, 5, 6, 7, 8, 9],  // Target numeric columns for sorting
                                "render": function (data, type, row) {
                                    return type === 'display' ? data.toLocaleString() : data;  // Format with commas for display, but keep as number for sorting
                                },
                                "type": "num"  // Ensure numeric sorting
                            }
                        ]
                    });
                }, 100);
            } catch (error) {
                console.error("Error fetching Blast Furnace data", error);
                setLoading(false);
            }
        };

        fetchStaminaCost();  // Fetch the stamina cost
        fetchData();  // Fetch the Blast Furnace data
    }, [xpOption]);

    if (loading) {
        return <p>Loading data...</p>;
    }

    if (!data) {
        return <p>No data available</p>;
    }

    // Helper function to calculate profit per hour
    const calculateProfitPerHour = (profit, barsPerHour) => {
        let profitPerHour = profit * barsPerHour;
        if (includeStamina) {
            profitPerHour -= staminaCost;
        }
        return profitPerHour;
    };

    // Helper function to calculate XP per hour
    const calculateXpPerHour = (itemName, barsPerHour) => {
        const itemXpData = xpPerHourMapping[itemName];
        if (!itemXpData) return 0;

        const { xp, gauntletsXp } = itemXpData;
        let barsRange = itemXpData.default;
        let xpValue = xp;

        // Handle Gold bar special cases
        if (itemName === 'Gold bar') {
            if (xpOption === 'gauntlets') {
                barsRange = itemXpData.gauntlets;
                xpValue = gauntletsXp;
            } else if (xpOption === 'cape') {
                barsRange = itemXpData.cape;
                xpValue = gauntletsXp;  // same XP for gold bars with cape
            }
        } else if (itemXpData[xpOption]) {
            barsRange = itemXpData[xpOption];
        }

        const averageBars = (barsRange[0] + barsRange[1]) / 2;
        return Math.round(averageBars * xpValue);
    };

    return (
        <div>
            <h2>Blast Furnace</h2>
            <label>
                Include stamina cost:
                <input
                    type="checkbox"
                    checked={includeStamina}
                    onChange={(e) => setIncludeStamina(e.target.checked)}
                />
            </label>
            <label>
                XP Calculation:
                <select onChange={(e) => setXpOption(e.target.value)} value={xpOption}>
                    <option value="default">Default</option>
                    <option value="gauntlets">Goldsmith Gauntlets</option>
                    <option value="cape">Smithing Cape</option>
                    <option value="coalBag">Coal Bag</option>
                </select>
            </label>
            <table id="blastFurnaceTable" className="display">
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
                    <th>Bars per hour</th>
                    <th>Profit per hour (gp)</th>
                    <th>XP per hour</th>
                </tr>
                </thead>
                <tbody>
                {data.map((item, index) => {
                    // Safely access data and default to 0 if undefined
                    const cost = item?.cost?.cost ?? 0;
                    const selling = item?.target?.item?.data?.selling ?? 0;
                    const tax = item?.cost?.tax ?? 0;
                    const profit = item?.cost?.profit ?? 0;
                    const barsPerHour = item?.target?.perHr ?? 0;
                    const buyingQuantity = item?.target?.item?.data?.buyingQuantity ?? 0;
                    const sellingQuantity = item?.target?.item?.data?.sellingQuantity ?? 0;
                    const itemName = item?.target?.item?.data?.name;

                    return (
                        <tr key={index}>
                            <td>
                                <a href={item.target.item.data.wikiUrl} target="_blank" rel="noopener noreferrer">
                                    {itemName}
                                </a>
                            </td>
                            <td>
                                <img
                                    src={getWikiImageUrl(itemName)}
                                    alt={itemName}
                                    width="30"
                                    onError={(e) => { e.target.src = item.target.item.data.icon; }}
                                />
                            </td>
                            <td>{cost}</td>
                            <td>{selling}</td>
                            <td>{tax}</td>
                            <td>{profit}</td>
                            <td>{buyingQuantity}</td>
                            <td>{sellingQuantity}</td>
                            <td>{barsPerHour}</td>
                            <td>{calculateProfitPerHour(profit, barsPerHour)}</td>
                            <td>{calculateXpPerHour(itemName, barsPerHour)}</td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </div>
    );
};

export default BlastFurnace;
