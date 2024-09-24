import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import Points from './components/Points';
import CraftingSmithing from './components/MoneyMaking/CraftingSmithing';

function App() {
    return (
        <Router>
            <div>
                {/* Navigation Menu */}
                <nav>
                    <ul>
                        <li><Link to="/points">Points</Link></li>
                        <li><Link to="/money-making/crafting-smithing">Crafting & Smithing</Link></li>
                        {/* Add more links for other sections as needed */}
                    </ul>
                </nav>

                {/* Define Routes */}
                <Routes>
                    {/* Default route - Redirect / to /points */}
                    <Route path="/" element={<Navigate to="/points" />} />

                    {/* Points Page */}
                    <Route path="/points" element={<Points />} />

                    {/* Crafting & Smithing Routes */}
                    <Route path="/money-making/crafting-smithing/*" element={<CraftingSmithing />} />

                    {/* Add other routes here */}
                </Routes>
            </div>
        </Router>
    );
}

export default App;
