import React from 'react';
import logo from './logo.svg';
import './App.css';
import 'antd/dist/antd.css';
import MainPage from "./pages/MainPage";

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <MainPage></MainPage>
            </header>
        </div>
    );
}

export default App;
