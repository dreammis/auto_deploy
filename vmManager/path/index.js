import "babel-polyfill";
import React, {Component} from 'react';
import {render} from "react-dom";
import {BrowserRouter as Router, Switch, Route, Redirect} from "react-router-dom";
import {Provider} from "react-redux";
import store from "Store";
import lazy from "Utils/lazy";
import BundleMainPage from "bundle-loader?lazy!Components/main-page";
import "./index.less";
import { adtion } from './utils/adtion';

/**
 * 自适应，响应式代码
 */
adtion(1024);
window.onresize = function() {
    adtion(1024);
};

//懒加载模块
const MainPage = lazy(BundleMainPage, MainPage);


class App extends Component {
    render() {
        return (
            <Provider store={store}>
                <Router>
                    <Switch>
                        <Route path="/vmManager" component={MainPage}/>
                        <Redirect from="/" to="/vmManager" />
                    </Switch>
                </Router>
            </Provider>
        );
    }
}

render(
    <App />, 
    document.getElementById("root")
);