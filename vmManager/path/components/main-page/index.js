import React, {Component} from 'react';
import {BrowserRouter as Router, Switch, Route, Redirect} from "react-router-dom";
import BundleHome from "bundle-loader?lazy!Contairs/home";
import lazy from "Utils/lazy";

//懒加载模块
const Home = lazy(BundleHome, Home);

class MainPage extends Component {
    render() {
        let {match} = this.props;
        return (
            <div className="mainPage">
                <Switch>
                    <Route exact path={`${match.url}`} component={Home}/>
                </Switch>
            </div>
        );
    }
}

export default MainPage;