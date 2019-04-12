import {connect} from "react-redux";
import {withRouter} from "react-router-dom";
import Home from "Components/public/home";
import {fetch_username} from "Action";

const mapStateToProps = (state) => ({username: state.home.username,menu:state.home.menu});

const mapDispatchToProps = (dispatch) => ({
    fetch_username : (username) => dispatch(fetch_username(username))
});

export default connect(mapStateToProps, mapDispatchToProps)(Home);
