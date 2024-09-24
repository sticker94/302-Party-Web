import React from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import BlastFurnace from './BlastFurnace';
import CookingBrewing from './CookingBrewing';
import TanLeather from './TanLeather';

const CraftingSmithing = () => {
    return (
        <div>
            <h1>Crafting & Smithing</h1>
            <nav>
                <ul>
                    <li><Link to="/money-making/crafting-smithing/blast-furnace">Blast Furnace</Link></li>
                    <li><Link to="/money-making/crafting-smithing/cooking-brewing">Cooking/Brewing</Link></li>
                    <li><Link to="/money-making/crafting-smithing/tan-leather">Tan Leather</Link></li>
                </ul>
            </nav>

            <Routes>
                <Route path="blast-furnace" element={<BlastFurnace />} />
                <Route path="cooking-brewing" element={<CookingBrewing />} />
                <Route path="tan-leather" element={<TanLeather />} />
            </Routes>
        </div>
    );
};

export default CraftingSmithing;
