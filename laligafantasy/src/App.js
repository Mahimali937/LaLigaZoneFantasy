import React, { useEffect } from 'react';
import './App.scss';
import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Home from './components/Home/Home';
import Teams from './components/Teams/Teams';
import TeamData from './components/TeamData/TeamData';
import Nations from './components/Nations/Nations';
import Positions from './components/Positions/Positions';
import Search from './components/Search/Search';

function App() {
  useEffect(() => {
    document.title = 'LaLigaZone Fantasy';
  }, []);

  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="teams" element={<Teams />} />
          <Route path="data" element={<TeamData />} />
          <Route path="nations" element={<Nations />} />
          <Route path="positions" element={<Positions />} />
          <Route path="search" element={<Search />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;