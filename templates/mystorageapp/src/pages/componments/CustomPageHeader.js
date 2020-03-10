import React from "react";
import { Layout, Input, Button } from 'antd';
import { Row, Col } from 'antd';
import {connect} from 'react-redux';
import * as tokenActionCreator from "../commons/store/tokanActionCreator";

const { Header, Content, Footer } = Layout;

class CustomPageHeader extends React.Component{
    constructor(props) {
        super(props);
        this.state={
            tokenValue:"",
        }
    }
    handleClearToken =()=>{
        this.props.updateToken("");
        this.setState({tokenValue:""})
    }
    handleUpdateToken =()=>{
        this.props.updateToken(this.state.tokenValue);
    }
    handleInputChange =(value)=>{
        this.setState({tokenValue:value});
    }
    render() {
        const tokenValue = this.props.token.value;
        return (
            <Row type="flex" justify="space-between" align="middle">
                <Col >
                    <h2 style={{color:"white"}}>WebStorage</h2>
                </Col>
                <Row type="flex" align="middle">
                    <Col>
                        <Input.Password placeholder="Token" value={this.state.tokenValue}
                                        onChange={(e)=>{this.handleInputChange(e.target.value)}}/>
                    </Col>
                    <Col>
                        {tokenValue!==""&&<Button type="danger" style={{marginLeft:"20px"}} onClick={()=>{this.handleClearToken()}}>Clear</Button>}
                        {tokenValue===""&&<Button type="primary" style={{marginLeft:"20px"}} onClick={()=>{this.handleUpdateToken()}}>Save</Button>}
                    </Col>
                </Row>
            </Row>
        );
    }
}

const mapStoreToProps = (store) => {
    return {
        token:store.token,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        updateToken(value){
            dispatch(tokenActionCreator.updateToken(value));
        },
    }
}

export default connect(mapStoreToProps,mapDispatchToProps)(CustomPageHeader)

