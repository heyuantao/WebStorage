import React from 'react';
import { Provider } from "react-redux";
import store from "./store"

import MainPage from "./pages/mainpage";

import './App.css';
import 'antd/dist/antd.css';


function App() {
    return (
        <div>
            <Provider store={store}>
                <MainPage></MainPage>
            </Provider>
        </div>
    );
}

export default App;
